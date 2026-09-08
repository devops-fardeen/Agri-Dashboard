#include <WiFi.h>
#include <esp_now.h>

// =====================================================
// PINS CONFIGURATION
// =====================================================
#define RAIN_PIN 27
#define RELAY1_PIN 25  // Smart Pump Zone A
#define RELAY2_PIN 26  // Smart Pump Zone B

// =====================================================
// RELAY CONFIGURATION (Active LOW Relay Modules)
// =====================================================
#define RELAY_ON LOW
#define RELAY_OFF HIGH

// =====================================================
// DATA STRUCTURE (Matches Slave Node)
// =====================================================
typedef struct {
  float temperature;
  float humidity;
  int soilRaw;
  int soilPercent;
} SensorData;

SensorData slaveData;

// =====================================================
// =====================================================
// GLOBAL VARIABLES & TIMERS
// =====================================================
unsigned long lastRainSample = 0;
const unsigned long RAIN_SAMPLE_INTERVAL = 1000; // Sample rain sensor every 1 second
int lastRainState = -1; // -1: uninitialized, 0: NO_RAIN, 1: RAIN

// =====================================================
// ESP-NOW RECEIVE CALLBACK
// =====================================================
void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  if (len == sizeof(SensorData)) {
    memcpy(&slaveData, incomingData, sizeof(slaveData));

    // Active LOW: Rain on sensor plate grounds the comparator DO pin to LOW
    bool raining = (digitalRead(RAIN_PIN) == LOW);

    // Send structured serial packet to Raspberry Pi 5 Gateway
    // Format: DATA,<temp>,<humidity>,<soilPercent>,<soilRaw>,<RAIN/NO_RAIN>
    Serial.print("DATA,");
    Serial.print(slaveData.temperature, 2);
    Serial.print(",");
    Serial.print(slaveData.humidity, 2);
    Serial.print(",");
    Serial.print(slaveData.soilPercent);
    Serial.print(",");
    Serial.print(slaveData.soilRaw);
    Serial.print(",");
    if (raining) {
      Serial.println("RAIN");
    } else {
      Serial.println("NO_RAIN");
    }
  }
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=====================================");
  Serial.println("   AGRISMART MASTER NODE (ESP32)");
  Serial.println("=====================================");

  // Digital Rain Sensor (Active LOW on FC-37 / YL-83 comparator)
  pinMode(RAIN_PIN, INPUT_PULLUP);
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);

  // Default Relays to OFF on boot
  digitalWrite(RELAY1_PIN, RELAY_OFF);
  digitalWrite(RELAY2_PIN, RELAY_OFF);

  WiFi.mode(WIFI_STA);
  delay(500);

  Serial.print("Master MAC Address: ");
  Serial.println(WiFi.macAddress());

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW initialization failed!");
    while (true) delay(1000);
  }

  esp_now_register_recv_cb(onDataRecv);
  Serial.println("✓ ESP-NOW receiver ready. Master Node Online.");
}

// =====================================================
// MAIN LOOP: READ COMMANDS & PERIODIC SENSOR BROADCAST
// =====================================================
void loop() {
  unsigned long now = millis();

  // 1. Continuous Periodic Rain Sensor Broadcast (Every 1000ms)
  // Ensures Raspberry Pi edge gateway receives live rain telemetry even without slave node
  if (now - lastRainSample >= RAIN_SAMPLE_INTERVAL) {
    lastRainSample = now;
    int currentRain = (digitalRead(RAIN_PIN) == LOW) ? 1 : 0;
    
    if (currentRain == 1) {
      Serial.println("RAIN_STATUS:RAIN");
    } else {
      Serial.println("RAIN_STATUS:NO_RAIN");
    }
    lastRainState = currentRain;
  }

  // 2. Read Commands from Raspberry Pi
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "PUMP1_ON") {
      digitalWrite(RELAY1_PIN, RELAY_ON);
      Serial.println("PUMP1_ON_ACK");
    } else if (command == "PUMP1_OFF") {
      digitalWrite(RELAY1_PIN, RELAY_OFF);
      Serial.println("PUMP1_OFF_ACK");
    } else if (command == "PUMP2_ON") {
      digitalWrite(RELAY2_PIN, RELAY_ON);
      Serial.println("PUMP2_ON_ACK");
    } else if (command == "PUMP2_OFF") {
      digitalWrite(RELAY2_PIN, RELAY_OFF);
      Serial.println("PUMP2_OFF_ACK");
    } else if (command == "ALL_OFF") {
      digitalWrite(RELAY1_PIN, RELAY_OFF);
      digitalWrite(RELAY2_PIN, RELAY_OFF);
      Serial.println("ALL_PUMPS_OFF_ACK");
    } else if (command == "GET_RAIN") {
      bool raining = (digitalRead(RAIN_PIN) == LOW);
      Serial.println(raining ? "RAIN_STATUS:RAIN" : "RAIN_STATUS:NO_RAIN");
    }
  }
  delay(20);
}

