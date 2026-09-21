import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { Telemetry } from "@/lib/db/models/Telemetry";

export async function GET(req: NextRequest) {
  try {
    await connectToDatabase();

    const { searchParams } = new URL(req.url);
    const limitParam = searchParams.get("limit");
    const zoneParam = searchParams.get("zone") || searchParams.get("zoneId");

    const limit = limitParam ? Math.min(Math.max(parseInt(limitParam, 10) || 10, 1), 100) : 12;

    const query: Record<string, any> = {};
    if (zoneParam) {
      const zUpper = zoneParam.toUpperCase();
      if (zUpper === "ZONE_A" || zUpper === "A" || zUpper.includes("FIELD_A") || zUpper.includes("TOMATO")) {
        query.zoneId = { $in: ["ZONE_A", "Tomato Field A", "NODE_01", "SLAVE_01"] };
      } else if (zUpper === "ZONE_B" || zUpper === "B" || zUpper.includes("FIELD_B") || zUpper.includes("GREENHOUSE")) {
        query.zoneId = { $in: ["ZONE_B", "Greenhouse B", "NODE_02"] };
      } else {
        query.zoneId = zoneParam;
      }
    }

    let records = await Telemetry.find(query)
      .sort({ recordedAt: -1 })
      .limit(limit)
      .lean();

    if (records.length === 0) {
      records = await Telemetry.find({})
        .sort({ recordedAt: -1 })
        .limit(limit)
        .lean();
    }

    return NextResponse.json({
      success: true,
      count: records.length,
      limit,
      latest: records[0] || null,
      history: records,
      data: records,
    });
  } catch (error: any) {
    console.error("Failed to fetch telemetry records:", error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Failed to retrieve telemetry records",
      },
      { status: 500 }
    );
  }
}

// EDGE STATION: Sync worker pushes batches of telemetry from SQLite to Cloud MongoDB
export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get("x-edge-sync-key");
    const expectedKey = process.env.EDGE_SYNC_API_KEY || "agrismart-secret-edge-key-2026";
    if (authHeader && authHeader !== expectedKey && process.env.NODE_ENV === "production") {
      return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
    }

    const body = await req.json();
    const records = Array.isArray(body) ? body : [body];

    if (records.length === 0) {
      return NextResponse.json({ success: true, count: 0, message: "No records to insert" });
    }

    try {
      await connectToDatabase();
      const docs = records.map((r: any) => ({
        zoneId: r.zoneId || "ZONE_A",
        nodeId: r.nodeId || "EDGE_STATION",
        recordedAt: r.recordedAt ? new Date(r.recordedAt) : new Date(),
        telemetry: r.telemetry || {},
        actuatorState: r.actuatorState || {},
        alerts: r.alerts || [],
      }));

      await Telemetry.insertMany(docs, { ordered: false });
    } catch (dbErr: any) {
      console.warn("Telemetry DB write error:", dbErr.message);
    }

    return NextResponse.json({
      success: true,
      count: records.length,
      syncedAt: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error("Telemetry POST error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to ingest telemetry" },
      { status: 500 }
    );
  }
}
