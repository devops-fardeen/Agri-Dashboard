export interface TelemetryReading {
  id?: string;
  sensorId: string;
  zoneId: string;
  soilMoisture: number; // percentage (0 - 100%)
  temperature: number; // Celsius
  humidity: number; // percentage (0 - 100%)
  soilPh?: number; // 0 - 14
  batteryLevel?: number; // percentage (0 - 100%)
  rainDetected?: boolean; // Physical rain sensor Pin 27
  rainIntensity?: number; // 0 - 100%
  rainStatus?: "NO_RAIN" | "LIGHT_RAIN" | "HEAVY_RAIN";
  timestamp: string | Date;
}

export interface ZoneData {
  id: string;
  name: string;
  cropType: string;
  status: "optimal" | "warning" | "critical" | "offline";
  lastSync: string | Date;
  activeSensors: number;
}
