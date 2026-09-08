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
