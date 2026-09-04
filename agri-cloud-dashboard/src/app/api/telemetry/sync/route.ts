import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ready",
    message: "Chapter 2: Ingestion endpoint ready for database connection.",
    timestamp: new Date().toISOString(),
  });
}

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    return NextResponse.json({
      status: "received",
      data: payload,
      syncedAt: new Date().toISOString(),
    });
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON payload" },
      { status: 400 }
    );
  }
}
