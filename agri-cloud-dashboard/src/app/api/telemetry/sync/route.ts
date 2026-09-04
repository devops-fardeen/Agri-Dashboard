import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { Telemetry } from "@/lib/db/models/Telemetry";

export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get("x-edge-sync-key");
    if (authHeader !== process.env.EDGE_SYNC_API_KEY) {
      return NextResponse.json({ success: false, error: "Unauthorized sync request" }, { status: 401 });
    }

    const body = await req.json();
    const readings = Array.isArray(body) ? body : [body];

    if (readings.length === 0) {
      return NextResponse.json({ success: false, error: "Empty payload" }, { status: 400 });
    }

    await connectToDatabase();

    // Prepare batch operations
    const bulkOps = readings.map((item) => ({
      updateOne: {
        filter: {
          zoneId: item.zoneId,
          recordedAt: new Date(item.recordedAt),
        },
        update: {
          $set: {
            nodeId: item.nodeId,
            telemetry: item.telemetry,
            actuatorState: item.actuatorState,
            alerts: item.alerts || [],
            syncedAt: new Date(),
          },
        },
        upsert: true,
      },
    }));

    const result = await Telemetry.bulkWrite(bulkOps);

    return NextResponse.json({
      success: true,
      syncedCount: result.upsertedCount + result.modifiedCount,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error("Telemetry sync error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to process telemetry sync" },
      { status: 500 }
    );
  }
}