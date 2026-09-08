import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { AIDetection } from "@/lib/db/models/AIDetection";

export async function GET(req: NextRequest) {
  try {
    await connectToDatabase();

    const { searchParams } = new URL(req.url);
    const nodeId = searchParams.get("nodeId");
    const limit = parseInt(searchParams.get("limit") || "20", 10);

    const filter: Record<string, any> = {};
    if (nodeId) {
      const nUpper = nodeId.toUpperCase();
      if (nUpper === "NODE_01" || nUpper === "ZONE_A" || nUpper === "FIELD_A") {
        filter.nodeId = { $in: ["NODE_01", "ZONE_A", "PHONE_ZONE_A", "ROVER_PHONE_01", "ROVER_MANUAL_CAM", "EDGE_STATION_PI"] };
      } else if (nUpper === "NODE_02" || nUpper === "ZONE_B" || nUpper === "FIELD_B") {
        filter.nodeId = { $in: ["NODE_02", "ZONE_B", "PHONE_ZONE_B", "SLAVE_01"] };
      } else {
        filter.nodeId = nodeId;
      }
    }

    let detections = await AIDetection.find(filter)
      .sort({ recordedAt: -1 })
      .limit(limit)
      .lean();

    // If no detections found for specific node/zone, fallback to latest overall farm detections
    if (detections.length === 0) {
      detections = await AIDetection.find({})
        .sort({ recordedAt: -1 })
        .limit(limit)
        .lean();
    }

    // Group latest detection per model
    const latestPerModel: Record<string, any> = {
      disease: null,
      pest: null,
      nutrition: null,
      stage: null,
    };

    for (const d of detections) {
      if (!latestPerModel[d.modelName]) {
        latestPerModel[d.modelName] = d;
      }
    }

    return NextResponse.json({
      success: true,
      summary: latestPerModel,
      models: latestPerModel,
      history: detections,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error("Fetch AI latest error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to fetch latest AI diagnostics" },
      { status: 500 }
    );
  }
}
