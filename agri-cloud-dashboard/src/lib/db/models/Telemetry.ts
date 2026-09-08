import mongoose, { Schema, Document, Model } from "mongoose";

export interface ITelemetryDocument extends Document {
  zoneId: "ZONE_A" | "ZONE_B";
  nodeId: string;
  telemetry: {
    soilMoisture: number;    // %
    soilTemperature: number; // °C
    ambientTemp: number;     // °C
    ambientHumidity: number; // %
    lightLux?: number;       // Lux
    barometricPressure?: number; // hPa
    rainDetected?: boolean;  // Master Node Pin 27 Rain Sensor
    rainIntensity?: number;  // 0 - 100%
    rainStatus?: "NO_RAIN" | "LIGHT_RAIN" | "HEAVY_RAIN";
  };
  actuatorState: {
    pumpActive: boolean;
    lastIrrigationDurationSec?: number;
    triggerSource?: "MANUAL" | "AUTO_RULE" | "AI_RECOMMENDATION";
  };
  alerts: Array<{
    type: string;
    severity: "low" | "warning" | "critical";
    message: string;
  }>;
  recordedAt: Date;
  syncedAt: Date;
}

const TelemetrySchema = new Schema<ITelemetryDocument>(
  {
    zoneId: { type: String, required: true, enum: ["ZONE_A", "ZONE_B"], index: true },
    nodeId: { type: String, required: true },
    telemetry: {
      soilMoisture: { type: Number, required: true },
      soilTemperature: { type: Number, required: true },
      ambientTemp: { type: Number, required: true },
      ambientHumidity: { type: Number, required: true },
      lightLux: { type: Number },
      barometricPressure: { type: Number },
      rainDetected: { type: Boolean, default: false },
      rainIntensity: { type: Number, default: 0 },
      rainStatus: { type: String, enum: ["NO_RAIN", "LIGHT_RAIN", "HEAVY_RAIN"], default: "NO_RAIN" },
    },
    actuatorState: {
      pumpActive: { type: Boolean, default: false },
      lastIrrigationDurationSec: { type: Number, default: 0 },
      triggerSource: { type: String, enum: ["MANUAL", "AUTO_RULE", "AI_RECOMMENDATION"] },
    },
    alerts: [
      {
        type: { type: String },
        severity: { type: String, enum: ["low", "warning", "critical"] },
        message: { type: String },
      },
    ],
    recordedAt: { type: Date, required: true, index: true },
    syncedAt: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

// Compound index for high-speed time-series trend queries
TelemetrySchema.index({ zoneId: 1, recordedAt: -1 });

export const Telemetry: Model<ITelemetryDocument> =
  mongoose.models.Telemetry || mongoose.model<ITelemetryDocument>("Telemetry", TelemetrySchema);