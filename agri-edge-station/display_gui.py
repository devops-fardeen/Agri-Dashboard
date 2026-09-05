import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime, timezone
import os
import sys

# Ensure local module directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database

class AgriSmartDisplayGUI:
    """
    Tier 1: Physical On-Device Display GUI for Raspberry Pi Touchscreen (1024x600 / 800x480).
    Runs natively on Python Tkinter with direct SQLite database binding for seamless
    bidirectional synchronization with Tier 2 (Local AP) and Tier 3 (Cloud).
    """

    # High-contrast outdoor-readable color palette
    BG_DARK = "#0d1117"        # Deep midnight background
    CARD_BG = "#161b22"        # Elevated panel background
    INNER_BG = "#090d13"       # Recessed metric background
    BORDER_COLOR = "#30363d"   # Crisp border
    TEXT_MAIN = "#f0f6fc"      # Crisp bright text
    TEXT_MUTED = "#8b949e"     # Subtitle gray
    
    # Semantic Accents
    GREEN_ON = "#238636"       # Active emerald
    GREEN_TEXT = "#3fb950"     # Emerald readout
    RED_STOP = "#da3633"       # Emergency rose
    RED_ACTIVE = "#f85149"
    AMBER_WARN = "#d29922"     # Low moisture amber
    BLUE_ACCENT = "#58a6ff"    # Soil temp blue
    ORANGE_TEMP = "#f0883e"    # Canopy temp orange
    CYAN_HUMID = "#39c5cf"     # Humidity cyan
    BTN_IDLE = "#21262d"       # Idle actuator button
    BTN_IDLE_HOVER = "#30363d"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AgriSmart Field Console — Tier 1")
        self.root.configure(bg=self.BG_DARK)
        
        # Center 1024x600 window by default
        win_w, win_h = 1024, 600
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(800, 480)

        # Fullscreen handling (F11 = Toggle, Escape = Exit Fullscreen)
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Initialize SQLite database
        database.init_db()

        # Build UI Components
        self._setup_styles()
        self._build_header()
        self._build_zone_cards()
        self._build_bottom_bar()

        # Start non-blocking polling loop (every 1000ms)
        self.poll_data()

    def _setup_styles(self):
        """Prepares standard system font families for crisp rendering."""
        family = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"
        self.font_brand = (family, 13, "bold")
        self.font_clock = (family, 15, "bold")
        self.font_small = (family, 9)
        self.font_badge = (family, 10, "bold")
        self.font_zone_title = (family, 13, "bold")
        self.font_big_num = (family, 32, "bold")
        self.font_metric_lbl = (family, 8, "bold")
        self.font_metric_val = (family, 12, "bold")
        self.font_btn = (family, 11, "bold")

    def _build_header(self):
        """Builds top status bar: Brand, Digital Clock, Cloud Sync State."""
        self.header_frame = tk.Frame(self.root, bg=self.CARD_BG, height=58, padx=16, pady=8, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Left: Station Brand & IP
        left_box = tk.Frame(self.header_frame, bg=self.CARD_BG)
        left_box.pack(side=tk.LEFT, fill=tk.Y)
        
        lbl_brand = tk.Label(left_box, text="🌱 AGRISMART FIELD CONSOLE", font=self.font_brand, fg=self.TEXT_MAIN, bg=self.CARD_BG)
        lbl_brand.pack(anchor="w")
        
        lbl_ap = tk.Label(left_box, text="Local Hotspot AP: 10.42.0.1:8000 • Tier 1 Physical Console", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG)
        lbl_ap.pack(anchor="w")

        # Center: Live Digital Clock & Date
        center_box = tk.Frame(self.header_frame, bg=self.CARD_BG)
        center_box.pack(side=tk.LEFT, expand=True)

        self.lbl_clock = tk.Label(center_box, text="--:--:--", font=self.font_clock, fg=self.TEXT_MAIN, bg=self.CARD_BG)
        self.lbl_clock.pack()
        self.lbl_date = tk.Label(center_box, text="Loading date...", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG)
        self.lbl_date.pack()

        # Right: Cloud Sync Health Indicator
        right_box = tk.Frame(self.header_frame, bg=self.CARD_BG)
        right_box.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_sync_badge = tk.Label(
            right_box,
            text="● CLOUD LINKED",
            font=self.font_badge,
            fg=self.GREEN_TEXT,
            bg=self.BTN_IDLE,
            padx=12,
            pady=4,
            relief=tk.FLAT,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.lbl_sync_badge.pack(pady=4)

    def _build_zone_cards(self):
        """Builds side-by-side telemetry cards for Zone A (Crops) and Zone B (Orchard)."""
        self.cards_container = tk.Frame(self.root, bg=self.BG_DARK, padx=16, pady=12)
        self.cards_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.cards_container.grid_columnconfigure(0, weight=1, uniform="group1")
        self.cards_container.grid_columnconfigure(1, weight=1, uniform="group1")
        self.cards_container.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # ZONE A CARD
        # -------------------------------------------------------------
        self.card_a = tk.Frame(self.cards_container, bg=self.CARD_BG, padx=16, pady=14, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.card_a.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Zone A Header
        hdr_a = tk.Frame(self.card_a, bg=self.CARD_BG)
        hdr_a.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr_a, text="ZONE A — CROPS FIELD", font=self.font_zone_title, fg=self.TEXT_MAIN, bg=self.CARD_BG).pack(side=tk.LEFT)
        tk.Label(hdr_a, text="Node: EDGE_01 • LoRa Ch 1", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(side=tk.RIGHT)

        # Zone A Main Moisture Hero Box
        moist_box_a = tk.Frame(self.card_a, bg=self.INNER_BG, padx=12, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        moist_box_a.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(moist_box_a, text="ROOT SOIL MOISTURE", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_za_moist = tk.Label(moist_box_a, text="--.-%", font=self.font_big_num, fg=self.GREEN_TEXT, bg=self.INNER_BG)
        self.lbl_za_moist.pack(anchor="w")
        self.lbl_za_moist_status = tk.Label(moist_box_a, text="Target: 60% – 75% • Optimal", font=self.font_small, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_za_moist_status.pack(anchor="w")

        # Zone A Secondary Metrics Row (Soil Temp, Canopy Temp, Humidity)
        grid_a = tk.Frame(self.card_a, bg=self.CARD_BG)
        grid_a.pack(fill=tk.X, pady=(0, 12))
        grid_a.grid_columnconfigure((0, 1, 2), weight=1, uniform="submetric")

        # Metric 1: Soil Temp
        m1_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m1_a.grid(row=0, column=0, sticky="nsew", padx=2)
        tk.Label(m1_a, text="SOIL TEMP", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_za_soil_temp = tk.Label(m1_a, text="--°C", font=self.font_metric_val, fg=self.BLUE_ACCENT, bg=self.INNER_BG)
        self.lbl_za_soil_temp.pack(anchor="w")

        # Metric 2: Canopy Temp
        m2_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m2_a.grid(row=0, column=1, sticky="nsew", padx=2)
        tk.Label(m2_a, text="CANOPY TEMP", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_za_amb_temp = tk.Label(m2_a, text="--°C", font=self.font_metric_val, fg=self.ORANGE_TEMP, bg=self.INNER_BG)
        self.lbl_za_amb_temp.pack(anchor="w")

        # Metric 3: Air Humidity
        m3_a = tk.Frame(grid_a, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m3_a.grid(row=0, column=2, sticky="nsew", padx=2)
        tk.Label(m3_a, text="AIR HUMIDITY", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_za_humid = tk.Label(m3_a, text="--%", font=self.font_metric_val, fg=self.CYAN_HUMID, bg=self.INNER_BG)
        self.lbl_za_humid.pack(anchor="w")

        # Zone A Touch-Friendly Pump Actuator Button
        self.btn_pump_a = tk.Button(
            self.card_a,
            text="PUMP IDLE / OFF",
            font=self.font_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MAIN,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            command=lambda: self.toggle_pump("PUMP_ZONE_A")
        )
        self.btn_pump_a.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))

        # -------------------------------------------------------------
        # ZONE B CARD
        # -------------------------------------------------------------
        self.card_b = tk.Frame(self.cards_container, bg=self.CARD_BG, padx=16, pady=14, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.card_b.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Zone B Header
        hdr_b = tk.Frame(self.card_b, bg=self.CARD_BG)
        hdr_b.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr_b, text="ZONE B — ORCHARD GROVE", font=self.font_zone_title, fg=self.TEXT_MAIN, bg=self.CARD_BG).pack(side=tk.LEFT)
        tk.Label(hdr_b, text="Node: EDGE_02 • LoRa Ch 2", font=self.font_small, fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(side=tk.RIGHT)

        # Zone B Main Moisture Hero Box
        moist_box_b = tk.Frame(self.card_b, bg=self.INNER_BG, padx=12, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        moist_box_b.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(moist_box_b, text="ORCHARD SOIL MOISTURE", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_zb_moist = tk.Label(moist_box_b, text="--.-%", font=self.font_big_num, fg=self.GREEN_TEXT, bg=self.INNER_BG)
        self.lbl_zb_moist.pack(anchor="w")
        self.lbl_zb_moist_status = tk.Label(moist_box_b, text="Target: 50% – 65% • Normal", font=self.font_small, fg=self.TEXT_MUTED, bg=self.INNER_BG)
        self.lbl_zb_moist_status.pack(anchor="w")

        # Zone B Secondary Metrics Row
        grid_b = tk.Frame(self.card_b, bg=self.CARD_BG)
        grid_b.pack(fill=tk.X, pady=(0, 12))
        grid_b.grid_columnconfigure((0, 1, 2), weight=1, uniform="submetric")

        # Metric 1: Soil Temp
        m1_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m1_b.grid(row=0, column=0, sticky="nsew", padx=2)
        tk.Label(m1_b, text="SOIL TEMP", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_zb_soil_temp = tk.Label(m1_b, text="--°C", font=self.font_metric_val, fg=self.BLUE_ACCENT, bg=self.INNER_BG)
        self.lbl_zb_soil_temp.pack(anchor="w")

        # Metric 2: Canopy Temp
        m2_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m2_b.grid(row=0, column=1, sticky="nsew", padx=2)
        tk.Label(m2_b, text="CANOPY TEMP", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_zb_amb_temp = tk.Label(m2_b, text="--°C", font=self.font_metric_val, fg=self.ORANGE_TEMP, bg=self.INNER_BG)
        self.lbl_zb_amb_temp.pack(anchor="w")

        # Metric 3: Air Humidity
        m3_b = tk.Frame(grid_b, bg=self.INNER_BG, padx=8, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        m3_b.grid(row=0, column=2, sticky="nsew", padx=2)
        tk.Label(m3_b, text="AIR HUMIDITY", font=self.font_metric_lbl, fg=self.TEXT_MUTED, bg=self.INNER_BG).pack(anchor="w")
        self.lbl_zb_humid = tk.Label(m3_b, text="--%", font=self.font_metric_val, fg=self.CYAN_HUMID, bg=self.INNER_BG)
        self.lbl_zb_humid.pack(anchor="w")

        # Zone B Touch-Friendly Pump Actuator Button
        self.btn_pump_b = tk.Button(
            self.card_b,
            text="PUMP IDLE / OFF",
            font=self.font_btn,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MAIN,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            height=2,
            cursor="hand2",
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            command=lambda: self.toggle_pump("PUMP_ZONE_B")
        )
        self.btn_pump_b.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))

    def _build_bottom_bar(self):
        """Builds bottom quick action bar: Rover Telemetry, Emergency Stop, Exit."""
        self.bottom_frame = tk.Frame(self.root, bg=self.CARD_BG, height=52, padx=16, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_frame.pack_propagate(False)

        # Left: Rover Status Readout
        self.lbl_rover_status = tk.Label(
            self.bottom_frame,
            text="🚜 Rover: IDLE / STOP • Battery: 84% • Heading: NW (312°)",
            font=self.font_small,
            fg=self.TEXT_MAIN,
            bg=self.CARD_BG
        )
        self.lbl_rover_status.pack(side=tk.LEFT, pady=4)

        # Right: Emergency Stop Rover & Exit / Maintenance Buttons
        btn_exit = tk.Button(
            self.bottom_frame,
            text="EXIT CONSOLE",
            font=self.font_small,
            bg=self.BTN_IDLE,
            fg=self.TEXT_MUTED,
            activebackground=self.BTN_IDLE_HOVER,
            activeforeground=self.TEXT_MAIN,
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.root.quit
        )
        btn_exit.pack(side=tk.RIGHT, padx=(8, 0))

        btn_emergency_stop = tk.Button(
            self.bottom_frame,
            text="🛑 EMERGENCY STOP ROVER",
            font=self.font_btn,
            bg=self.RED_STOP,
            fg="#ffffff",
            activebackground=self.RED_ACTIVE,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=4,
            cursor="hand2",
            command=self.emergency_stop_rover
        )
        btn_emergency_stop.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # ACTIONS & EVENT HANDLERS
    # ------------------------------------------------------------------
    def toggle_pump(self, target: str):
        """Toggles the state of a pump directly in SQLite and updates button."""
        new_state = database.toggle_actuator_state(target)
        self.update_pump_button(target, new_state)

    def emergency_stop_rover(self):
        """Dispatches an immediate emergency stop for the field scout rover."""
        database.update_rover_command("STOP")
        self.lbl_rover_status.config(text="🛑 ROVER EMERGENCY STOP TRIGGERED", fg=self.RED_STOP)

    def update_pump_button(self, target: str, state: int):
        """Updates the visual appearance of a pump actuator button."""
        btn = self.btn_pump_a if target == "PUMP_ZONE_A" else self.btn_pump_b
        name = "ZONE A PUMP" if target == "PUMP_ZONE_A" else "ZONE B PUMP"
        
        if state:
            btn.config(
                text=f"● {name} RUNNING (ACTIVE)",
                bg=self.GREEN_ON,
                fg="#ffffff",
                activebackground="#2ea043"
            )
        else:
            btn.config(
                text=f"○ {name} IDLE / OFF",
                bg=self.BTN_IDLE,
                fg=self.TEXT_MAIN,
                activebackground=self.BTN_IDLE_HOVER
            )

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    # ------------------------------------------------------------------
    # DATA POLLING LOOP
    # ------------------------------------------------------------------
    def poll_data(self):
        """Non-blocking 1-second polling loop reading SQLite state."""
        try:
            # 1. Update Clock & Date
            now = datetime.now()
            self.lbl_clock.config(text=now.strftime("%I:%M:%S %p"))
            self.lbl_date.config(text=now.strftime("%A, %b %d, %Y"))

            # 2. Update Cloud Sync Badge
            stats = database.get_edge_stats()
            unsynced = stats.get("unsynced_records", 0)
            if unsynced == 0:
                self.lbl_sync_badge.config(text="● CLOUD LINKED", fg=self.GREEN_TEXT)
            else:
                self.lbl_sync_badge.config(text=f"○ BUFFERING ({unsynced} queued)", fg=self.AMBER_WARN)

            # 3. Update Zone A Telemetry
            za = database.get_latest_zone_data("ZONE_A")
            if za:
                moist_a = za.get("soil_moisture", 0.0)
                self.lbl_za_moist.config(text=f"{moist_a:.1f}%")
                
                # Dynamic Threshold Coloring
                if moist_a < 40.0:
                    self.lbl_za_moist.config(fg=self.AMBER_WARN)
                    self.lbl_za_moist_status.config(text="Target: 60% – 75% • LOW MOISTURE / DRY", fg=self.AMBER_WARN)
                elif moist_a > 75.0:
                    self.lbl_za_moist.config(fg=self.CYAN_HUMID)
                    self.lbl_za_moist_status.config(text="Target: 60% – 75% • HIGH MOISTURE / SATURATED", fg=self.CYAN_HUMID)
                else:
                    self.lbl_za_moist.config(fg=self.GREEN_TEXT)
                    self.lbl_za_moist_status.config(text="Target: 60% – 75% • OPTIMAL HYDRATION", fg=self.GREEN_TEXT)

                self.lbl_za_soil_temp.config(text=f"{za.get('soil_temp', 0.0):.1f}°C")
                self.lbl_za_amb_temp.config(text=f"{za.get('ambient_temp', 0.0):.1f}°C")
                self.lbl_za_humid.config(text=f"{za.get('ambient_humidity', 0.0):.1f}%")

            # 4. Update Zone B Telemetry
            zb = database.get_latest_zone_data("ZONE_B")
            if zb:
                moist_b = zb.get("soil_moisture", 0.0)
                self.lbl_zb_moist.config(text=f"{moist_b:.1f}%")
                
                if moist_b < 38.0:
                    self.lbl_zb_moist.config(fg=self.AMBER_WARN)
                    self.lbl_zb_moist_status.config(text="Target: 50% – 65% • LOW MOISTURE / DRY", fg=self.AMBER_WARN)
                elif moist_b > 70.0:
                    self.lbl_zb_moist.config(fg=self.CYAN_HUMID)
                    self.lbl_zb_moist_status.config(text="Target: 50% – 65% • HIGH MOISTURE", fg=self.CYAN_HUMID)
                else:
                    self.lbl_zb_moist.config(fg=self.GREEN_TEXT)
                    self.lbl_zb_moist_status.config(text="Target: 50% – 65% • OPTIMAL HYDRATION", fg=self.GREEN_TEXT)

                self.lbl_zb_soil_temp.config(text=f"{zb.get('soil_temp', 0.0):.1f}°C")
                self.lbl_zb_amb_temp.config(text=f"{zb.get('ambient_temp', 0.0):.1f}°C")
                self.lbl_zb_humid.config(text=f"{zb.get('ambient_humidity', 0.0):.1f}%")

            # 5. Update Actuator Pump States (Two-Way Synced)
            pump_a = database.get_actuator_state("PUMP_ZONE_A")
            pump_b = database.get_actuator_state("PUMP_ZONE_B")
            self.update_pump_button("PUMP_ZONE_A", pump_a)
            self.update_pump_button("PUMP_ZONE_B", pump_b)

            # 6. Update Rover State
            rover = database.get_rover_state()
            action = rover.get("last_action", "STOP")
            speed = rover.get("speed", 0.0)
            battery = rover.get("battery", 84)
            heading = rover.get("heading", "NW (312°)")
            self.lbl_rover_status.config(
                text=f"🚜 Rover: {action} ({speed:.1f} m/s) • Battery: {battery}% • Heading: {heading}",
                fg=self.TEXT_MAIN
            )

        except Exception as e:
            print(f"[GUI Error] {e}")

        # Schedule next poll in 1000ms
        self.root.after(1000, self.poll_data)

def main():
    root = tk.Tk()
    app = AgriSmartDisplayGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
