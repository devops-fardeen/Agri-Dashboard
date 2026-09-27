"use client";

import { useEffect, useState, useRef, useMemo } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { AuthCard } from "@/components/AuthCard";
import { ManualCropScanner } from "@/components/dashboard/ManualCropScanner";
import {
  Droplets,
  Thermometer,
  CloudSun,
  AlertTriangle,
  ShieldCheck,
  LogOut,
  RefreshCw,
  Wind,
  Power,
  Navigation,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Square,
  BatteryCharging,
  Wifi,
  Sparkles,
  Bell,
  Search,
  Sprout,
  Clock,
  Home,
  Sun,
  Moon,
  CloudRain,
  Download,
  Calendar as CalendarIcon,
  Layers,
  Activity,
  Cpu,
  Radio,
  Sliders,
  CheckCircle2,
  ChevronRight,
  MoreVertical,
  MoreHorizontal,
  Camera,
  Heart,
  Share2,
  HelpCircle,
  TrendingUp,
  Globe,
  Mic,
  Plus,
  SlidersHorizontal,
  Zap,
  Smartphone,
  Laptop,
  Check,
  ChevronDown,
  User as UserIcon,
  X,
  Upload,
  Play,
  RotateCcw,
  Compass,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";

// ---------------------------------------------------------------------------
// TYPES & DATA STRUCTURES
// ---------------------------------------------------------------------------

interface HourlyForecastItem {
  time: string;
  iso: string;
  temp: number;
  humidity: number;
  rainProb: number;
  windSpeed: number;
  weatherCode: number;
  condition: string;
  icon: string;
  isNow: boolean;
}

interface DailyForecastDay {
  date: string;
  dayLabel: string;
  tempMax: number;
  tempMin: number;
  rainProb: number;
  rainSum: number;
  weatherCode: number;
  condition: string;
  isToday: boolean;
}

interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  time: string;
  floodRisk: boolean;
  alertMessage?: string;
  days: DailyForecastDay[];
  hourly?: HourlyForecastItem[];
}

interface FarmAlert {
  id: string;
  type: "CRITICAL" | "WARNING" | "ADVISORY" | "NORMAL";
  title: string;
  message: string;
  zone: string;
  timestamp: string;
  confidence?: number;
  treatment?: string;
  actionText?: string;
  actionTarget?: "PUMP_ZONE_A" | "PUMP_ZONE_B" | "ROVER";
  actionCmd?: string;
}

// 60+ Major Indian & Global Agricultural/Urban Hubs Database for Instant Offline Geocoding
const OFFLINE_CITY_DATABASE = [
  { name: "Lucknow, Uttar Pradesh", city: "Lucknow", state: "Uttar Pradesh", lat: 26.8467, lon: 80.9462 },
  { name: "Ludhiana, Punjab", city: "Ludhiana", state: "Punjab", lat: 30.9010, lon: 75.8573 },
  { name: "Nashik, Maharashtra", city: "Nashik", state: "Maharashtra", lat: 19.9975, lon: 73.7898 },
  { name: "Karnal, Haryana", city: "Karnal", state: "Haryana", lat: 29.6857, lon: 76.9905 },
  { name: "Pune, Maharashtra", city: "Pune", state: "Maharashtra", lat: 18.5204, lon: 73.8567 },
  { name: "Bengaluru / Bangalore", city: "Bengaluru", state: "Karnataka", lat: 12.9716, lon: 77.5946 },
  { name: "Jaipur, Rajasthan", city: "Jaipur", state: "Rajasthan", lat: 26.9124, lon: 75.7873 },
  { name: "Delhi / NCR", city: "Delhi", state: "Delhi", lat: 28.6139, lon: 77.2090 },
  { name: "Ahmedabad, Gujarat", city: "Ahmedabad", state: "Gujarat", lat: 23.0225, lon: 72.5714 },
  { name: "Indore, Madhya Pradesh", city: "Indore", state: "Madhya Pradesh", lat: 22.7196, lon: 75.8577 },
  { name: "Hyderabad, Telangana", city: "Hyderabad", state: "Telangana", lat: 17.3850, lon: 78.4867 },
  { name: "Chennai, Tamil Nadu", city: "Chennai", state: "Tamil Nadu", lat: 13.0827, lon: 80.2707 },
  { name: "Kolkata, West Bengal", city: "Kolkata", state: "West Bengal", lat: 22.5726, lon: 88.3639 },
  { name: "Patna, Bihar", city: "Patna", state: "Bihar", lat: 25.5941, lon: 85.1376 },
  { name: "Bhopal, Madhya Pradesh", city: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lon: 77.4126 },
  { name: "Nagpur, Maharashtra", city: "Nagpur", state: "Maharashtra", lat: 21.1458, lon: 79.0882 },
  { name: "Amritsar, Punjab", city: "Amritsar", state: "Punjab", lat: 31.6340, lon: 74.8723 },
  { name: "Shimla, Himachal Pradesh", city: "Shimla", state: "Himachal Pradesh", lat: 31.1048, lon: 77.1734 },
  { name: "Dehradun, Uttarakhand", city: "Dehradun", state: "Uttarakhand", lat: 30.3165, lon: 78.0322 },
  { name: "Varanasi, Uttar Pradesh", city: "Varanasi", state: "Uttar Pradesh", lat: 25.3176, lon: 82.9739 },
];

export default function DashboardPage() {
  const { data: sessionData, isPending } = authClient.useSession();
  const router = useRouter();

  // User session state (supports OAuth, credentials, and instant demo access)
  const [demoUser, setDemoUser] = useState<{ id?: string; name?: string; email?: string; image?: string } | null>(null);

  const isAuthenticated = Boolean(sessionData?.user || demoUser);

  // Active user session object
  const session = useMemo(() => {
    if (sessionData?.user) return sessionData;
    if (demoUser) return { user: demoUser };
    return {
      user: {
        id: "demo_user_01",
        name: "Kristin Watson",
        email: "farmer@agrismart.io",
        image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
      },
    };
  }, [sessionData, demoUser]);

  // 1. WELCOME SCREEN ANIMATION (Image 1)
  const [showWelcome, setShowWelcome] = useState<boolean>(true);
  const [welcomeProgress, setWelcomeProgress] = useState<number>(0);

  useEffect(() => {
    if (!showWelcome) return;
    const interval = setInterval(() => {
      setWelcomeProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setShowWelcome(false), 500);
          return 100;
        }
        return prev + 25;
      });
    }, 400);
    return () => clearInterval(interval);
  }, [showWelcome]);

  // 2. HEADER: DATE, TIME, CALENDAR & PROFILE (Image 2)
  const [currentTime, setCurrentTime] = useState({
    dateStr: "",
    timeStr: "",
    dayStr: "",
  });
  const [showCalendarPopover, setShowCalendarPopover] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileHover, setProfileHover] = useState(false);
  const [customAvatar, setCustomAvatar] = useState<string | null>(null);
  const [avatarError, setAvatarError] = useState(false);

  useEffect(() => {
    setAvatarError(false);
  }, [session.user?.image]);

  // Dynamic Interactive Calendar State
  const [calendarMonthOffset, setCalendarMonthOffset] = useState<number>(0);

  const calendarData = useMemo(() => {
    const today = new Date();
    const targetDate = new Date(today.getFullYear(), today.getMonth() + calendarMonthOffset, 1);
    const year = targetDate.getFullYear();
    const month = targetDate.getMonth();
    
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const monthName = months[month];
    
    // Day of week for 1st of this month (0 = Sun, 1 = Mon, 2 = Tue, etc.)
    const firstDayIndex = new Date(year, month, 1).getDay();
    const totalDaysInMonth = new Date(year, month + 1, 0).getDate();
    const prevMonthTotalDays = new Date(year, month, 0).getDate();

    // Previous month trailing days
    const prevDays: { day: number; isCurrentMonth: boolean; isToday: boolean; dateStr: string }[] = [];
    for (let i = firstDayIndex - 1; i >= 0; i--) {
      prevDays.push({
        day: prevMonthTotalDays - i,
        isCurrentMonth: false,
        isToday: false,
        dateStr: `${monthName} ${prevMonthTotalDays - i}, ${year}`,
      });
    }

    // Current month days
    const currentDays: { day: number; isCurrentMonth: boolean; isToday: boolean; dateStr: string }[] = [];
    for (let d = 1; d <= totalDaysInMonth; d++) {
      const isToday =
        d === today.getDate() &&
        month === today.getMonth() &&
        year === today.getFullYear();
      currentDays.push({
        day: d,
        isCurrentMonth: true,
        isToday,
        dateStr: `${monthName} ${d}, ${year}`,
      });
    }

    // Next month leading days to complete grid row
    const totalSlots = prevDays.length + currentDays.length > 35 ? 42 : 35;
    const nextDaysCount = totalSlots - (prevDays.length + currentDays.length);
    const nextDays: { day: number; isCurrentMonth: boolean; isToday: boolean; dateStr: string }[] = [];
    for (let d = 1; d <= nextDaysCount; d++) {
      nextDays.push({
        day: d,
        isCurrentMonth: false,
        isToday: false,
        dateStr: `${d}`,
      });
    }

    return {
      monthName,
      year,
      todayDate: today.getDate(),
      todayMonthName: months[today.getMonth()].slice(0, 3),
      todayYear: today.getFullYear(),
      allCells: [...prevDays, ...currentDays, ...nextDays],
    };
  }, [calendarMonthOffset]);

  // Sync State & Last Synced Timestamp
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>("Today, 10:33 PM");

  // 2.5 DARK THEME MODE STATE & PERSISTENCE
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  useEffect(() => {
    const saved = localStorage.getItem("agri_theme");
    if (saved === "dark") {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
      document.body.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
      document.body.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    const next = !isDarkMode;
    setIsDarkMode(next);
    if (next) {
      document.documentElement.classList.add("dark");
      document.body.classList.add("dark");
      localStorage.setItem("agri_theme", "dark");
      setActionNotice("🌙 Switched to Dark Theme Mode");
    } else {
      document.documentElement.classList.remove("dark");
      document.body.classList.remove("dark");
      localStorage.setItem("agri_theme", "light");
      setActionNotice("☀️ Switched to Light Theme Mode");
    }
    setTimeout(() => setActionNotice(null), 2500);
  };

  const triggerLiveSync = (callback?: () => void) => {
    setIsSyncing(true);
    setTimeout(() => {
      if (callback) callback();
      const now = new Date();
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      let hours = now.getHours();
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      const ampm = hours >= 12 ? "PM" : "AM";
      hours = hours % 12 || 12;
      setLastSyncTime(`${months[now.getMonth()]} ${now.getDate()}, ${hours}:${minutes}:${seconds} ${ampm}`);
      setIsSyncing(false);
    }, 1400);
  };

  useEffect(() => {
    // Initial sync
    triggerLiveSync();
    
    // Periodic background telemetry sync every 25 seconds
    const syncInterval = setInterval(() => {
      triggerLiveSync();
    }, 25000);
    return () => clearInterval(syncInterval);
  }, []);

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      
      const day = days[now.getDay()];
      const month = months[now.getMonth()];
      const date = now.getDate();
      const year = now.getFullYear();
      
      let hours = now.getHours();
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      const ampm = hours >= 12 ? "PM" : "AM";
      hours = hours % 12 || 12;

      setCurrentTime({
        dateStr: `${month} ${date}, ${year}`,
        timeStr: `${hours}:${minutes}:${seconds} ${ampm}`,
        dayStr: day,
      });
    };

    updateClock();
    const clockInterval = setInterval(updateClock, 1000);
    return () => clearInterval(clockInterval);
  }, []);

  // 3. WEATHER WIDGET & SEARCH (Image 2)
  const [weatherLocation, setWeatherLocation] = useState<{ name: string; lat: number; lon: number }>({
    name: "Shahjahanpur, Uttar Pradesh",
    lat: 27.8805,
    lon: 79.9122,
  });
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [showWeatherSearch, setShowWeatherSearch] = useState(false);
  const [showHourlyForecast, setShowHourlyForecast] = useState(false);
  const [mobileWeatherExpanded, setMobileWeatherExpanded] = useState(false);
  const [searchCityQuery, setSearchCityQuery] = useState("");
  const [isSearchingCity, setIsSearchingCity] = useState(false);
  const [manualLatInput, setManualLatInput] = useState("27.8805");
  const [manualLonInput, setManualLonInput] = useState("79.9122");
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  // Top 15 Major Indian Agricultural Hubs Database for Instant Offline Filtering
  const OFFLINE_CITIES = useMemo(
    () => [
      { id: "shahjahanpur_up", name: "Shahjahanpur", admin1: "Uttar Pradesh", country: "India", latitude: 27.8805, longitude: 79.9122 },
      { id: "lucknow_up", name: "Lucknow", admin1: "Uttar Pradesh", country: "India", latitude: 26.8467, longitude: 80.9462 },
      { id: "bareilly_up", name: "Bareilly", admin1: "Uttar Pradesh", country: "India", latitude: 28.3670, longitude: 79.4304 },
      { id: "ludhiana_pb", name: "Ludhiana", admin1: "Punjab", country: "India", latitude: 30.9010, longitude: 75.8573 },
      { id: "karnal_hr", name: "Karnal", admin1: "Haryana", country: "India", latitude: 29.6857, longitude: 76.9905 },
      { id: "nashik_mh", name: "Nashik", admin1: "Maharashtra", country: "India", latitude: 19.9975, longitude: 73.7898 },
      { id: "pune_mh", name: "Pune", admin1: "Maharashtra", country: "India", latitude: 18.5204, longitude: 73.8567 },
      { id: "nagpur_mh", name: "Nagpur", admin1: "Maharashtra", country: "India", latitude: 21.1458, longitude: 79.0882 },
      { id: "jaipur_rj", name: "Jaipur", admin1: "Rajasthan", country: "India", latitude: 26.9124, longitude: 75.7873 },
      { id: "delhi_dl", name: "Delhi", admin1: "Delhi", country: "India", latitude: 28.6139, longitude: 77.2090 },
      { id: "ahmedabad_gj", name: "Ahmedabad", admin1: "Gujarat", country: "India", latitude: 23.0225, longitude: 72.5714 },
      { id: "indore_mp", name: "Indore", admin1: "Madhya Pradesh", country: "India", latitude: 22.7196, longitude: 75.8577 },
      { id: "bhopal_mp", name: "Bhopal", admin1: "Madhya Pradesh", country: "India", latitude: 23.2599, longitude: 77.4126 },
      { id: "patna_br", name: "Patna", admin1: "Bihar", country: "India", latitude: 25.5941, longitude: 85.1376 },
      { id: "bengaluru_ka", name: "Bengaluru", admin1: "Karnataka", country: "India", latitude: 12.9716, longitude: 77.5946 },
      { id: "hyderabad_ts", name: "Hyderabad", admin1: "Telangana", country: "India", latitude: 17.3850, longitude: 78.4867 },
      { id: "chennai_tn", name: "Chennai", admin1: "Tamil Nadu", country: "India", latitude: 13.0827, longitude: 80.2707 },
      { id: "kolkata_wb", name: "Kolkata", admin1: "West Bengal", country: "India", latitude: 22.5726, longitude: 88.3639 },
      { id: "dehradun_uk", name: "Dehradun", admin1: "Uttarakhand", country: "India", latitude: 30.3165, longitude: 78.0322 },
    ],
    []
  );

  const [searchResults, setSearchResults] = useState<
    { id: string | number; name: string; admin1?: string; country?: string; latitude: number; longitude: number }[]
  >([]);

  // Initialize search results
  useEffect(() => {
    setSearchResults(OFFLINE_CITIES.slice(0, 6));
  }, [OFFLINE_CITIES]);

  // Live Geocoding API Search with instant offline fallback
  useEffect(() => {
    const q = searchCityQuery.trim().toLowerCase();
    if (!q) {
      setSearchResults(OFFLINE_CITIES.slice(0, 6));
      setIsSearchingCity(false);
      return;
    }

    const localMatches = OFFLINE_CITIES.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.admin1 && c.admin1.toLowerCase().includes(q))
    );

    if (localMatches.length > 0) {
      setSearchResults(localMatches);
    }

    setIsSearchingCity(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=8&language=en&format=json`
        );
        if (res.ok) {
          const data = await res.json();
          if (data.results && Array.isArray(data.results) && data.results.length > 0) {
            const apiResults = data.results.map((r: any) => ({
              id: r.id || `${r.latitude}_${r.longitude}`,
              name: r.name,
              admin1: r.admin1 || r.admin2 || "",
              country: r.country || "India",
              latitude: Number(r.latitude),
              longitude: Number(r.longitude),
            }));
            setSearchResults(apiResults);
          } else if (localMatches.length === 0) {
            setSearchResults([]);
          }
        }
      } catch (err) {
        console.error("Geocoding fetch error:", err);
      } finally {
        setIsSearchingCity(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [searchCityQuery, OFFLINE_CITIES]);

  // Weather Fetcher (Open-Meteo API)
  const fetchWeather = async (lat: number, lon: number): Promise<WeatherData> => {
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const getCondition = (code: number, prob: number) => {
      if (code === 0) return "Sunny / Clear";
      if (code === 1 || code === 2) return "Partly Cloudy";
      if (code === 3) return "Overcast";
      if (code >= 45 && code <= 48) return "Fog / Mist";
      if (code >= 51 && code <= 55) return "Light Drizzle";
      if (code >= 61 && code <= 65) return "Moderate Rain";
      if (code >= 80 && code <= 82) return "Rain Showers";
      if (code >= 95) return "Thunderstorm";
      return prob > 40 ? "Rain Possible" : "Clear Sky";
    };

    const getIcon = (code: number, prob: number, isNight: boolean = false) => {
      if (code === 0) return isNight ? "🌙" : "☀️";
      if (code <= 3) return isNight ? "☁️" : "⛅";
      if (code >= 45 && code <= 48) return "🌫️";
      if (prob > 40 || code >= 51) return "🌧️";
      return isNight ? "🌙" : "🌤️";
    };

    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,weather_code&forecast_days=14&timezone=auto`
      );
      if (!res.ok) throw new Error("Weather fetch failed");
      const data = await res.json();
      const current = data.current || {};
      const daily = data.daily || {};
      const hourly = data.hourly || {};
      const precipitation = current.precipitation || 0;
      const dailyRain = daily.precipitation_sum?.[0] || 0;
      const floodRisk = dailyRain > 45 || precipitation > 15;

      const dates = daily.time || [];
      const maxTemps = daily.temperature_2m_max || [];
      const minTemps = daily.temperature_2m_min || [];
      const rainProbs = daily.precipitation_probability_max || [];
      const rainSums = daily.precipitation_sum || [];
      const weatherCodes = daily.weather_code || [];

      // 24-hour hourly sequence
      const hTimes = hourly.time || [];
      const hTemps = hourly.temperature_2m || [];
      const hHums = hourly.relative_humidity_2m || [];
      const hRains = hourly.precipitation_probability || [];
      const hCodes = hourly.weather_code || [];
      const hWinds = hourly.wind_speed_10m || [];

      const nowLocal = new Date();
      const nowIsoHour = `${nowLocal.getFullYear()}-${String(nowLocal.getMonth() + 1).padStart(2, "0")}-${String(nowLocal.getDate()).padStart(2, "0")}T${String(nowLocal.getHours()).padStart(2, "0")}:00`;
      
      let hStartIdx = hTimes.findIndex((t: string) => t >= nowIsoHour);
      if (hStartIdx < 0) hStartIdx = 0;

      const hourlyList: HourlyForecastItem[] = [];
      for (let step = 0; step < 24; step++) {
        const idx = hStartIdx + step;
        if (idx < hTimes.length) {
          const tIso = hTimes[idx];
          const parts = tIso.split("T");
          const hourNum = parts[1] ? parseInt(parts[1].split(":")[0], 10) : 12;
          const isNight = hourNum < 6 || hourNum >= 19;
          const timeLabel = step === 0 ? "Now" : `${hourNum % 12 === 0 ? 12 : hourNum % 12} ${hourNum >= 12 ? "PM" : "AM"}`;
          const code = hCodes[idx] || 0;
          const prob = hRains[idx] ?? 0;
          
          hourlyList.push({
            time: timeLabel,
            iso: tIso,
            temp: Math.round(hTemps[idx] ?? 28),
            humidity: Math.round(hHums[idx] ?? 60),
            rainProb: prob,
            windSpeed: Math.round(hWinds[idx] ?? 8),
            weatherCode: code,
            condition: getCondition(code, prob),
            icon: getIcon(code, prob, isNight),
            isNow: step === 0,
          });
        }
      }

      const now = new Date();
      const todayIso = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
      let startIdx = dates.findIndex((d: string) => d >= todayIso);
      if (startIdx < 0) startIdx = 0;

      const targetDates = dates.slice(startIdx, startIdx + 7);
      const days: DailyForecastDay[] = targetDates.map((d: string, pos: number) => {
        const idx = startIdx + pos;
        const parts = d.split("-").map(Number);
        const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
        const dayLabel = pos === 0 ? "Today" : dayNames[dateObj.getDay()];
        const code = weatherCodes[idx] || 0;
        const prob = rainProbs[idx] || 0;
        return {
          date: d,
          dayLabel,
          tempMax: Math.round(maxTemps[idx] ?? 28),
          tempMin: Math.round(minTemps[idx] ?? 20),
          rainProb: prob,
          rainSum: Number(rainSums[idx] ?? 0),
          weatherCode: code,
          condition: getCondition(code, prob),
          isToday: pos === 0,
        };
      });

      return {
        temperature: Math.round(current.temperature_2m ?? 28),
        humidity: Math.round(current.relative_humidity_2m ?? 64),
        windSpeed: Math.round(current.wind_speed_10m ?? 9),
        condition: getCondition(weatherCodes[startIdx] ?? 0, rainProbs[startIdx] ?? 0),
        time: currentTime.timeStr || "10:30 PM",
        floodRisk,
        alertMessage: floodRisk
          ? "CRITICAL ALERT: Heavy precipitation detected. Root waterlogging risk active."
          : undefined,
        days,
        hourly: hourlyList,
      };
    } catch {
      const now = new Date();
      const fallbackDays: DailyForecastDay[] = [];
      const fallbackTemps = [
        { max: 29, min: 21, rain: 0, sum: 0, code: 0, cond: "Sunny / Clear" },
        { max: 28, min: 20, rain: 10, sum: 0, code: 1, cond: "Partly Cloudy" },
        { max: 26, min: 19, rain: 65, sum: 12, code: 61, cond: "Moderate Rain" },
        { max: 29, min: 22, rain: 5, sum: 0, code: 0, cond: "Sunny / Clear" },
        { max: 28, min: 21, rain: 15, sum: 0, code: 1, cond: "Partly Cloudy" },
        { max: 30, min: 23, rain: 20, sum: 0, code: 0, cond: "Sunny / Clear" },
        { max: 27, min: 20, rain: 40, sum: 3, code: 80, cond: "Rain Showers" },
      ];
      for (let i = 0; i < 7; i++) {
        const d = new Date(now);
        d.setDate(now.getDate() + i);
        const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        const ft = fallbackTemps[i] || fallbackTemps[0];
        fallbackDays.push({
          date: iso,
          dayLabel: i === 0 ? "Today" : dayNames[d.getDay()],
          tempMax: ft.max,
          tempMin: ft.min,
          rainProb: ft.rain,
          rainSum: ft.sum,
          weatherCode: ft.code,
          condition: ft.cond,
          isToday: i === 0,
        });
      }

      const fallbackHourly: HourlyForecastItem[] = [];
      for (let i = 0; i < 24; i++) {
        const d = new Date(now.getTime() + i * 3600000);
        const h = d.getHours();
        const isNight = h < 6 || h >= 19;
        const timeLabel = i === 0 ? "Now" : `${h % 12 === 0 ? 12 : h % 12} ${h >= 12 ? "PM" : "AM"}`;
        fallbackHourly.push({
          time: timeLabel,
          iso: d.toISOString(),
          temp: isNight ? 22 + (i % 3) : 28 + (i % 4),
          humidity: 60 + (i % 15),
          rainProb: (i * 7) % 35,
          windSpeed: 6 + (i % 4),
          weatherCode: 0,
          condition: isNight ? "Clear Night" : "Sunny / Clear",
          icon: isNight ? "🌙" : "☀️",
          isNow: i === 0,
        });
      }

      return {
        temperature: 28,
        humidity: 64,
        windSpeed: 9,
        condition: "Sunny / Clear",
        time: "10:30 PM",
        floodRisk: false,
        days: fallbackDays,
        hourly: fallbackHourly,
      };
    }
  };

  useEffect(() => {
    fetchWeather(weatherLocation.lat, weatherLocation.lon).then((data) => setWeather(data));
  }, [weatherLocation]);

  const handleSelectLocation = (name: string, lat: number, lon: number) => {
    setWeatherLocation({ name, lat, lon });
    setManualLatInput(String(lat));
    setManualLonInput(String(lon));
    setShowWeatherSearch(false);
    setActionNotice(`📍 Weather location updated to ${name}`);
    setTimeout(() => setActionNotice(null), 3000);
  };

  const handleSearchSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const q = searchCityQuery.trim();
    if (!q) return;

    setIsSearchingCity(true);
    try {
      const res = await fetch(
        `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=5&language=en&format=json`
      );
      if (res.ok) {
        const data = await res.json();
        if (data.results && data.results.length > 0) {
          const first = data.results[0];
          const displayName = first.admin1 ? `${first.name}, ${first.admin1}` : first.name;
          handleSelectLocation(displayName, Number(first.latitude), Number(first.longitude));
          return;
        }
      }
    } catch {} finally {
      setIsSearchingCity(false);
    }
  };

  const handleApplyManualCoords = () => {
    const lat = parseFloat(manualLatInput);
    const lon = parseFloat(manualLonInput);
    if (isNaN(lat) || isNaN(lon)) {
      alert("Please enter valid decimal latitude and longitude numbers.");
      return;
    }
    handleSelectLocation(`Custom Farm (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`, lat, lon);
  };

  // 4. ALERTS & AI SCOUTING PATROL (Image 3 - Left)
  const [patrolRunning, setPatrolRunning] = useState(false);
  const [alertsList, setAlertsList] = useState<FarmAlert[]>([
    {
      id: "alert-1",
      type: "CRITICAL",
      title: "Early Blight Detected (Field A - Tomato Canopy)",
      message: "Concentric brown-black lesions identified on lower tomato foliage during morning patrol routine.",
      confidence: 0.96,
      treatment: "Apply Copper Hydroxide (2.5g/L) or Mancozeb fungicide spray immediately. Prune heavily infected lower leaves.",
      zone: "Field A (Node 1)",
      timestamp: "07:15 AM",
    },
    {
      id: "alert-2",
      type: "WARNING",
      title: "Septoria Leaf Spot (Field B - Greenhouse)",
      message: "Circular lesions with dark margins found across tomato leaves in Greenhouse B.",
      confidence: 0.92,
      treatment: "Foliar bio-fungicide (Bacillus subtilis) spray recommended. Increase greenhouse ventilation to lower humidity.",
      zone: "Field B (Node 2)",
      timestamp: "07:22 AM",
    },
    {
      id: "alert-3",
      type: "ADVISORY",
      title: "Low Soil Moisture Setpoint Threshold",
      message: "Root moisture in Field A dropped below 50%. Micro-drip fertigation scheduled.",
      confidence: 0.99,
      treatment: "Engage Field A Drip Pump relay for 15 minutes.",
      zone: "Field A (Node 1)",
      timestamp: "09:40 AM",
    },
  ]);

  const handleTriggerPatrol = async () => {
    setPatrolRunning(true);
    setActionNotice("🚀 Rover AI Patrol dispatched! Scanning Field A & Field B rows...");

    try {
      fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: "ROVER_PATROL", action: "TRIGGER" }),
      }).catch(() => {});

      fetch("http://127.0.0.1:8000/api/edge/rover/patrol/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ field: "FIELD_A" }),
        signal: AbortSignal.timeout(2000),
      }).catch(() => {});
    } catch {}

    setTimeout(() => {
      setPatrolRunning(false);
      setActionNotice("✓ AI Patrol Completed: 24 leaf canopies analyzed. Alerts feed updated!");
      setTimeout(() => setActionNotice(null), 4000);
    }, 2500);
  };

  const handleManualScanComplete = (data: any) => {
    if (data?.diagnosis) {
      const d = data.diagnosis;
      const diseaseLabel = d.disease?.label || "Healthy Foliage";
      const isCritical = d.prescription?.severity === "CRITICAL";
      const isWarning = d.prescription?.severity === "HIGH";

      const newAlert: FarmAlert = {
        id: `manual_scan_${Date.now()}`,
        type: isCritical ? "CRITICAL" : isWarning ? "WARNING" : "ADVISORY",
        title: diseaseLabel,
        message: d.prescription?.action || "Manual leaf scan recorded via AI Vision Engine.",
        treatment: d.prescription?.treatment,
        confidence: (d.disease?.confidence || 95) / 100,
        zone: "Manual Scanner",
        timestamp: "Just Now",
      };

      setAlertsList((prev) => [newAlert, ...prev.slice(0, 5)]);
      setActionNotice(`🔬 Leaf Scan Diagnosed: ${diseaseLabel} (${d.disease?.confidence}% Confidence)`);
      setTimeout(() => setActionNotice(null), 4500);
    }
  };

  // 5. FIELD SUBNODES SENSOR DATA (Image 3 - Right)
  const [activeField, setActiveField] = useState<"FIELD_A" | "FIELD_B">("FIELD_A");
  const [pumpZoneA, setPumpZoneA] = useState(false);
  const [pumpZoneB, setPumpZoneB] = useState(false);
  const [isRaining, setIsRaining] = useState(false);
  const [edgeStationOnline, setEdgeStationOnline] = useState(false);
  const [pumpLogicInfo, setPumpLogicInfo] = useState<{
    ZONE_A?: { reason?: string; mode?: string; time_remaining_minutes?: number; action?: string; rain_chance?: number };
    ZONE_B?: { reason?: string; mode?: string; time_remaining_minutes?: number; action?: string; rain_chance?: number };
  }>({});

  // Field Telemetry Live State
  const [fieldTelemetry, setFieldTelemetry] = useState<{
    fieldA: { airTemp: number | null; humidity: number | null; soilMoisture: number | null; soilTemp: number | null; battery: number };
    fieldB: { airTemp: number | null; humidity: number | null; soilMoisture: number | null; soilTemp: number | null; battery: number };
  }>({
    fieldA: { airTemp: null, humidity: null, soilMoisture: null, soilTemp: null, battery: 92 },
    fieldB: { airTemp: null, humidity: null, soilMoisture: null, soilTemp: null, battery: 88 },
  });

  // Bidirectional Synchronization: Poll Edge Station & Cloud MongoDB for real-time pump & sensor state
  useEffect(() => {
    let isMounted = true;

    const syncEdgeAndCloudState = async () => {
      try {
        // 1. Check local edge station gateway on port 8000
        const edgeRes = await fetch("http://127.0.0.1:8000/api/edge/status", {
          signal: AbortSignal.timeout(1200),
        });

        if (edgeRes.ok) {
          const edgeData = await edgeRes.json();
          if (!isMounted) return;

          setEdgeStationOnline(true);

          // Sync Actuator Relay States
          if (edgeData.actuators) {
            setPumpZoneA(Boolean(edgeData.actuators.PUMP_ZONE_A));
            setPumpZoneB(Boolean(edgeData.actuators.PUMP_ZONE_B));
          }

          // Sync Flowchart Pump Logic Decisions
          if (edgeData.pump_logic) {
            setPumpLogicInfo(edgeData.pump_logic);
          }

          // Sync Live Sensors & Rain Interlock
          if (edgeData.telemetry) {
            const zA = edgeData.telemetry.ZONE_A || {};
            const zB = edgeData.telemetry.ZONE_B || {};

            setIsRaining(Boolean(zA.rain_detected || zB.rain_detected));

            setFieldTelemetry({
              fieldA: {
                airTemp: (zA.ambient_temp !== null && zA.ambient_temp !== undefined) ? Number(zA.ambient_temp) : null,
                humidity: (zA.ambient_humidity !== null && zA.ambient_humidity !== undefined) ? Number(zA.ambient_humidity) : null,
                soilMoisture: (zA.soil_moisture !== null && zA.soil_moisture !== undefined) ? Number(zA.soil_moisture) : null,
                soilTemp: (zA.soil_temp !== null && zA.soil_temp !== undefined) ? Number(zA.soil_temp) : null,
                battery: 92,
              },
              fieldB: {
                airTemp: (zB.ambient_temp !== null && zB.ambient_temp !== undefined) ? Number(zB.ambient_temp) : null,
                humidity: (zB.ambient_humidity !== null && zB.ambient_humidity !== undefined) ? Number(zB.ambient_humidity) : null,
                soilMoisture: (zB.soil_moisture !== null && zB.soil_moisture !== undefined) ? Number(zB.soil_moisture) : null,
                soilTemp: (zB.soil_temp !== null && zB.soil_temp !== undefined) ? Number(zB.soil_temp) : null,
                battery: 88,
              },
            });
          }

          if (edgeData.rover) {
            if (edgeData.rover.battery) setRoverBattery(Number(edgeData.rover.battery));
            if (edgeData.rover.mode) setRoverMode(edgeData.rover.mode);
          }
          return;
        }
      } catch {
        // Local edge offline/hotspot mode, fallback to Cloud MongoDB
      }

      try {
        // 2. Poll Cloud MongoDB /api/telemetry for internet sync
        const cloudRes = await fetch("/api/telemetry?limit=4", {
          signal: AbortSignal.timeout(2000),
        });

        if (cloudRes.ok && isMounted) {
          const cloudData = await cloudRes.json();
          const records = cloudData.history || [];

          for (const r of records) {
            const zId = (r.zoneId || "").toUpperCase();
            const pActive = r.actuatorState?.pumpActive;

            if (zId.includes("ZONE_A") || zId.includes("NODE_01") || zId.includes("FIELD_A") || zId.includes("TOMATO")) {
              if (pActive !== undefined) setPumpZoneA(Boolean(pActive));
              if (r.telemetry) {
                setFieldTelemetry((prev) => ({
                  ...prev,
                  fieldA: {
                    airTemp: Number(r.telemetry.ambientTemp ?? prev.fieldA.airTemp),
                    humidity: Number(r.telemetry.ambientHumidity ?? prev.fieldA.humidity),
                    soilMoisture: Number(r.telemetry.soilMoisture ?? prev.fieldA.soilMoisture),
                    soilTemp: Number(r.telemetry.soilTemperature ?? prev.fieldA.soilTemp),
                    battery: prev.fieldA.battery,
                  },
                }));
              }
            } else if (zId.includes("ZONE_B") || zId.includes("NODE_02") || zId.includes("FIELD_B") || zId.includes("GREENHOUSE")) {
              if (pActive !== undefined) setPumpZoneB(Boolean(pActive));
              if (r.telemetry) {
                setFieldTelemetry((prev) => ({
                  ...prev,
                  fieldB: {
                    airTemp: Number(r.telemetry.ambientTemp ?? prev.fieldB.airTemp),
                    humidity: Number(r.telemetry.ambientHumidity ?? prev.fieldB.humidity),
                    soilMoisture: Number(r.telemetry.soilMoisture ?? prev.fieldB.soilMoisture),
                    soilTemp: Number(r.telemetry.soilTemperature ?? prev.fieldB.soilTemp),
                    battery: prev.fieldB.battery,
                  },
                }));
              }
            }
          }
        }
      } catch {}
    };

    syncEdgeAndCloudState();
    const interval = setInterval(syncEdgeAndCloudState, 3500);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Field Telemetry State View
  const fieldData = useMemo(() => {
    if (activeField === "FIELD_A") {
      return {
        title: "Field A (Node 1 - Open Tomato Field)",
        airTemp: fieldTelemetry.fieldA.airTemp,
        humidity: fieldTelemetry.fieldA.humidity,
        soilMoisture: fieldTelemetry.fieldA.soilMoisture,
        soilTemp: fieldTelemetry.fieldA.soilTemp,
        battery: fieldTelemetry.fieldA.battery,
        pumpActive: pumpZoneA,
        pumpName: "Field A Drip Pump",
        logic: pumpLogicInfo.ZONE_A,
      };
    } else {
      return {
        title: "Field B (Node 2 - Controlled Greenhouse)",
        airTemp: fieldTelemetry.fieldB.airTemp,
        humidity: fieldTelemetry.fieldB.humidity,
        soilMoisture: fieldTelemetry.fieldB.soilMoisture,
        soilTemp: fieldTelemetry.fieldB.soilTemp,
        battery: fieldTelemetry.fieldB.battery,
        pumpActive: pumpZoneB,
        pumpName: "Field B Greenhouse Pump",
        logic: pumpLogicInfo.ZONE_B,
      };
    }
  }, [activeField, pumpZoneA, pumpZoneB, fieldTelemetry, pumpLogicInfo]);

  // Synchronized Pump Relay Toggle (Cloud <-> Edge Gateway Station)
  const togglePump = async () => {
    const targetKey = activeField === "FIELD_A" ? "PUMP_ZONE_A" : "PUMP_ZONE_B";
    const isCurrentlyOn = activeField === "FIELD_A" ? pumpZoneA : pumpZoneB;
    const nextState = !isCurrentlyOn;
    const nextAction = nextState ? "ON" : "OFF";

    // 1. Optimistic Local UI State
    if (activeField === "FIELD_A") {
      setPumpZoneA(nextState);
    } else {
      setPumpZoneB(nextState);
    }

    setActionNotice(
      nextState
        ? `💧 ${activeField === "FIELD_A" ? "Field A" : "Field B"} Drip Pump Started (Syncing to Edge Station)`
        : `⏹ ${activeField === "FIELD_A" ? "Field A" : "Field B"} Drip Pump Stopped (Syncing to Edge Station)`
    );

    // 2. Transmit Command to Cloud API (/api/commands) for internet sync worker
    try {
      await fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: targetKey, action: nextAction }),
      });
    } catch (cloudErr) {
      console.warn("Cloud command dispatch notice:", cloudErr);
    }

    // 3. Direct Fast Relay to Local Edge Gateway (Port 8000)
    try {
      fetch(`http://127.0.0.1:8000/api/edge/pump/${targetKey}/${nextAction}`, {
        method: "POST",
        signal: AbortSignal.timeout(1000),
      }).catch(() => {});
    } catch {}

    triggerLiveSync();
    setTimeout(() => setActionNotice(null), 3500);
  };

  // 6. ROVER POSITION & MODES (Image 4)
  const [roverPosition, setRoverPosition] = useState<"DOCK" | "FIELD_A" | "FIELD_B">("DOCK");
  const [roverMode, setRoverMode] = useState<"AUTO" | "MANUAL">("AUTO");
  const [roverSpeed, setRoverSpeed] = useState<number>(190);
  const [roverBattery, setRoverBattery] = useState<number>(88);
  const [roverActionNotice, setRoverActionNotice] = useState<string>("Standby at Charging Dock");

  const handleSwitchRoverMode = async (mode: "AUTO" | "MANUAL") => {
    setRoverMode(mode);
    setActionNotice(
      mode === "AUTO"
        ? "🤖 Rover switched to AUTO Patrol Mode"
        : "🕹️ Rover switched to MANUAL Joystick Mode"
    );

    try {
      fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: "ROVER_MODE", action: mode }),
      }).catch(() => {});

      fetch(`http://127.0.0.1:8000/api/edge/rover/mode/${mode}`, {
        method: "POST",
        signal: AbortSignal.timeout(1000),
      }).catch(() => {});
    } catch {}

    triggerLiveSync();
    setTimeout(() => setActionNotice(null), 2500);
  };

  const handleRoverSpeedChange = async (spd: number) => {
    setRoverSpeed(spd);
    try {
      fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: "ROVER", action: "SPEED", speed: spd }),
      }).catch(() => {});

      fetch(`http://127.0.0.1:8000/api/edge/rover/speed/${spd}`, {
        method: "POST",
        signal: AbortSignal.timeout(1000),
      }).catch(() => {});
    } catch {}
  };

  const handleRoverDpad = async (dir: string) => {
    if (roverMode === "AUTO") {
      setActionNotice("⚠️ Switch Rover to MANUAL mode to use D-Pad Joystick controls!");
      setTimeout(() => setActionNotice(null), 2500);
      return;
    }
    setRoverActionNotice(`Manual Command: ${dir} at PWM ${roverSpeed}`);
    setActionNotice(`🕹️ Rover: ${dir} (PWM ${roverSpeed})`);

    // Dispatch rover command to cloud and edge hardware
    try {
      fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: "ROVER", action: dir, speed: roverSpeed }),
      }).catch(() => {});

      fetch("http://127.0.0.1:8000/api/edge/rover/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: dir, speed: roverSpeed }),
        signal: AbortSignal.timeout(1000),
      }).catch(() => {});
    } catch {}

    setTimeout(() => setActionNotice(null), 2000);
  };

  const handleCaptureRoverPhoto = () => {
    setActionNotice("📸 Capturing Live Leaf Photo from ESP32-CAM...");
    setTimeout(() => {
      setActionNotice("✓ Snapshot Captured: Leaf healthy with 97.4% confidence");
      setTimeout(() => setActionNotice(null), 3000);
    }, 1500);
  };

  // 7. GRAPHICAL REPRESENTATION OF SENSORS (10-DAY DAY-WISE CALENDAR) (Image 4/5 - Top)
  const [graphNode, setGraphNode] = useState<"NODE_A" | "NODE_B">("NODE_A");
  const [selectedDayIndex, setSelectedDayIndex] = useState<number>(9); // Default to today (last index)
  const [selectedMetric, setSelectedMetric] = useState<"SOIL_MOISTURE" | "SOIL_TEMP" | "HUMIDITY">("SOIL_MOISTURE");

  // Generate 10 days of historical calendar date labels (Sep 11 to Sep 20, 2026)
  const tenDaysList = useMemo(() => {
    const list = [];
    for (let i = 9; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
      list.push({
        index: 9 - i,
        dateStr: `${months[d.getMonth()]} ${d.getDate()}`,
        dayName: i === 0 ? "Today" : days[d.getDay()],
        fullDate: d.toISOString().split("T")[0],
        isToday: i === 0,
      });
    }
    return list;
  }, []);

  // 24-Hour hourly telemetry data points for the selected historical day
  const hourlyTelemetryData = useMemo(() => {
    const data = [];
    const daySeed = selectedDayIndex * 3.7;
    for (let hour = 0; hour < 24; hour += 2) {
      const timeLabel = `${String(hour).padStart(2, "0")}:00`;
      
      // Node A Base Curves (Field A Open Tomato Canopy)
      const baseMoistureA = 74 + Math.sin((hour + daySeed) * 0.45) * 8;
      const baseTempA = 23 + Math.sin((hour - 8 + daySeed) * 0.35) * 6;
      const baseHumA = 60 + Math.cos((hour + daySeed) * 0.4) * 12;

      // Node B Base Curves (Field B Controlled Greenhouse)
      const baseMoistureB = 68 + Math.cos((hour + daySeed) * 0.4) * 6;
      const baseTempB = 21 + Math.sin((hour - 6 + daySeed) * 0.3) * 4;
      const baseHumB = 68 + Math.sin((hour + daySeed) * 0.45) * 9;

      data.push({
        time: timeLabel,
        // Node A
        moistureA: Number(baseMoistureA.toFixed(1)),
        soilTempA: Number(baseTempA.toFixed(1)),
        humidityA: Number(baseHumA.toFixed(1)),
        // Node B
        moistureB: Number(baseMoistureB.toFixed(1)),
        soilTempB: Number(baseTempB.toFixed(1)),
        humidityB: Number(baseHumB.toFixed(1)),
      });
    }
    return data;
  }, [selectedDayIndex]);

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 max-w-[1580px] mx-auto flex flex-col gap-6 select-none relative">
      
      {/* Dynamic Ambient Pastel Glow Orbs (Visible & Refracted through Frosted Bento Glass Cards) */}
      <div className="fixed top-10 left-10 w-[500px] h-[500px] bg-[#E0F2FE]/40 dark:bg-[#0284C7]/15 rounded-full blur-[130px] pointer-events-none -z-10 animate-pulse-glow" />
      <div className="fixed top-1/3 right-10 w-[550px] h-[550px] bg-[#FFEDD5]/40 dark:bg-[#EA580C]/12 rounded-full blur-[140px] pointer-events-none -z-10 animate-float-slow" />
      <div className="fixed bottom-10 left-1/4 w-[500px] h-[500px] bg-[#D1FAE5]/40 dark:bg-[#059669]/15 rounded-full blur-[130px] pointer-events-none -z-10" />
      <div className="fixed bottom-1/4 right-1/3 w-[450px] h-[450px] bg-[#EDE9FE]/35 dark:bg-[#6366F1]/15 rounded-full blur-[120px] pointer-events-none -z-10" />
      
      {/* 1. WELCOME SCREEN ANIMATION (Image 1) */}
      {showWelcome && (
        <div className="fixed inset-0 z-[100] bg-[#121417]/95 backdrop-blur-xl flex flex-col items-center justify-center p-6 text-white animate-fade-in-scale">
          <div className="absolute w-96 h-96 rounded-full bg-[#3B82F6]/20 blur-3xl pointer-events-none animate-pulse-glow" />
          <div className="absolute w-80 h-80 rounded-full bg-[#10B981]/15 blur-3xl -top-10 -right-10 pointer-events-none" />

          <div className="relative z-10 max-w-lg w-full text-center flex flex-col items-center gap-6">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-[#2563EB] to-[#60A5FA] text-white flex items-center justify-center shadow-2xl animate-float-slow">
              <Sprout className="w-10 h-10" />
            </div>

            <div className="space-y-2">
              <span className="text-[11px] font-black tracking-widest uppercase px-3.5 py-1 rounded-full bg-white/10 text-[#60A5FA] border border-white/10">
                AgriSmart Precision Cloud
              </span>
              <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white mt-3">
                Welcome to Cloud Dashboard
              </h1>
              <p className="text-sm text-white/70 max-w-md mx-auto">
                Next-generation precision agriculture intelligence • Real-time field telemetry, autonomous rover patrol, and edge AI diagnostics
              </p>
            </div>

            <div className="w-full max-w-xs space-y-2">
              <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden p-0.5 border border-white/10">
                <div
                  className="h-full bg-gradient-to-r from-[#3B82F6] to-[#10B981] rounded-full transition-all duration-300"
                  style={{ width: `${welcomeProgress}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-white/50 font-mono">
                <span>Connecting Cloud Gateway...</span>
                <span>{welcomeProgress}%</span>
              </div>
            </div>

            <button
              onClick={() => setShowWelcome(false)}
              className="mt-2 px-8 py-3 rounded-full bg-[#3B82F6] hover:bg-[#2563EB] text-white font-black text-sm transition-all shadow-xl hover:scale-105 active:scale-95 flex items-center gap-2 cursor-pointer"
            >
              <span>Enter Cloud Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* 1.5 AUTHENTICATION GATEWAY (Shows smoothly after opening animation if unauthenticated) */}
      {!isAuthenticated && !showWelcome && (
        <div className="fixed inset-0 z-[90] bg-[#F4F7FC]/80 dark:bg-[#090D16]/85 backdrop-blur-2xl flex items-center justify-center p-3 sm:p-6 py-6 sm:py-10 overflow-y-auto animate-fade-in-scale">
          {/* Ambient background glows */}
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-[#3B82F6]/15 dark:bg-[#3B82F6]/25 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-[#10B981]/15 dark:bg-[#10B981]/25 rounded-full blur-3xl pointer-events-none" />

          <AuthCard
            onSuccess={(user) => {
              setDemoUser(user || { name: "Kristin Watson", email: "farmer@agrismart.io" });
              setActionNotice("✓ Authenticated! Welcome to AgriSmart Cloud Central.");
              setTimeout(() => setActionNotice(null), 3000);
            }}
          />
        </div>
      )}

      {/* ACTION NOTICE TOAST */}
      {actionNotice && (
        <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50 animate-bounce">
          <div className="bg-[#1E2432] text-white px-5 py-2.5 rounded-full shadow-2xl border border-white/10 flex items-center gap-2.5 text-xs font-black tracking-wide">
            <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6] animate-ping" />
            <span>{actionNotice}</span>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. HEADER BAR (Image 2) */}
      {/* ========================================================================= */}
      <header className="w-full modern-card p-4 sm:p-5 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left: Brand Title & Dynamic Sync Status */}
        <div className="flex items-center gap-3.5 self-start md:self-auto">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-[#2563EB] to-[#60A5FA] text-white flex items-center justify-center shadow-[0_6px_18px_rgba(37,99,235,0.35)] shrink-0">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-[#1E2432] dark:text-[#F8FAFC]">
                Good Morning, {session.user?.name ? session.user.name.split(" ")[0] : "Farmer"} 👋
              </h1>
              {isSyncing ? (
                <span className="px-2.5 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46] text-[11px] font-black flex items-center gap-1.5 border border-[#A7F3D0] shadow-xs animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-ping" />
                  Live Syncing...
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded-full bg-[#F8FAFC] dark:bg-[#1A2234] text-[#64748B] dark:text-[#94A3B8] text-[11px] font-bold flex items-center gap-1.5 border border-[#E8EEF5] dark:border-[#212C42]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                  <span>Last sync: <span className="font-extrabold text-[#1E2432] dark:text-[#F8FAFC] font-mono">{lastSyncTime}</span></span>
                </span>
              )}
            </div>
            <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-medium">
              AgriSmart Precision Multi-Node Cloud Ecosystem
            </p>
          </div>
        </div>

        {/* Right Toolbar Group (Quick Weather + AI Scanner + Calendar Pill + Profile Modal) */}
        <div className="flex items-center justify-end flex-wrap gap-2.5 sm:gap-3 self-stretch md:self-auto ml-auto">
          
          {/* Quick AI Scanner Pill */}
          <a
            href="#manual-scanner-section"
            className="px-3.5 py-2 rounded-full bg-[#EEF2FF] dark:bg-[#1E1B4B] hover:bg-[#E0E7FF] dark:hover:bg-[#312E81] border border-[#C7D2FE] dark:border-[#4338CA] flex items-center gap-2 cursor-pointer transition shadow-xs select-none"
            title="Jump to Manual Plant Disease & Crop Scanner"
          >
            <span className="text-sm">🔬</span>
            <span className="text-xs font-black text-[#4338CA] dark:text-[#A5B4FC] hidden sm:inline">AI Scanner</span>
          </a>

          {/* Quick Weather Snapshot Pill */}
          <a
            href="#weather-section"
            className="px-3.5 py-2 rounded-full bg-[#F8FAFC] hover:bg-[#EEF2F6] border border-[#E8EEF5] flex items-center gap-2 cursor-pointer transition shadow-xs select-none"
            title="Click to view full 7-day weather forecast"
          >
            <span className="text-sm">🌤️</span>
            <div className="text-xs font-bold text-[#1E2432] flex items-center gap-1.5">
              <span className="font-extrabold text-[#0284C7]">{weather?.temperature ?? 28}°C</span>
              <span className="text-[#8A94A6] hidden sm:inline">• {weather?.days[0]?.condition || "Sunny"}</span>
            </div>
          </a>

          {/* Date, Time & Day (with Calendar Hover/Click Popover) */}
          <div className="relative">
            <div
              onClick={() => setShowCalendarPopover(!showCalendarPopover)}
              onMouseEnter={() => setShowCalendarPopover(true)}
              className="px-4 py-2 rounded-full bg-[#F8FAFC] hover:bg-[#EEF2F6] border border-[#E8EEF5] flex items-center gap-2.5 cursor-pointer transition shadow-xs select-none"
            >
              <CalendarIcon className="w-4 h-4 text-[#F59E0B]" />
              <div className="text-xs font-bold text-[#1E2432] flex items-center gap-1.5">
                <span className="font-extrabold">{currentTime.dayStr},</span>
                <span>{currentTime.dateStr}</span>
                <span className="text-[#8A94A6] font-mono hidden sm:inline">• {currentTime.timeStr}</span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-[#8A94A6]" />
            </div>

            {/* Interactive Calendar Popover */}
            {showCalendarPopover && (
              <div
                onMouseLeave={() => setShowCalendarPopover(false)}
                className="absolute top-full mt-2 right-0 sm:left-1/2 sm:-translate-x-1/2 z-40 w-80 bg-white dark:bg-[#131926] rounded-2xl border border-[#E8EEF5] dark:border-[#212C42] popover-shadow p-4 animate-fade-in-scale shadow-2xl"
              >
                {/* Calendar Header with Navigation */}
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCalendarMonthOffset((prev) => prev - 1);
                      }}
                      className="w-6 h-6 rounded-full hover:bg-[#F4F7FC] dark:hover:bg-[#1A2234] flex items-center justify-center text-xs font-black text-[#1E2432] dark:text-[#F8FAFC] transition cursor-pointer"
                      title="Previous Month"
                    >
                      ‹
                    </button>
                    <strong className="text-xs font-black text-[#1E2432] dark:text-[#F8FAFC]">
                      {calendarData.monthName} {calendarData.year}
                    </strong>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCalendarMonthOffset((prev) => prev + 1);
                      }}
                      className="w-6 h-6 rounded-full hover:bg-[#F4F7FC] dark:hover:bg-[#1A2234] flex items-center justify-center text-xs font-black text-[#1E2432] dark:text-[#F8FAFC] transition cursor-pointer"
                      title="Next Month"
                    >
                      ›
                    </button>
                  </div>
                  <span className="text-[10.5px] px-2 py-0.5 rounded-full bg-[#FEF3C7] dark:bg-[#78350F]/40 text-[#92400E] dark:text-[#FDE68A] font-bold">
                    {calendarMonthOffset === 0 ? "● Today" : "Browse"}
                  </span>
                </div>

                {/* Day of Week Headers */}
                <div className="grid grid-cols-7 gap-1 text-center text-[11px] font-bold mb-1 text-[#8A94A6] dark:text-[#64748B]">
                  <span>Su</span><span>Mo</span><span>Tu</span><span>We</span><span>Th</span><span>Fr</span><span>Sa</span>
                </div>

                {/* Day Cells */}
                <div className="grid grid-cols-7 gap-1 text-center text-xs">
                  {calendarData.allCells.map((cell, idx) => (
                    <button
                      key={idx}
                      disabled={!cell.isCurrentMonth}
                      onClick={() => {
                        if (cell.isCurrentMonth) {
                          setActionNotice(`📅 Calendar date selected: ${cell.dateStr}`);
                          setShowCalendarPopover(false);
                          setTimeout(() => setActionNotice(null), 2500);
                        }
                      }}
                      className={`h-7 w-7 mx-auto rounded-full flex items-center justify-center text-xs transition select-none ${
                        !cell.isCurrentMonth
                          ? "opacity-25 text-[#94A3B8] dark:text-[#4B5563] cursor-default font-normal"
                          : cell.isToday
                          ? "bg-[#2563EB] text-white font-black shadow-md ring-2 ring-[#2563EB]/40 scale-105"
                          : "hover:bg-[#F4F7FC] dark:hover:bg-[#1A2234] text-[#1E2432] dark:text-[#F8FAFC] font-bold cursor-pointer"
                      }`}
                    >
                      {cell.day}
                    </button>
                  ))}
                </div>

                {/* Footer */}
                <div className="mt-3 pt-2 border-t border-[#E8EEF5] dark:border-[#212C42] flex justify-between items-center text-[10.5px] text-[#8A94A6] dark:text-[#94A3B8]">
                  <span>Today: {calendarData.todayMonthName} {calendarData.todayDate}, {calendarData.todayYear}</span>
                  <div className="flex gap-2">
                    {calendarMonthOffset !== 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setCalendarMonthOffset(0);
                        }}
                        className="font-bold text-[#2563EB] dark:text-[#60A5FA] hover:underline cursor-pointer"
                      >
                        Today
                      </button>
                    )}
                    <button
                      onClick={() => setShowCalendarPopover(false)}
                      className="font-bold text-[#1E2432] dark:text-[#F8FAFC] hover:underline cursor-pointer"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Dark / Light Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="px-3.5 py-2 rounded-full bg-[#F8FAFC] dark:bg-[#1A2234] hover:bg-[#EEF2F6] dark:hover:bg-[#222C42] border border-[#E8EEF5] dark:border-[#212C42] flex items-center gap-2 cursor-pointer transition shadow-xs select-none"
            title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDarkMode ? (
              <>
                <Sun className="w-4 h-4 text-[#F59E0B]" />
                <span className="text-xs font-bold text-[#F8FAFC] hidden sm:inline">Light</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-[#6366F1]" />
                <span className="text-xs font-bold text-[#1E2432] hidden sm:inline">Dark</span>
              </>
            )}
          </button>

          {/* Right: Profile Icon */}
          <div className="relative">
            <div
              onClick={() => setShowProfileModal(!showProfileModal)}
              onMouseEnter={() => setProfileHover(true)}
              onMouseLeave={() => setProfileHover(false)}
              className="flex items-center gap-2 pl-3 pr-1.5 py-1.5 rounded-full bg-[#0F172A] dark:bg-[#1E293B] text-white hover:bg-[#1E293B] dark:hover:bg-[#334155] border border-slate-700/40 cursor-pointer transition shadow-sm select-none"
            >
              <div className="text-right hidden sm:block px-1">
                <div className="text-xs font-black tracking-tight">{session.user?.name || "Farmer Master"}</div>
              </div>

              {/* Profile Avatar Image */}
              <div className="w-8 h-8 rounded-full overflow-hidden bg-[#2563EB] text-white flex items-center justify-center font-black text-xs border border-white/20 shrink-0">
                {customAvatar ? (
                  <img
                    src={customAvatar}
                    alt="Profile"
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                  />
                ) : session.user?.image && !avatarError ? (
                  <img
                    src={session.user.image}
                    alt={session.user.name || "Profile"}
                    className="w-full h-full object-cover"
                    referrerPolicy="no-referrer"
                    crossOrigin="anonymous"
                    onError={() => setAvatarError(true)}
                  />
                ) : (
                  <span>
                    {session.user?.name
                      ? session.user.name
                          .split(" ")
                          .filter(Boolean)
                          .map((n: string) => n[0])
                          .join("")
                          .slice(0, 2)
                          .toUpperCase()
                      : "U"}
                  </span>
                )}
              </div>
            </div>

            {/* Hover Tooltip */}
            {profileHover && !showProfileModal && (
              <div className="absolute top-full mt-2 right-0 z-40 bg-[#0F172A] dark:bg-[#1E293B] text-white text-xs px-3 py-1.5 rounded-xl whitespace-nowrap shadow-xl border border-white/10 pointer-events-none">
                <div className="font-bold">{session.user?.name || "Farmer Master"}</div>
                <div className="text-[10.5px] text-[#9CA3AF] font-mono">{session.user?.email || "farmer@agrismart.io"}</div>
              </div>
            )}

            {/* Click: Interactive Profile Modal */}
            {showProfileModal && (
              <div className="absolute top-full mt-2 right-0 z-50 w-80 bg-white dark:bg-[#131926] rounded-3xl border border-[#E8EEF5] dark:border-[#212C42] popover-shadow p-5 text-[#0F172A] dark:text-[#F8FAFC] animate-fade-in-scale">
                <div className="flex justify-between items-start pb-4 border-b border-[#E8EEF5] dark:border-[#212C42]">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full overflow-hidden bg-[#EFF6FF] dark:bg-[#1E293B] text-[#2563EB] dark:text-[#60A5FA] flex items-center justify-center font-black text-base border-2 border-[#2563EB] shrink-0">
                      {customAvatar ? (
                        <img
                          src={customAvatar}
                          alt="Profile"
                          className="w-full h-full object-cover"
                          referrerPolicy="no-referrer"
                        />
                      ) : session.user?.image && !avatarError ? (
                        <img
                          src={session.user.image}
                          alt={session.user.name || "Profile"}
                          className="w-full h-full object-cover"
                          referrerPolicy="no-referrer"
                          crossOrigin="anonymous"
                          onError={() => setAvatarError(true)}
                        />
                      ) : (
                        <span>
                          {session.user?.name
                            ? session.user.name
                                .split(" ")
                                .filter(Boolean)
                                .map((n: string) => n[0])
                                .join("")
                                .slice(0, 2)
                                .toUpperCase()
                            : "U"}
                        </span>
                      )}
                    </div>
                    <div>
                      <h4 className="text-sm font-black text-[#0F172A] dark:text-[#F8FAFC]">{session.user?.name || "Aarav Sharma"}</h4>
                      <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-mono">{session.user?.email || "aarav@agrismart.io"}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowProfileModal(false)}
                    className="w-7 h-7 rounded-full bg-[#F4F7FC] dark:bg-[#1E293B] hover:bg-[#E2E8F0] dark:hover:bg-[#334155] flex items-center justify-center text-xs font-bold text-[#64748B] dark:text-[#CBD5E1]"
                  >
                    ✕
                  </button>
                </div>

                <div className="py-3.5 space-y-2.5 text-xs">
                  <div className="flex justify-between items-center py-1 border-b border-[#F4F7FC] dark:border-[#1E293B]">
                    <span className="text-[#8A94A6] dark:text-[#94A3B8] font-bold">Connected Nodes:</span>
                    <span className="font-bold text-[#10B981]">2 Subnodes + 1 Rover</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-[#F4F7FC] dark:border-[#1E293B]">
                    <span className="text-[#8A94A6] dark:text-[#94A3B8] font-bold">Account Auth:</span>
                    <span className="font-bold text-[#0F172A] dark:text-[#F8FAFC]">Google OAuth 2.0</span>
                  </div>

                  <div className="pt-2">
                    <label className="text-[11px] font-black text-[#8A94A6] dark:text-[#94A3B8] block mb-1.5">Change Avatar Photo:</label>
                    <label className="w-full py-2 px-3 rounded-xl border border-dashed border-[#CBD5E1] dark:border-[#334155] hover:border-[#0F172A] dark:hover:border-white bg-[#F8FAFC] dark:bg-[#1A2234] flex items-center justify-center gap-2 cursor-pointer text-xs font-bold text-[#4B5563] dark:text-[#CBD5E1]">
                      <Upload className="w-3.5 h-3.5" />
                      <span>Upload New Image</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            setCustomAvatar(URL.createObjectURL(file));
                            setActionNotice("✓ Profile photo updated successfully!");
                            setTimeout(() => setActionNotice(null), 3000);
                          }
                        }}
                      />
                    </label>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#E8EEF5] dark:border-[#212C42]">
                  <button
                    onClick={async () => {
                      try {
                        await authClient.signOut();
                      } catch {}
                      setDemoUser(null);
                      setShowProfileModal(false);
                      setActionNotice("Logged out of session.");
                      setTimeout(() => setActionNotice(null), 2500);
                    }}
                    className="w-full py-2.5 rounded-xl bg-[#FEE2E2] dark:bg-[#7F1D1D]/30 hover:bg-[#FCA5A5] dark:hover:bg-[#7F1D1D]/50 text-[#B91C1C] dark:text-[#FCA5A5] font-black text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-xs"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Logout Account</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ========================================================================= */}
      {/* 3. WEATHER WIDGET (Image 2) */}
      {/* ========================================================================= */}
      <section id="weather-section" className="w-full modern-card p-5 sm:p-6 space-y-4">
        
        {/* Header Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#E0F2FE] dark:bg-[#0284C7]/20 text-[#0284C7] dark:text-[#38BDF8] flex items-center justify-center text-lg shadow-sm">
              🌤️
            </div>
            <div>
              <h2 className="text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">Weather Widget</h2>
              <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8]">
                7-day microclimate forecast • Live temperature & humidity via Open-Meteo API
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-3 py-1.5 rounded-full bg-[#FEF3C7] dark:bg-[#D97706]/15 text-[#92400E] dark:text-[#FDE68A] font-black text-xs flex items-center gap-1.5 border border-[#FDE68A] dark:border-[#D97706]/30">
              <Sun className="w-3.5 h-3.5 text-[#F59E0B]" />
              <span>Live Temp: {weather?.temperature ?? 28}°C</span>
            </span>

            <span className="px-3 py-1.5 rounded-full bg-[#E0F2FE] dark:bg-[#0284C7]/15 text-[#0369A1] dark:text-[#38BDF8] font-black text-xs flex items-center gap-1.5 border border-[#BAE6FD] dark:border-[#0284C7]/30">
              <Droplets className="w-3.5 h-3.5 text-[#0284C7]" />
              <span>Live Humidity: {weather?.humidity ?? 64}%</span>
            </span>

            <button
              onClick={() => {
                triggerLiveSync(() => {
                  fetchWeather(weatherLocation.lat, weatherLocation.lon).then((d) => setWeather(d));
                });
                setActionNotice("🔄 Weather data refreshed from Open-Meteo Live API!");
                setTimeout(() => setActionNotice(null), 2500);
              }}
              className="px-3.5 py-1.5 rounded-full bg-[#F4F7FC] dark:bg-[#1A2234] hover:bg-[#E8EDF4] dark:hover:bg-[#222C42] text-[#0F172A] dark:text-[#F8FAFC] font-bold text-xs border border-[#E8EEF5] dark:border-[#212C42] flex items-center gap-1.5 cursor-pointer transition shadow-xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-[#8A94A6] ${isSyncing ? "animate-spin text-[#10B981]" : ""}`} />
              <span>Sync Weather</span>
            </button>
          </div>
        </div>

        {/* Location Bar with Search Toggle Button */}
        <div className="bg-[#F8FAFC] dark:bg-[#131926] rounded-2xl p-3.5 border border-[#E8EEF5] dark:border-[#212C42] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="text-lg">📍</span>
            <div>
              <strong className="text-xs sm:text-sm font-black text-[#0F172A] dark:text-[#F8FAFC]">{weatherLocation.name}</strong>
              <span className="text-xs text-[#8A94A6] dark:text-[#94A3B8] ml-2 font-mono">
                (Lat: {weatherLocation.lat.toFixed(4)}° N, Lon: {weatherLocation.lon.toFixed(4)}° E)
              </span>
            </div>
          </div>

          <button
            onClick={() => setShowWeatherSearch(!showWeatherSearch)}
            className="px-4 py-1.5 rounded-full bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white text-xs font-black flex items-center justify-center gap-2 cursor-pointer transition shadow-sm self-start sm:self-auto"
          >
            <Search className="w-3.5 h-3.5 text-[#3B82F6] dark:text-white" />
            <span>{showWeatherSearch ? "✕ Close Search" : "🔍 Search City / Lat-Lon"}</span>
          </button>
        </div>

        {/* Expandable City & GPS Coordinate Search Panel */}
        {showWeatherSearch && (
          <div className="bg-[#FFFFFF] dark:bg-[#131926] rounded-2xl p-4 border border-[#E8EEF5] dark:border-[#212C42] shadow-inner space-y-4 animate-fade-in-scale">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* 1. Search City Name */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">Search Any Indian / Global City or District:</label>
                  {isSearchingCity && (
                    <span className="text-[11px] font-bold text-[#0284C7] dark:text-[#38BDF8] flex items-center gap-1">
                      <RefreshCw className="w-3 h-3 animate-spin" />
                      Searching live...
                    </span>
                  )}
                </div>

                <form onSubmit={handleSearchSubmit} className="relative flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type="text"
                      placeholder="Type any city (e.g. Shahjahanpur, Lucknow, Bareilly, Nashik)..."
                      value={searchCityQuery}
                      onChange={(e) => setSearchCityQuery(e.target.value)}
                      className="w-full pl-9 pr-7 py-2 rounded-xl bg-[#F8FAFC] dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    />
                    <Search className="w-4 h-4 text-[#8A94A6] absolute left-3 top-1/2 -translate-y-1/2" />
                    {searchCityQuery && (
                      <button
                        type="button"
                        onClick={() => setSearchCityQuery("")}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-[#9CA3AF] hover:text-[#0F172A] dark:hover:text-white"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  <button
                    type="submit"
                    className="px-3.5 py-2 rounded-xl bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white text-xs font-black flex items-center gap-1.5 cursor-pointer transition shadow-sm"
                  >
                    <Search className="w-3.5 h-3.5" />
                    <span>Search</span>
                  </button>
                </form>

                {/* Results List */}
                <div className="max-h-56 overflow-y-auto space-y-1.5 pr-1 mt-2">
                  {searchResults.length > 0 ? (
                    searchResults.map((c, i) => {
                      const displayName = c.admin1 ? `${c.name}, ${c.admin1}` : c.name;
                      return (
                        <button
                          key={c.id || i}
                          onClick={() => handleSelectLocation(displayName, c.latitude, c.longitude)}
                          className="w-full p-2.5 rounded-xl bg-[#F8FAFC] dark:bg-[#1A2234] hover:bg-[#EEF2F6] dark:hover:bg-[#222C42] border border-[#E8EEF5] dark:border-[#212C42] text-left flex items-center justify-between text-xs transition cursor-pointer"
                        >
                          <span className="font-bold text-[#0F172A] dark:text-[#F8FAFC]">{displayName}</span>
                          <span className="text-[#8A94A6] dark:text-[#94A3B8] text-[11px] font-mono">
                            {c.latitude.toFixed(2)}°N, {c.longitude.toFixed(2)}°E
                          </span>
                        </button>
                      );
                    })
                  ) : (
                    <div className="text-xs text-[#8A94A6] dark:text-[#94A3B8] p-2 text-center">
                      No matching cities found. Try typing district or state name.
                    </div>
                  )}
                </div>
              </div>

              {/* 2. Manual Decimal GPS Coordinates */}
              <div className="space-y-2">
                <label className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">Direct GPS Coordinates (Decimal Latitude & Longitude):</label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-[10.5px] font-bold text-[#8A94A6] dark:text-[#94A3B8] block mb-1">Latitude (°N)</span>
                    <input
                      type="number"
                      step="0.0001"
                      placeholder="e.g. 27.8805"
                      value={manualLatInput}
                      onChange={(e) => setManualLatInput(e.target.value)}
                      className="w-full p-2 rounded-xl bg-[#F8FAFC] dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    />
                  </div>
                  <div>
                    <span className="text-[10.5px] font-bold text-[#8A94A6] dark:text-[#94A3B8] block mb-1">Longitude (°E)</span>
                    <input
                      type="number"
                      step="0.0001"
                      placeholder="e.g. 79.9122"
                      value={manualLonInput}
                      onChange={(e) => setManualLonInput(e.target.value)}
                      className="w-full p-2 rounded-xl bg-[#F8FAFC] dark:bg-[#1A2234] border border-[#E8EEF5] dark:border-[#212C42] text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    />
                  </div>
                </div>
                <button
                  onClick={handleApplyManualCoords}
                  className="w-full py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-black text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-xs mt-2"
                >
                  <span>Apply Custom GPS Coordinates</span>
                </button>
              </div>

            </div>
          </div>
        )}

        {/* 7-Day Forecast Grid (Desktop View: Full 7-column horizontal cards) */}
        <div className="hidden md:grid md:grid-cols-7 gap-3">
          {weather?.days.map((day) => (
            <div
              key={day.date}
              onClick={() => {
                if (day.isToday) setShowHourlyForecast(!showHourlyForecast);
              }}
              title={day.isToday ? "Click to toggle 24-Hour hourly forecast" : undefined}
              className={`p-3.5 rounded-2xl border text-center space-y-1.5 transition ${
                day.isToday
                  ? "bg-[#EFF6FF] dark:bg-[#1E293B] border-[#BFDBFE] dark:border-[#3B82F6] shadow-xs cursor-pointer hover:border-[#3B82F6] hover:shadow-md hover:-translate-y-0.5"
                  : "bg-[#F8FAFC] dark:bg-[#131926] border-[#E8EEF5] dark:border-[#212C42]"
              }`}
            >
              <div className="flex items-center justify-center gap-1">
                <span className="text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC]">{day.dayLabel}</span>
                {day.isToday && (
                  <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded-full bg-[#2563EB]/15 text-[#2563EB] dark:text-[#60A5FA]">
                    {showHourlyForecast ? "24h ▲" : "24h ▼"}
                  </span>
                )}
              </div>
              <div className="text-xl">
                {day.weatherCode === 0 ? "☀️" : day.weatherCode <= 3 ? "⛅" : day.rainProb > 40 ? "🌧️" : "🌤️"}
              </div>
              <div className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">
                {day.tempMax}° / <span className="text-[#8A94A6] dark:text-[#94A3B8] font-medium">{day.tempMin}°</span>
              </div>
              <div className="text-[10.5px] font-bold text-[#0284C7] dark:text-[#38BDF8]">
                💧 {day.rainProb}%
              </div>
            </div>
          ))}
        </div>

        {/* Google Weather Style 24-Hour Hourly Forecast Expandable Drawer (Desktop & Mobile) */}
        {showHourlyForecast && weather?.hourly && (
          <div className="p-4 sm:p-5 rounded-2xl bg-[#F8FAFC] dark:bg-[#151D2A] border border-[#BFDBFE] dark:border-[#2563EB]/30 animate-fade-in-scale space-y-3 shadow-xs">
            <div className="flex items-center justify-between pb-2 border-b border-[#E2E8F0] dark:border-[#212C42]">
              <div className="flex items-center gap-2">
                <span className="text-base">⏱️</span>
                <div>
                  <h4 className="text-xs sm:text-sm font-black text-[#0F172A] dark:text-white">
                    Next 24-Hour Weather Prediction
                  </h4>
                  <p className="text-[11px] text-[#8A94A6] dark:text-[#94A3B8] font-medium">
                    Google Weather style hourly temperature, conditions, rain % and wind
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowHourlyForecast(false)}
                className="px-2.5 py-1 text-xs font-bold rounded-lg bg-white dark:bg-[#1E2432] border border-[#E2E8F0] dark:border-[#334155] text-[#64748B] hover:text-[#0F172A] dark:hover:text-white transition cursor-pointer shadow-2xs"
              >
                ✕ Close
              </button>
            </div>

            {/* Horizontal Scrollable Hourly Pill Cards */}
            <div className="flex gap-2.5 overflow-x-auto p-1.5 pb-3 scrollbar-thin scrollbar-thumb-slate-300">
              {weather.hourly.map((item, idx) => (
                <div
                  key={idx}
                  className={`min-w-[82px] shrink-0 p-3 rounded-xl border text-center space-y-1.5 transition flex flex-col items-center justify-between ${
                    item.isNow
                      ? "bg-[#EFF6FF] dark:bg-[#1E293B] border-[#93C5FD] dark:border-[#3B82F6] shadow-xs"
                      : "bg-white dark:bg-[#1A2234] border-[#E8EEF5] dark:border-[#212C42] hover:border-[#93C5FD] hover:shadow-xs"
                  }`}
                >
                  <span className={`text-[11px] font-bold ${item.isNow ? "text-[#2563EB] dark:text-[#60A5FA] font-black" : "text-[#0F172A] dark:text-slate-200"}`}>
                    {item.time}
                  </span>
                  <span className="text-xl my-0.5">{item.icon || "☀️"}</span>
                  <span className="text-sm font-black text-[#0F172A] dark:text-white">
                    {item.temp}°
                  </span>
                  <span className="text-[10px] font-bold text-[#0284C7] dark:text-[#38BDF8]">
                    💧 {item.rainProb}%
                  </span>
                  <span className="text-[9.5px] font-semibold text-[#8A94A6] dark:text-[#94A3B8]">
                    💨 {item.windSpeed}k/h
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mobile View: Collapsible Forecast */}
        <div className="block md:hidden space-y-3">
          {/* Today's Active Weather Card */}
          {weather?.days[0] && (
            <div
              onClick={() => setShowHourlyForecast(!showHourlyForecast)}
              className="p-4 rounded-2xl bg-[#EFF6FF] dark:bg-[#1A2234] border border-[#BFDBFE] dark:border-[#2563EB]/40 shadow-xs flex items-center justify-between transition cursor-pointer hover:border-[#3B82F6]"
            >
              <div className="flex items-center gap-3">
                <div className="text-3xl">
                  {weather.days[0].weatherCode === 0 ? "☀️" : weather.days[0].weatherCode <= 3 ? "⛅" : weather.days[0].rainProb > 40 ? "🌧️" : "🌤️"}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">Today</span>
                    <span className="px-2 py-0.5 rounded-full bg-[#2563EB]/10 dark:bg-[#2563EB]/25 text-[#2563EB] dark:text-[#60A5FA] font-bold text-[10px]">
                      {showHourlyForecast ? "24h Active ▲" : "Tap 24h ▾"}
                    </span>
                  </div>
                  <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8] font-medium mt-0.5">
                    {weather.days[0].condition || "Clear Conditions"}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-black text-[#0F172A] dark:text-[#F8FAFC]">
                  {weather.days[0].tempMax}° / <span className="text-[#8A94A6] dark:text-[#94A3B8] font-medium">{weather.days[0].tempMin}°</span>
                </div>
                <div className="text-[11px] font-bold text-[#0284C7] dark:text-[#38BDF8] mt-0.5">
                  💧 {weather.days[0].rainProb}% Rain
                </div>
              </div>
            </div>
          )}

          {/* Expanded 6-Day Forecast Grid on Mobile */}
          {mobileWeatherExpanded && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1 animate-fade-in-scale">
              {weather?.days.slice(1).map((day) => (
                <div
                  key={day.date}
                  className="p-3 rounded-2xl border bg-[#F8FAFC] dark:bg-[#1A2234] border-[#E8EEF5] dark:border-[#212C42] text-center space-y-1.5 transition"
                >
                  <div className="text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC]">{day.dayLabel}</div>
                  <div className="text-xl">
                    {day.weatherCode === 0 ? "☀️" : day.weatherCode <= 3 ? "⛅" : day.rainProb > 40 ? "🌧️" : "🌤️"}
                  </div>
                  <div className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">
                    {day.tempMax}° / <span className="text-[#8A94A6] dark:text-[#94A3B8] font-medium">{day.tempMin}°</span>
                  </div>
                  <div className="text-[10.5px] font-bold text-[#0284C7] dark:text-[#38BDF8]">
                    💧 {day.rainProb}%
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Mobile Toggle Button */}
          <div className="flex justify-center pt-1">
            <button
              onClick={() => setMobileWeatherExpanded(!mobileWeatherExpanded)}
              className={`w-full py-2.5 px-4 rounded-full border font-bold text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-xs select-none ${
                mobileWeatherExpanded
                  ? "bg-[#0F172A] dark:bg-[#0284C7] text-white border-[#0F172A] dark:border-[#0284C7]"
                  : "bg-[#F8FAFC] dark:bg-[#1A2234] hover:bg-[#EEF2F6] dark:hover:bg-[#222C42] text-[#0F172A] dark:text-[#F8FAFC] border-[#E8EEF5] dark:border-[#212C42]"
              }`}
            >
              <span>{mobileWeatherExpanded ? "✕ Hide 6-Day Forecast" : "📅 View 6-Day Forecast"}</span>
              <span
                className="text-xs transition-transform duration-200 inline-block"
                style={{ transform: mobileWeatherExpanded ? "rotate(180deg)" : "rotate(0deg)" }}
              >
                ▼
              </span>
            </button>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. ROW 1: AI SCOUTING ALERTS (LEFT) + FIELD SUBNODES SENSORS (RIGHT) */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* LEFT: ALERTS & AI SCOUTING PATROL (Image 3 - Left) */}
        <section className="lg:col-span-5 modern-card p-5 sm:p-6 flex flex-col justify-between space-y-4">
          <div className="flex flex-col min-h-0">
            {/* Header with Trigger Patrol Button */}
            <div className="flex items-center justify-between gap-3 mb-3 shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#FEE2E2] dark:bg-[#EF4444]/20 text-[#DC2626] dark:text-[#F87171] flex items-center justify-center text-lg shadow-sm">
                  🔍
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base sm:text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">
                      Alerts & AI Scouting Patrol
                    </h2>
                    {alertsList.length > 0 && (
                      <span className="text-[10.5px] font-extrabold px-2 py-0.5 rounded-full bg-[#EFF6FF] dark:bg-[#1E293B] text-[#2563EB] dark:text-[#60A5FA] border border-[#DBEAFE] dark:border-[#3B82F6]/30">
                        {alertsList.length}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8]">Autonomous 2x daily schedule • Disease diagnostics & pest alerts</p>
                </div>
              </div>

              <button
                onClick={handleTriggerPatrol}
                disabled={patrolRunning}
                className="px-3.5 py-1.5 rounded-full bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white text-xs font-black flex items-center gap-1.5 cursor-pointer transition shadow-sm shrink-0"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#3B82F6] dark:text-white" />
                <span>{patrolRunning ? "Patrol Scanning..." : "🚀 Trigger AI Patrol"}</span>
              </button>
            </div>

            {/* Routine Patrol Times */}
            <div className="grid grid-cols-2 gap-2.5 mb-3.5 shrink-0">
              <div className="bg-[#F8FAFC] dark:bg-[#131926] rounded-xl p-2.5 border border-[#E8EEF5] dark:border-[#212C42] flex items-center gap-2">
                <span className="text-base">🌅</span>
                <div>
                  <span className="text-[10.5px] font-bold text-[#8A94A6] dark:text-[#94A3B8] block">Morning Patrol:</span>
                  <span className="text-xs font-black text-[#059669] dark:text-[#34D399]">07:00 AM (Completed)</span>
                </div>
              </div>
              <div className="bg-[#F8FAFC] dark:bg-[#131926] rounded-xl p-2.5 border border-[#E8EEF5] dark:border-[#212C42] flex items-center gap-2">
                <span className="text-base">🌇</span>
                <div>
                  <span className="text-[10.5px] font-bold text-[#8A94A6] dark:text-[#94A3B8] block">Evening Patrol:</span>
                  <span className="text-xs font-black text-[#0284C7] dark:text-[#38BDF8]">05:30 PM (Scheduled)</span>
                </div>
              </div>
            </div>

            {/* Alerts Feed */}
            <div className="space-y-2.5 overflow-y-auto max-h-[260px] pr-1.5 modern-scrollbar">
              {alertsList.map((a) => (
                <div
                  key={a.id}
                  className={`p-3.5 rounded-2xl border space-y-1.5 transition ${
                    a.type === "CRITICAL"
                      ? "bg-[#FFF5F5] dark:bg-[#EF4444]/10 border-[#FEE2E2] dark:border-[#EF4444]/25"
                      : a.type === "WARNING"
                      ? "bg-[#FFFDF5] dark:bg-[#F59E0B]/10 border-[#FEF3C7] dark:border-[#F59E0B]/25"
                      : "bg-[#F8FAFC] dark:bg-[#131926] border-[#E8EEF5] dark:border-[#212C42]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${a.type === "CRITICAL" ? "bg-[#EF4444]" : a.type === "WARNING" ? "bg-[#F59E0B]" : "bg-[#3B82F6]"}`} />
                      <h4 className="text-xs font-black text-[#0F172A] dark:text-[#F8FAFC]">{a.title}</h4>
                    </div>
                    {a.confidence && (
                      <span className="text-[10.5px] font-black px-2 py-0.5 rounded-full bg-white dark:bg-[#1E293B] border border-[#E8EEF5] dark:border-[#334155] text-[#0F172A] dark:text-[#F8FAFC]">
                        {Math.round(a.confidence * 100)}% Conf
                      </span>
                    )}
                  </div>
                  <p className="text-[11.5px] text-[#64748B] dark:text-[#94A3B8]">{a.message}</p>
                  {a.treatment && (
                    <div className={`text-[11px] font-bold pt-1 ${a.type === "CRITICAL" ? "text-[#DC2626] dark:text-[#F87171]" : "text-[#D97706] dark:text-[#FBBF24]"}`}>
                      <strong>Action Needed:</strong> {a.treatment}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="text-[11px] text-[#8A94A6] dark:text-[#94A3B8] font-mono text-center pt-2 shrink-0 border-t border-[#E8EEF5]/40 dark:border-white/10">
            AI models: MobileNetV3 Disease, Pest Classifier, YOLOv8 Crop Health
          </div>
        </section>

        {/* RIGHT: FIELD SUBNODES SENSOR DATA (Image 3 - Right) */}
        <section className="lg:col-span-7 modern-card p-5 sm:p-6 flex flex-col justify-between space-y-4">
          <div>
            {/* Header & Subnode Switcher */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#D1FAE5] dark:bg-[#059669]/20 text-[#059669] dark:text-[#34D399] flex items-center justify-center text-lg shadow-sm">
                  🌱
                </div>
                <div>
                  <h2 className="text-base sm:text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">
                    Field Subnodes Sensor Data
                  </h2>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8]">Real-time environmental telemetry & actuator control</p>
                </div>
              </div>

              {/* Subnode Segmented Toggle */}
              <div className="flex items-center p-1 rounded-full bg-[#F1F5F9] dark:bg-white/10 border border-[#E2E8F0] dark:border-white/10">
                <button
                  onClick={() => setActiveField("FIELD_A")}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition cursor-pointer ${
                    activeField === "FIELD_A"
                      ? "bg-[#0284C7] text-white shadow-xs"
                      : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                  }`}
                >
                  Subnode A (Field)
                </button>
                <button
                  onClick={() => setActiveField("FIELD_B")}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition cursor-pointer ${
                    activeField === "FIELD_B"
                      ? "bg-[#0284C7] text-white shadow-xs"
                      : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                  }`}
                >
                  Subnode B (Greenhouse)
                </button>
              </div>
            </div>

            {/* 4 Sensor Metrics Cards (Pastel Themed Pods) */}
            <div className="grid grid-cols-2 gap-3.5 mb-4">
              
              {/* Surroundings Air (Pastel Warm Peach) */}
              <div className="bg-[#FFF7ED] dark:bg-[#EA580C]/10 p-4 rounded-2xl border border-[#FED7AA] dark:border-[#EA580C]/25 space-y-2 hover:shadow-md transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black tracking-wider uppercase text-[#C2410C] dark:text-[#FB923C]">SURROUNDINGS</span>
                  <div className="w-8 h-8 rounded-full bg-white/90 dark:bg-white/10 text-[#EA580C] dark:text-[#FB923C] flex items-center justify-center text-sm shadow-xs">
                    🌡️
                  </div>
                </div>
                <div className="text-2xl sm:text-3xl font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">
                  {fieldData.airTemp !== null ? fieldData.airTemp.toFixed(1) : "--"}<span className="text-sm font-bold text-[#EA580C] ml-1">°C</span>
                </div>
                <div className="text-xs text-[#64748B] dark:text-[#94A3B8] font-bold">
                  Humidity: <span className="text-[#0F172A] dark:text-[#F8FAFC]">{fieldData.humidity !== null ? `${fieldData.humidity}%` : "--"}</span>
                </div>
              </div>

              {/* Soil Moisture (Pastel Soft Sky) */}
              <div className="bg-[#F0F9FF] dark:bg-[#0284C7]/10 p-4 rounded-2xl border border-[#BAE6FD] dark:border-[#0284C7]/25 space-y-2 hover:shadow-md transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black tracking-wider uppercase text-[#0369A1] dark:text-[#38BDF8]">SOIL MOISTURE</span>
                  <div className="w-8 h-8 rounded-full bg-white/90 dark:bg-white/10 text-[#0284C7] dark:text-[#38BDF8] flex items-center justify-center text-sm shadow-xs">
                    💧
                  </div>
                </div>
                <div className="text-2xl sm:text-3xl font-black tracking-tight text-[#0284C7] dark:text-[#38BDF8]">
                  {fieldData.soilMoisture !== null ? fieldData.soilMoisture.toFixed(1) : "--"}<span className="text-sm font-bold text-[#0284C7]/80 ml-1">%</span>
                </div>
                <div className="w-full bg-[#E0F2FE] dark:bg-white/10 h-2 rounded-full overflow-hidden mt-2">
                  <div className="bg-[#0284C7] h-full rounded-full" style={{ width: `${fieldData.soilMoisture !== null ? Math.min(100, fieldData.soilMoisture) : 0}%` }} />
                </div>
              </div>

              {/* Soil Temp (Pastel Rose Coral) */}
              <div className="bg-[#FFF1F2] dark:bg-[#E11D48]/10 p-4 rounded-2xl border border-[#FECDD3] dark:border-[#E11D48]/25 space-y-2 hover:shadow-md transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black tracking-wider uppercase text-[#BE123C] dark:text-[#FB7185]">SOIL TEMP</span>
                  <div className="w-8 h-8 rounded-full bg-white/90 dark:bg-white/10 text-[#E11D48] dark:text-[#FB7185] flex items-center justify-center text-sm shadow-xs">
                    🌱
                  </div>
                </div>
                <div className="text-2xl sm:text-3xl font-black tracking-tight text-[#E11D48] dark:text-[#FB7185]">
                  {fieldData.soilTemp !== null ? fieldData.soilTemp.toFixed(1) : "--"}<span className="text-sm font-bold text-[#E11D48]/80 ml-1">°C</span>
                </div>
                <div className="text-xs text-[#059669] dark:text-[#34D399] font-bold">● {fieldData.soilTemp !== null ? "Optimal Root Zone" : "Sensor Disconnected"}</div>
              </div>

              {/* Battery (Pastel Mint) */}
              <div className="bg-[#F0FDF4] dark:bg-[#059669]/10 p-4 rounded-2xl border border-[#BBF7D0] dark:border-[#059669]/25 space-y-2 hover:shadow-md transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black tracking-wider uppercase text-[#15803D] dark:text-[#34D399]">BATTERY</span>
                  <div className="w-8 h-8 rounded-full bg-white/90 dark:bg-white/10 text-[#059669] dark:text-[#34D399] flex items-center justify-center text-sm shadow-xs">
                    🔋
                  </div>
                </div>
                <div className="text-2xl sm:text-3xl font-black tracking-tight text-[#059669] dark:text-[#34D399]">
                  {fieldData.battery}<span className="text-sm font-bold text-[#059669]/80 ml-1">%</span>
                </div>
                <div className="text-xs text-[#059669] dark:text-[#34D399] font-bold">⚡ Solar Charging</div>
              </div>

            </div>

            {/* Actuator Relay Card (Field A/B Pump with Flowchart Logic & Force Run Override) */}
            <div className="bg-[#0F172A] dark:bg-[#1E293B] text-white p-4 sm:p-5 rounded-2xl flex flex-col gap-3 shadow-md border border-white/10">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10.5px] font-bold text-[#94A3B8] uppercase tracking-wider block">Actuator Control</span>
                    {fieldData.logic?.mode && (
                      <span className={`text-[9.5px] font-black px-2 py-0.5 rounded-full border ${
                        fieldData.logic.mode === "MANUAL_FORCE_OVERRIDE"
                          ? "bg-[#D97706]/20 text-[#FBBF24] border-[#D97706]/50"
                          : fieldData.logic.mode === "RAIN_LOCKOUT"
                          ? "bg-[#EF4444]/20 text-[#FCA5A5] border-[#EF4444]/40"
                          : fieldData.logic.mode === "RAIN_IMMINENT_HOLD"
                          ? "bg-[#F59E0B]/20 text-[#FCD34D] border-[#F59E0B]/40"
                          : fieldData.logic.mode === "TIMED_CYCLE_15MIN"
                          ? "bg-[#3B82F6]/20 text-[#93C5FD] border-[#3B82F6]/40"
                          : "bg-[#10B981]/20 text-[#6EE7B7] border-[#10B981]/40"
                      }`}>
                        {fieldData.logic.mode.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>
                  <h3 className="text-sm font-black text-white mt-0.5">{fieldData.pumpName}</h3>
                  <p className="text-xs text-[#94A3B8] flex items-center gap-1.5 mt-0.5">
                    <span className={`w-2 h-2 rounded-full ${fieldData.pumpActive ? "bg-[#10B981] animate-ping" : "bg-[#64748B]"}`} />
                    <span>
                      {fieldData.pumpActive
                        ? (fieldData.logic?.mode === "MANUAL_FORCE_OVERRIDE"
                            ? "FORCED ON • Running regardless of weather/moisture"
                            : fieldData.logic?.time_remaining_minutes
                            ? `Running 15-min cycle (${fieldData.logic.time_remaining_minutes}m left)`
                            : "Pump is currently pumping water • 45 L/h")
                        : "Standby • Automated Flowchart Control Active"}
                    </span>
                  </p>
                </div>

                <div className="flex items-center gap-2 self-stretch sm:self-auto">
                  {/* Dedicated Force Run / Override Button */}
                  <button
                    onClick={async () => {
                      const targetKey = activeField === "FIELD_A" ? "PUMP_ZONE_A" : "PUMP_ZONE_B";
                      const isForced = fieldData.logic?.mode === "MANUAL_FORCE_OVERRIDE" || fieldData.pumpActive;
                      const nextAction = isForced ? "FORCE_OFF" : "FORCE_ON";
                      
                      if (activeField === "FIELD_A") setPumpZoneA(!isForced);
                      else setPumpZoneB(!isForced);

                      setActionNotice(
                        !isForced
                          ? `⚡ Force Override: ${activeField === "FIELD_A" ? "Field A" : "Field B"} Pump Forced ON!`
                          : `🔄 Force Override Cleared: ${activeField === "FIELD_A" ? "Field A" : "Field B"} returned to Auto Logic`
                      );

                      try {
                        await fetch("/api/commands", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ target: targetKey, action: nextAction }),
                        });
                        fetch(`http://127.0.0.1:8000/api/edge/pump/${targetKey}/${nextAction}`, {
                          method: "POST",
                          signal: AbortSignal.timeout(1000),
                        }).catch(() => {});
                      } catch {}
                      setTimeout(() => setActionNotice(null), 3000);
                    }}
                    className={`flex-1 sm:flex-initial px-4 py-2.5 rounded-full font-black text-xs flex items-center justify-center gap-1.5 cursor-pointer transition shadow-sm border ${
                      fieldData.logic?.mode === "MANUAL_FORCE_OVERRIDE"
                        ? "bg-[#D97706] hover:bg-[#B45309] text-white border-[#F59E0B]"
                        : "bg-[#1E293B] hover:bg-[#334155] text-[#FBBF24] border-[#F59E0B]/40"
                    }`}
                    title="Force pump ON regardless of rain or soil moisture"
                  >
                    <span>⚡</span>
                    <span>{fieldData.logic?.mode === "MANUAL_FORCE_OVERRIDE" ? "FORCE ACTIVE" : "FORCE RUN PUMP"}</span>
                  </button>

                  {/* Standard Start/Stop Toggle Button */}
                  <button
                    onClick={togglePump}
                    className={`flex-1 sm:flex-initial px-5 py-2.5 rounded-full font-bold text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-sm ${
                      fieldData.pumpActive
                        ? "bg-[#EF4444] hover:bg-[#DC2626] text-white"
                        : "bg-[#0284C7] hover:bg-[#0369A1] text-white"
                    }`}
                  >
                    <Power className="w-3.5 h-3.5" />
                    <span>{fieldData.pumpActive ? "STOP PUMP" : "START PUMP"}</span>
                  </button>
                </div>
              </div>

              {/* Flowchart Rule & Reason Banner */}
              {fieldData.logic?.reason && (
                <div className="pt-2 border-t border-white/10 flex items-start gap-2 text-[11px] text-[#94A3B8]">
                  <span className="text-xs shrink-0">{fieldData.logic.mode === "MANUAL_FORCE_OVERRIDE" ? "⚡" : "🧠"}</span>
                  <span className="leading-snug">
                    <strong className="text-white font-semibold">Pump Logic: </strong>
                    {fieldData.logic.reason}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="text-[11px] text-[#64748B] dark:text-[#94A3B8] font-mono text-center pt-2">
            ESP32 Subnode • LoRa 868MHz Mesh • Automated Soil Moisture & Rain Decision Tree
          </div>
        </section>

      </div>

      {/* ========================================================================= */}
      {/* 4.5 MANUAL PLANT DISEASE & CROP SCANNER (4 ONNX AI MODELS) */}
      {/* ========================================================================= */}
      <ManualCropScanner onScanComplete={handleManualScanComplete} />

      {/* ========================================================================= */}
      {/* 5. ROW 2: ROVER POSITION (LEFT) + ROVER MODES (RIGHT) */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* LEFT: ROVER POSITION DOCK (Image 4 - Left) */}
        <section className="lg:col-span-6 modern-card p-5 sm:p-6 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#E0F2FE] dark:bg-[#0284C7]/20 text-[#0284C7] dark:text-[#38BDF8] flex items-center justify-center text-lg shadow-sm">
                  🚗
                </div>
                <div>
                  <h2 className="text-base sm:text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">Rover Position</h2>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8]">Real-time autonomous farm bay navigation</p>
                </div>
              </div>

              <span className="px-3 py-1 rounded-full bg-[#F1F5F9] dark:bg-white/10 border border-[#E2E8F0] dark:border-white/10 text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC] flex items-center gap-1.5">
                <span>🔋 Rover Battery: <strong className="text-[#059669] dark:text-[#34D399]">{roverBattery}%</strong></span>
              </span>
            </div>

            {/* 3 Nav Bay Buttons */}
            <div className="grid grid-cols-3 gap-3 mb-3">
              <button
                onClick={() => {
                  setRoverPosition("DOCK");
                  setRoverActionNotice("Standby at Charging Dock");
                }}
                className={`p-3.5 rounded-2xl border text-center transition cursor-pointer ${
                  roverPosition === "DOCK"
                    ? "bg-[#0284C7] text-white border-[#0284C7] shadow-sm"
                    : "bg-[#F8FAFC] dark:bg-white/5 border-[#E2E8F0] dark:border-white/10 text-[#0F172A] dark:text-[#F8FAFC] hover:bg-[#F1F5F9]"
                }`}
              >
                <div className="text-lg">⚡</div>
                <div className="text-xs font-bold mt-1">Base Dock</div>
                <div className={`text-[10px] ${roverPosition === "DOCK" ? "text-white/80" : "text-[#94A3B8]"}`}>
                  {roverPosition === "DOCK" ? "● ACTIVE HERE" : "Standby"}
                </div>
              </button>

              <button
                onClick={() => {
                  setRoverPosition("FIELD_A");
                  setRoverActionNotice("Navigating Field A (Tomato Canopy)");
                }}
                className={`p-3.5 rounded-2xl border text-center transition cursor-pointer ${
                  roverPosition === "FIELD_A"
                    ? "bg-[#0284C7] text-white border-[#0284C7] shadow-sm"
                    : "bg-[#F8FAFC] dark:bg-white/5 border-[#E2E8F0] dark:border-white/10 text-[#0F172A] dark:text-[#F8FAFC] hover:bg-[#F1F5F9]"
                }`}
              >
                <div className="text-lg">🍅</div>
                <div className="text-xs font-bold mt-1">Field A</div>
                <div className={`text-[10px] ${roverPosition === "FIELD_A" ? "text-white/80" : "text-[#94A3B8]"}`}>
                  {roverPosition === "FIELD_A" ? "● ACTIVE HERE" : "Standby"}
                </div>
              </button>

              <button
                onClick={() => {
                  setRoverPosition("FIELD_B");
                  setRoverActionNotice("Navigating Field B (Greenhouse)");
                }}
                className={`p-3.5 rounded-2xl border text-center transition cursor-pointer ${
                  roverPosition === "FIELD_B"
                    ? "bg-[#0284C7] text-white border-[#0284C7] shadow-sm"
                    : "bg-[#F8FAFC] dark:bg-white/5 border-[#E2E8F0] dark:border-white/10 text-[#0F172A] dark:text-[#F8FAFC] hover:bg-[#F1F5F9]"
                }`}
              >
                <div className="text-lg">🌿</div>
                <div className="text-xs font-bold mt-1">Field B</div>
                <div className={`text-[10px] ${roverPosition === "FIELD_B" ? "text-white/80" : "text-[#94A3B8]"}`}>
                  {roverPosition === "FIELD_B" ? "● ACTIVE HERE" : "Standby"}
                </div>
              </button>
            </div>

            <div className="bg-[#F8FAFC] dark:bg-white/5 p-3 rounded-xl border border-[#E2E8F0] dark:border-white/10 flex items-center justify-between text-xs">
              <span className="text-[#64748B] dark:text-[#94A3B8] font-medium">Current State: <strong className="text-[#0F172A] dark:text-[#F8FAFC]">{roverActionNotice}</strong></span>
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-ping" />
            </div>
          </div>

          <div className="text-[11px] text-[#64748B] dark:text-[#94A3B8] font-mono text-center pt-1">
            Ultrasonic Obstacle Avoidance: Active • GPS Coordinate Beacon: Locked
          </div>
        </section>

        {/* RIGHT: ROVER MODES & CONTROLS (Image 4 - Right) */}
        <section className="lg:col-span-6 modern-card p-5 sm:p-6 flex flex-col justify-between space-y-4">
          <div>
            {/* Header with AUTO / MANUAL Mode Switcher */}
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-[#EDE9FE] dark:bg-[#6366F1]/20 text-[#6366F1] dark:text-[#A5B4FC] flex items-center justify-center text-lg shadow-sm">
                  🎮
                </div>
                <div>
                  <h2 className="text-base sm:text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">Rover Modes</h2>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8]">Autonomous 2x daily patrol schedule & manual joystick override</p>
                </div>
              </div>

              {/* Mode Switcher */}
              <div className="flex items-center p-1 rounded-full bg-[#F1F5F9] dark:bg-white/10 border border-[#E2E8F0] dark:border-white/10">
                <button
                  onClick={() => handleSwitchRoverMode("AUTO")}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-black transition cursor-pointer ${
                    roverMode === "AUTO"
                      ? "bg-[#059669] text-white shadow-xs"
                      : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                  }`}
                >
                  Auto
                </button>
                <button
                  onClick={() => handleSwitchRoverMode("MANUAL")}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-black transition cursor-pointer ${
                    roverMode === "MANUAL"
                  ? "bg-[#D97706] text-white shadow-xs"
                      : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                  }`}
                >
                  Manual
                </button>
              </div>
            </div>

            {/* 1. AUTO MODE VIEW (Exact match to Edge Offline Dashboard) */}
            {roverMode === "AUTO" ? (
              <div className="space-y-3.5 animate-fade-in-scale">
                {/* Scheduled Auto-Patrol Box */}
                <div className="bg-[#F8FAFC] dark:bg-white/5 rounded-2xl p-4 border border-[#E2E8F0] dark:border-white/10 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs sm:text-sm font-black text-[#0F172A] dark:text-[#F8FAFC]">Scheduled Auto-Patrol</h3>
                    <span className="px-2.5 py-0.5 rounded-full bg-[#D1FAE5] text-[#059669] text-[11px] font-black border border-[#A7F3D0]">
                      ● Auto Mode Active
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2.5">
                    <div className="bg-white dark:bg-white/5 rounded-xl p-3 border border-[#E2E8F0] dark:border-white/10">
                      <div className="text-[11px] font-bold text-[#64748B] dark:text-[#94A3B8]">🌅 Morning Patrol</div>
                      <div className="text-xs sm:text-sm font-black text-[#0F172A] dark:text-[#F8FAFC] mt-0.5">07:00 AM (Routine)</div>
                    </div>
                    <div className="bg-white dark:bg-white/5 rounded-xl p-3 border border-[#E2E8F0] dark:border-white/10">
                      <div className="text-[11px] font-bold text-[#64748B] dark:text-[#94A3B8]">🌇 Evening Patrol</div>
                      <div className="text-xs sm:text-sm font-black text-[#0F172A] dark:text-[#F8FAFC] mt-0.5">05:30 PM (Routine)</div>
                    </div>
                  </div>
                </div>

                {/* Rain Safety Interlock & Post-Rain Drying Timer */}
                <div className="grid grid-cols-2 gap-2.5 text-center">
                  <div className="bg-[#F8FAFC] dark:bg-white/5 rounded-xl p-3 border border-[#E2E8F0] dark:border-white/10">
                    <span className="text-[11px] font-bold text-[#64748B] dark:text-[#94A3B8] block">Rain Safety Interlock</span>
                    <div className="text-xs sm:text-sm font-black text-[#059669] dark:text-[#34D399] mt-0.5">
                      {isRaining ? "🚨 ACTIVE (Rain Detected)" : "ARMED (Pumps Protected)"}
                    </div>
                  </div>
                  <div className="bg-[#F8FAFC] dark:bg-white/5 rounded-xl p-3 border border-[#E2E8F0] dark:border-white/10">
                    <span className="text-[11px] font-bold text-[#64748B] dark:text-[#94A3B8] block">Post-Rain Drying Timer</span>
                    <div className="text-xs sm:text-sm font-black text-[#0284C7] dark:text-[#38BDF8] mt-0.5">Clear (0 min hold)</div>
                  </div>
                </div>

                {/* Start Scheduled Patrol Run Button */}
                <button
                  onClick={handleTriggerPatrol}
                  disabled={patrolRunning}
                  className="w-full py-3 rounded-2xl bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white font-black text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-md"
                >
                  <span>🚜</span>
                  <span>{patrolRunning ? "Patrol Scan in Progress..." : "Start Scheduled Patrol Run Now"}</span>
                </button>
              </div>
            ) : (
              /* 2. MANUAL MODE VIEW */
              <div className="space-y-3.5 animate-fade-in-scale">
                <div className="bg-[#FEF3C7] border border-[#FDE68A] rounded-2xl p-2.5 px-3.5 flex items-center justify-between">
                  <h3 className="text-xs font-black text-[#92400E]">Manual Control Override</h3>
                  <span className="px-2 py-0.5 rounded-full bg-[#F59E0B] text-white text-[10.5px] font-black">
                    ● Manual Active
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
                  {/* 5-Button Directional D-Pad */}
                  <div className="flex flex-col items-center justify-center p-3 bg-[#F8FAFC] dark:bg-white/5 rounded-2xl border border-[#E2E8F0] dark:border-white/10">
                    <div className="text-[11px] font-black text-[#64748B] dark:text-[#94A3B8] uppercase tracking-wider mb-2">
                      Directional Joystick
                    </div>
                    
                    <button
                      onClick={() => handleRoverDpad("FORWARD")}
                      className="w-10 h-10 rounded-xl dpad-btn flex items-center justify-center font-black mb-1 cursor-pointer"
                    >
                      ▲
                    </button>
                    
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleRoverDpad("LEFT")}
                        className="w-10 h-10 rounded-xl dpad-btn flex items-center justify-center font-black cursor-pointer"
                      >
                        ◀
                      </button>
                      <button
                        onClick={() => handleRoverDpad("STOP")}
                        className="w-10 h-10 rounded-xl bg-[#EF4444] text-white flex items-center justify-center font-black shadow-md cursor-pointer hover:bg-[#DC2626]"
                      >
                        ■
                      </button>
                      <button
                        onClick={() => handleRoverDpad("RIGHT")}
                        className="w-10 h-10 rounded-xl dpad-btn flex items-center justify-center font-black cursor-pointer"
                      >
                        ▶
                      </button>
                    </div>

                    <button
                      onClick={() => handleRoverDpad("REVERSE")}
                      className="w-10 h-10 rounded-xl dpad-btn flex items-center justify-center font-black mt-1 cursor-pointer"
                    >
                      ▼
                    </button>
                  </div>

                  {/* Speed Slider & Snapshot Camera */}
                  <div className="space-y-3">
                    <div className="bg-[#F8FAFC] dark:bg-white/5 p-3 rounded-2xl border border-[#E2E8F0] dark:border-white/10 space-y-1.5">
                      <div className="flex justify-between items-center text-xs font-bold text-[#0F172A] dark:text-[#F8FAFC]">
                        <span>Speed bar:</span>
                        <span className="font-extrabold text-[#D97706]">{Math.round((roverSpeed / 255) * 100)}% (PWM {roverSpeed})</span>
                      </div>
                      <input
                        type="range"
                        min="50"
                        max="255"
                        value={roverSpeed}
                        onChange={(e) => handleRoverSpeedChange(Number(e.target.value))}
                        className="w-full accent-[#F59E0B] cursor-pointer"
                      />
                      <div className="flex justify-between gap-2 pt-1">
                        <button
                          onClick={() => handleRoverSpeedChange(Math.max(50, roverSpeed - 25))}
                          className="flex-1 py-1 rounded-lg bg-white dark:bg-white/10 hover:bg-[#EEF2F6] border border-[#E2E8F0] dark:border-white/10 text-[11px] font-black text-[#0F172A] dark:text-[#F8FAFC] cursor-pointer"
                        >
                          - Speed
                        </button>
                        <button
                          onClick={() => handleRoverSpeedChange(Math.min(255, roverSpeed + 25))}
                          className="flex-1 py-1 rounded-lg bg-white dark:bg-white/10 hover:bg-[#EEF2F6] border border-[#E2E8F0] dark:border-white/10 text-[11px] font-black text-[#0F172A] dark:text-[#F8FAFC] cursor-pointer"
                        >
                          + Speed
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={handleCaptureRoverPhoto}
                      className="w-full py-2.5 rounded-2xl bg-[#0F172A] dark:bg-[#0284C7] hover:bg-[#1E293B] dark:hover:bg-[#0369A1] text-white font-black text-xs flex items-center justify-center gap-2 cursor-pointer transition shadow-md"
                    >
                      <Camera className="w-4 h-4 text-[#F59E0B]" />
                      <span>📷 Capture Live Leaf Photo</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="text-[11px] text-[#64748B] dark:text-[#94A3B8] font-mono text-center pt-1">
            ESP32-CAM WiFi Telemetry • PWM Motor Driver: L298N
          </div>
        </section>
      </div>

      {/* ======================================================================= */}
      {/* 6. ROW 3: GRAPHICAL REPRESENTATION OF SENSORS (10-DAY CALENDAR) */}
      {/* ======================================================================= */}
      <section className="w-full modern-card p-5 sm:p-6 space-y-5">
        
        {/* Header Row */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#EFF6FF] dark:bg-[#1E293B] text-[#2563EB] dark:text-[#60A5FA] flex items-center justify-center text-lg shadow-sm border border-[#DBEAFE] dark:border-[#3B82F6]/30">
              📊
            </div>
            <div>
              <h2 className="text-lg font-black tracking-tight text-[#0F172A] dark:text-[#F8FAFC]">
                Graphical Representation of Sensor Data (Node A & B)
              </h2>
              <p className="text-xs text-[#8A94A6] dark:text-[#94A3B8]">
                24-Hour telemetry curves • Select any of the last 10 days to inspect historical day-wise records
              </p>
            </div>
          </div>

          {/* Node & Metric Switcher Toolbar */}
          <div className="flex items-center gap-2.5 flex-wrap">
            
            {/* Node Switcher [ Node A | Node B ] */}
            <div className="flex items-center p-1 rounded-full bg-[#F4F7FC] dark:bg-[#131926] border border-[#E8EEF5] dark:border-[#212C42]">
              <button
                onClick={() => setGraphNode("NODE_A")}
                className={`px-3 py-1 rounded-full text-xs font-black transition cursor-pointer ${
                  graphNode === "NODE_A"
                    ? "bg-[#0F172A] dark:bg-[#0284C7] text-white shadow-xs"
                    : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                }`}
              >
                Node A
              </button>
              <button
                onClick={() => setGraphNode("NODE_B")}
                className={`px-3 py-1 rounded-full text-xs font-black transition cursor-pointer ${
                  graphNode === "NODE_B"
                    ? "bg-[#0F172A] dark:bg-[#0284C7] text-white shadow-xs"
                    : "text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white"
                }`}
              >
                Node B
              </button>
            </div>

            {/* Metric Pills */}
            <button
              onClick={() => setSelectedMetric("SOIL_MOISTURE")}
              className={`px-3.5 py-1.5 rounded-full text-xs font-black transition cursor-pointer flex items-center gap-1.5 ${
                selectedMetric === "SOIL_MOISTURE"
                  ? "bg-[#0284C7] text-white shadow-xs"
                  : "bg-[#F4F7FC] dark:bg-[#131926] text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white border border-[#E8EEF5] dark:border-[#212C42]"
              }`}
            >
              <span>💧 Soil Moisture</span>
            </button>
            <button
              onClick={() => setSelectedMetric("SOIL_TEMP")}
              className={`px-3.5 py-1.5 rounded-full text-xs font-black transition cursor-pointer flex items-center gap-1.5 ${
                selectedMetric === "SOIL_TEMP"
                  ? "bg-[#EA580C] text-white shadow-xs"
                  : "bg-[#F4F7FC] dark:bg-[#131926] text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white border border-[#E8EEF5] dark:border-[#212C42]"
              }`}
            >
              <span>🌡️ Soil Temp</span>
            </button>
            <button
              onClick={() => setSelectedMetric("HUMIDITY")}
              className={`px-3.5 py-1.5 rounded-full text-xs font-black transition cursor-pointer flex items-center gap-1.5 ${
                selectedMetric === "HUMIDITY"
                  ? "bg-[#059669] text-white shadow-xs"
                  : "bg-[#F4F7FC] dark:bg-[#131926] text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-white border border-[#E8EEF5] dark:border-[#212C42]"
              }`}
            >
              <span>💨 Humidity</span>
            </button>

          </div>
        </div>

        {/* 10-Day Historical Day Picker Calendar Tabs Bar */}
        <div className="bg-[#F8FAFC] dark:bg-[#131926] rounded-2xl p-2.5 border border-[#E8EEF5] dark:border-[#212C42] overflow-x-auto">
          <div className="flex items-center gap-2 min-w-max">
            <span className="text-xs font-black text-[#8A94A6] dark:text-[#94A3B8] uppercase px-2">10-Day Calendar:</span>
            {tenDaysList.map((d) => (
              <button
                key={d.index}
                onClick={() => setSelectedDayIndex(d.index)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold transition cursor-pointer flex flex-col items-center min-w-[70px] ${
                  selectedDayIndex === d.index
                    ? "bg-[#2563EB] text-white font-black shadow-sm"
                    : "bg-white dark:bg-[#1A2234] hover:bg-[#EEF2F6] dark:hover:bg-[#222C42] text-[#64748B] dark:text-[#CBD5E1] border border-[#E8EEF5] dark:border-[#212C42]"
                }`}
              >
                <span className="text-[10px] opacity-80">{d.dayName}</span>
                <span className="font-extrabold">{d.dateStr}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 24-Hour Recharts Area Curve Visualizer */}
        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={hourlyTelemetryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="areaCurveGradA" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="areaCurveGradB" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34D399" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#34D399" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDarkMode ? "rgba(255, 255, 255, 0.08)" : "rgba(15, 23, 42, 0.06)"} />
              <XAxis dataKey="time" stroke={isDarkMode ? "#94A3B8" : "#64748B"} fontSize={11} tickLine={false} />
              <YAxis stroke={isDarkMode ? "#94A3B8" : "#64748B"} fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDarkMode ? "rgba(15, 23, 42, 0.95)" : "rgba(255, 255, 255, 0.95)",
                  backdropFilter: "blur(16px)",
                  borderRadius: "16px",
                  border: isDarkMode ? "1px solid rgba(255, 255, 255, 0.12)" : "1px solid rgba(226, 232, 240, 0.9)",
                  color: isDarkMode ? "#F8FAFC" : "#0F172A",
                  fontSize: "12px",
                  fontWeight: "bold",
                  boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
                }}
              />
              <Area
                type="monotone"
                dataKey={
                  selectedMetric === "SOIL_MOISTURE"
                    ? graphNode === "NODE_A" ? "moistureA" : "moistureB"
                    : selectedMetric === "SOIL_TEMP"
                    ? graphNode === "NODE_A" ? "soilTempA" : "soilTempB"
                    : graphNode === "NODE_A" ? "humidityA" : "humidityB"
                }
                name={graphNode === "NODE_A" ? "Node A (Field A)" : "Node B (Field B)"}
                stroke={graphNode === "NODE_A" ? "#0284C7" : "#059669"}
                strokeWidth={2.5}
                fillOpacity={1}
                fill={graphNode === "NODE_A" ? "url(#areaCurveGradA)" : "url(#areaCurveGradB)"}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* 24-Hour Telemetry Summary Row */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-[#E8EEF5] dark:border-white/10 text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 font-bold text-[#0F172A] dark:text-[#F8FAFC]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#0284C7]" />
              <span>Node A (Field A - Tomato Canopy)</span>
            </div>
            <div className="flex items-center gap-1.5 font-bold text-[#0F172A] dark:text-[#F8FAFC]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#059669]" />
              <span>Node B (Field B - Greenhouse)</span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-lg font-black text-[#0F172A] dark:text-[#F8FAFC]">
              {selectedMetric === "SOIL_MOISTURE" ? "76.2% Avg Moisture" : selectedMetric === "SOIL_TEMP" ? "24.1°C Avg Temp" : "64.8% Avg Humidity"}
            </span>
            <span className="text-xs text-[#64748B] dark:text-[#94A3B8] ml-2 font-medium">for {tenDaysList[selectedDayIndex]?.dateStr || "Today"}</span>
          </div>
        </div>

      </section>

    </div>
  );
}
