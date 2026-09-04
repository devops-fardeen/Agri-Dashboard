export interface TelemetryReading {
  id?: string;
  sensorId: string;
  zoneId: string;
  soilMoisture: number; // percentage (0 - 100%)
  temperature: number; // Celsius
  humidity: number; // percentage (0 - 100%)
  soilPh?: number; // 0 - 14
  batteryLevel?: number; // percentage (0 - 100%)
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
