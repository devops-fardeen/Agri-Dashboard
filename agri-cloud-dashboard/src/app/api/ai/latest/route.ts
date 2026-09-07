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
      filter.nodeId = nodeId;
    }

    const detections = await AIDetection.find(filter)
      .sort({ recordedAt: -1 })
      .limit(limit)
      .lean();

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
