import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { AIDetection } from "@/lib/db/models/AIDetection";

export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get("x-edge-sync-key");
    if (authHeader !== process.env.EDGE_SYNC_API_KEY) {
      return NextResponse.json({ success: false, error: "Unauthorized sync request" }, { status: 401 });
    }

    const body = await req.json();
    const detections = Array.isArray(body) ? body : [body];

    if (detections.length === 0) {
      return NextResponse.json({ success: false, error: "Empty payload" }, { status: 400 });
    }

    await connectToDatabase();

    // Prepare batch upsert operations for AI detections
    const bulkOps = detections.map((item) => ({
      updateOne: {
        filter: {
          nodeId: item.nodeId,
          modelName: item.modelName,
          recordedAt: new Date(item.recordedAt),
        },
        update: {
          $set: {
            detectionLabel: item.detectionLabel,
            confidence: item.confidence,
            imagePath: item.imagePath,
            metadata: item.metadata || {},
            syncedAt: new Date(),
          },
        },
        upsert: true,
      },
    }));

    const result = await AIDetection.bulkWrite(bulkOps);

    return NextResponse.json({
      success: true,
      syncedCount: result.upsertedCount + result.modifiedCount,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error("AI sync error:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to process AI detections sync" },
      { status: 500 }
    );
  }
}
