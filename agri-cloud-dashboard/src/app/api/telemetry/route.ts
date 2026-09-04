import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { Telemetry } from "@/lib/db/models/Telemetry";

export async function GET(req: NextRequest) {
  try {
    await connectToDatabase();

    const { searchParams } = new URL(req.url);
    const limitParam = searchParams.get("limit");
    const zoneId = searchParams.get("zoneId");

    const limit = limitParam ? Math.min(Math.max(parseInt(limitParam, 10) || 10, 1), 100) : 10;

    const query: Record<string, any> = {};
    if (zoneId && (zoneId === "ZONE_A" || zoneId === "ZONE_B")) {
      query.zoneId = zoneId;
    }

    const records = await Telemetry.find(query)
      .sort({ recordedAt: -1 })
      .limit(limit)
      .lean();

    return NextResponse.json({
      success: true,
      count: records.length,
      limit,
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
