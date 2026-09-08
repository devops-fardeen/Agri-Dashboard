import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/db/connect";
import { DeviceCommand } from "@/lib/db/models/DeviceCommand";

// DASHBOARD: Post new pump or rover action
export async function POST(req: NextRequest) {
  try {
    const { target, action, rover_ip } = await req.json();
    const roverIp = rover_ip || "10.84.122.196";

    // 1. Direct relay to local Edge Station on port 8000 if running locally
    try {
      if (target === "PUMP_ZONE_A" || target === "PUMP_ZONE_B") {
        await fetch(`http://127.0.0.1:8000/api/edge/pump/${target}/${action}`, {
          method: "POST",
          signal: AbortSignal.timeout(1000),
        }).catch(() => {});
      } else if (target === "ROVER") {
        const cmdMap: Record<string, string> = {
          MOVE_FORWARD: "forward",
          FORWARD: "forward",
          MOVE_BACKWARD: "backward",
          BACKWARD: "backward",
          MOVE_LEFT: "left",
          LEFT: "left",
          MOVE_RIGHT: "right",
          RIGHT: "right",
          STOP: "stop",
          AUTO_ON: "auto_on",
          AUTO_OFF: "auto_off",
        };
        const moveCmd = cmdMap[action] || "stop";
        // Direct Rover ESP32 Web Server dispatch
        fetch(`http://${roverIp}/cmd?move=${moveCmd}`, { signal: AbortSignal.timeout(1200) }).catch(() => {});

        // Local Edge Gateway dispatch
        await fetch(`http://127.0.0.1:8000/api/edge/rover/command`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action, rover_ip: roverIp }),
          signal: AbortSignal.timeout(1000),
        }).catch(() => {});
      }
    } catch {
      // Local relay skipped if station offline
    }

    // 2. Persist command to MongoDB for cloud-to-edge worker synchronization
    let command = null;
    try {
      await connectToDatabase();
      command = await DeviceCommand.create({
        target,
        action,
        status: "PENDING",
      });
    } catch (dbErr: any) {
      console.warn("MongoDB offline, command dispatched to local hardware:", dbErr.message);
    }

    return NextResponse.json({ success: true, command, target, action });
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