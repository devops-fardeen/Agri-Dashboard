import mongoose, { Schema, Document, Model } from "mongoose";

export interface IDeviceCommand extends Document {
  target: "PUMP_ZONE_A" | "PUMP_ZONE_B" | "ROVER";
  action: "ON" | "OFF" | "MOVE_FORWARD" | "MOVE_BACKWARD" | "MOVE_LEFT" | "MOVE_RIGHT" | "STOP";
  parameters?: Record<string, any>;
  status: "PENDING" | "EXECUTED" | "FAILED";
  issuedBy: string;
  createdAt: Date;
  executedAt?: Date;
}

const DeviceCommandSchema = new Schema<IDeviceCommand>(
  {
    target: { type: String, required: true },
    action: { type: String, required: true },
    parameters: { type: Schema.Types.Mixed, default: {} },
    status: { type: String, enum: ["PENDING", "EXECUTED", "FAILED"], default: "PENDING", index: true },
    issuedBy: { type: String, default: "FARM_OPERATOR" },
  },
  { timestamps: true }
);

export const DeviceCommand: Model<IDeviceCommand> =
  mongoose.models.DeviceCommand || mongoose.model<IDeviceCommand>("DeviceCommand", DeviceCommandSchema);