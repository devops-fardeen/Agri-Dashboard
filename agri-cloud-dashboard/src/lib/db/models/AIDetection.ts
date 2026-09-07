import mongoose, { Schema, Document, Model } from "mongoose";

export interface IAIDetectionDocument extends Document {
  nodeId: string;
  modelName: "disease" | "pest" | "nutrition" | "stage";
  detectionLabel: string;
  confidence: number;
  imagePath?: string;
  metadata?: Record<string, any>;
  recordedAt: Date;
  syncedAt: Date;
}

const AIDetectionSchema = new Schema<IAIDetectionDocument>(
  {
    nodeId: { type: String, required: true, index: true },
    modelName: { 
      type: String, 
      required: true, 
      enum: ["disease", "pest", "nutrition", "stage"], 
      index: true 
    },
    detectionLabel: { type: String, required: true },
    confidence: { type: Number, required: true },
    imagePath: { type: String },
    metadata: { type: Schema.Types.Mixed },
    recordedAt: { type: Date, required: true, index: true },
    syncedAt: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

// Compound index for instant querying of latest detection per node/model
AIDetectionSchema.index({ nodeId: 1, modelName: 1, recordedAt: -1 });

export const AIDetection: Model<IAIDetectionDocument> =
  mongoose.models.AIDetection || mongoose.model<IAIDetectionDocument>("AIDetection", AIDetectionSchema);
