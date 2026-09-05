import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { DeviceCommand } from "@/lib/db/models/DeviceCommand";

// DASHBOARD: Post new pump or rover action
export async function POST(req: NextRequest) {
  try {
    const { target, action } = await req.json();
    await connectToDatabase();

    const command = await DeviceCommand.create({
      target,
      action,
      status: "PENDING",
    });

    return NextResponse.json({ success: true, command });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

// RASPBERRY PI: Fetch pending commands to execute on edge hardware
export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("x-edge-sync-key");
    if (authHeader !== process.env.EDGE_SYNC_API_KEY) {
      return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
    }

    await connectToDatabase();
    const pendingCommands = await DeviceCommand.find({ status: "PENDING" }).sort({ createdAt: 1 }).limit(10);

    return NextResponse.json({ success: true, commands: pendingCommands });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

// RASPBERRY PI: Acknowledge command execution status
export async function PATCH(req: NextRequest) {
  try {
    const authHeader = req.headers.get("x-edge-sync-key");
    if (authHeader !== process.env.EDGE_SYNC_API_KEY) {
      return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
    }

    const body = await req.json();
    await connectToDatabase();

    if (body.id) {
      const updated = await DeviceCommand.findByIdAndUpdate(
        body.id,
        {
          status: body.status || "EXECUTED",
          executedAt: new Date(),
        },
        { returnDocument: "after" }
      );
      return NextResponse.json({ success: true, updatedCommand: updated });
    } else if (Array.isArray(body.ids)) {
      const res = await DeviceCommand.updateMany(
        { _id: { $in: body.ids } },
        {
          $set: {
            status: body.status || "EXECUTED",
            executedAt: new Date(),
          },
        }
      );
      return NextResponse.json({ success: true, updatedCount: res.modifiedCount });
    }

    return NextResponse.json({ success: false, error: "Missing command id or ids" }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}