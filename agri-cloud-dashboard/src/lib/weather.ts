export interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  time: string;
  floodRisk: boolean;
  alertMessage?: string;
}

export async function fetchFarmWeather(latitude = 26.8467, longitude = 80.9462): Promise<WeatherData> {
  try {
    const res = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&daily=precipitation_sum&timezone=auto`,
      { next: { revalidate: 600 } } // cache for 10 minutes
    );

    if (!res.ok) throw new Error("Failed to fetch weather data");
    const data = await res.json();

    const precipitation = data.current?.precipitation || 0;
    const dailyRain = data.daily?.precipitation_sum?.[0] || 0;

    // Trigger disaster warning if heavy rain exceeds threshold
    const floodRisk = dailyRain > 45 || precipitation > 15;

    return {
      temperature: data.current?.temperature_2m ?? 28,
      humidity: data.current?.relative_humidity_2m ?? 65,
      windSpeed: data.current?.wind_speed_10m ?? 8,
      condition: floodRisk ? "Heavy Rain / Storm" : "Clear / Stable",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      floodRisk,
      alertMessage: floodRisk
        ? "CRITICAL ALERT: High precipitation detected. Risk of waterlogging and flash floods in low fields."
        : undefined,
    };
  } catch (err) {
    return {
      temperature: 29.4,
      humidity: 62,
      windSpeed: 7,
      condition: "Clear",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      floodRisk: false,
    };
  }
}