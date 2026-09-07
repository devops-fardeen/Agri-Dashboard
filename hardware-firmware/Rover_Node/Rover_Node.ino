#include <WiFi.h>
#include <WebServer.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// =====================================================
// WIFI CONFIGURATION (Phone Mobile Hotspot)
// =====================================================
const char* WIFI_SSID     = "realme";
const char* WIFI_PASSWORD = "123456789";

WebServer server(80);

// =====================================================
// BTS7960 HIGH POWER MOTOR DRIVER PINS
// =====================================================
#define LEFT_RPWM  25
#define LEFT_LPWM  26

#define RIGHT_RPWM 18
#define RIGHT_LPWM 19

// =====================================================
// SENSOR PINS
// =====================================================
#define LEFT_IR     32
#define RIGHT_IR    33

#define TRIG_PIN     5
#define ECHO_PIN    34

#define BATTERY_PIN 35

// =====================================================
// PWM CONFIGURATION & STATE
// =====================================================
#define PWM_FREQ       1000
#define PWM_RESOLUTION 8

int motorSpeed = 190;
String currentMovement = "STOP";

// =====================================================
// BATTERY VOLTAGE MONITORING (3S LiPo Calibration)
// Voltage Divider: R1=30k, R2=7.5k (Ratio = 5.00)
// =====================================================
float voltageCalibration = 5.00;

// Calculate accurate LiPo percentage using standard discharge curve
int calculateBatteryPercent(float voltage) {
  if (voltage >= 12.60) return 100;
  if (voltage >= 12.45) return 95;
  if (voltage >= 12.30) return 90;
  if (voltage >= 12.15) return 80;
  if (voltage >= 12.00) return 70;
  if (voltage >= 11.85) return 60;
  if (voltage >= 11.70) return 50;
  if (voltage >= 11.55) return 40;
  if (voltage >= 11.40) return 30;
  if (voltage >= 11.20) return 20;
  if (voltage >= 11.00) return 10;
  if (voltage >= 10.50) return 5;
  return 0;
}

// Multi-sampled ADC reading to eliminate motor electrical noise
float getBatteryVoltage() {
  long rawSum = 0;
  for (int i = 0; i < 32; i++) {
    rawSum += analogRead(BATTERY_PIN);
    delayMicroseconds(50);
  }
  float avgRaw = (float)rawSum / 32.0;
  float pinVoltage = (avgRaw / 4095.0) * 3.3;
  float actualVoltage = pinVoltage * voltageCalibration;
  return actualVoltage;
}

// =====================================================
// AUTONOMOUS NAVIGATION CONFIGURATION
// =====================================================
const float FRONT_OBSTACLE_DISTANCE = 28.0; // cm

bool autoMode = false;
bool autoTurning = false;
unsigned long autoTurnStart = 0;
const unsigned long AUTO_TURN_TIME = 380; // ms turn duration

unsigned long lastAutoCheck = 0;
const unsigned long AUTO_CHECK_INTERVAL = 60; // ms check rate

unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 5000;

// =====================================================
// PWM SETUP
// =====================================================
void setupPWM() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(LEFT_RPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(LEFT_LPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(RIGHT_RPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(RIGHT_LPWM, PWM_FREQ, PWM_RESOLUTION);

  ledcWrite(LEFT_RPWM, 0);
  ledcWrite(LEFT_LPWM, 0);
  ledcWrite(RIGHT_RPWM, 0);
  ledcWrite(RIGHT_LPWM, 0);
#else
  ledcSetup(0, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(LEFT_RPWM, 0);
  ledcSetup(1, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(LEFT_LPWM, 1);
  ledcSetup(2, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(RIGHT_RPWM, 2);
  ledcSetup(3, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(RIGHT_LPWM, 3);

  ledcWrite(0, 0);
  ledcWrite(1, 0);
  ledcWrite(2, 0);
  ledcWrite(3, 0);
#endif
}

void writeMotorPWM(int leftR, int leftL, int rightR, int rightL) {
  leftR = constrain(leftR, 0, 255);
  leftL = constrain(leftL, 0, 255);
  rightR = constrain(rightR, 0, 255);
  rightL = constrain(rightL, 0, 255);

#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(LEFT_RPWM, leftR);
  ledcWrite(LEFT_LPWM, leftL);
  ledcWrite(RIGHT_RPWM, rightR);
  ledcWrite(RIGHT_LPWM, rightL);
#else
  ledcWrite(0, leftR);
  ledcWrite(1, leftL);
  ledcWrite(2, rightR);
  ledcWrite(3, rightL);
#endif
}

// =====================================================
// MOTOR CONTROL PRIMITIVES (BTS7960)
// =====================================================
void stopMotors() {
  writeMotorPWM(0, 0, 0, 0);
  currentMovement = "STOP";
}

void moveForward() {
  writeMotorPWM(motorSpeed, 0, motorSpeed, 0);
  currentMovement = "FORWARD";
}

void moveBackward() {
  writeMotorPWM(0, motorSpeed, 0, motorSpeed);
  currentMovement = "BACKWARD";
}

void turnLeft() {
  writeMotorPWM(0, motorSpeed, motorSpeed, 0);
  currentMovement = "LEFT";
}

void turnRight() {
  writeMotorPWM(motorSpeed, 0, 0, motorSpeed);
  currentMovement = "RIGHT";
}

// Apply speed immediately to whatever state is currently active
void applyCurrentMovement() {
  if (currentMovement == "FORWARD" || currentMovement == "AUTO" || currentMovement == "AUTO-FORWARD") {
    writeMotorPWM(motorSpeed, 0, motorSpeed, 0);
  } else if (currentMovement == "BACKWARD") {
    writeMotorPWM(0, motorSpeed, 0, motorSpeed);
  } else if (currentMovement == "LEFT" || currentMovement == "AUTO-AVOID-LEFT") {
    writeMotorPWM(0, motorSpeed, motorSpeed, 0);
  } else if (currentMovement == "RIGHT" || currentMovement == "AUTO-AVOID-RIGHT") {
    writeMotorPWM(motorSpeed, 0, 0, motorSpeed);
  } else if (currentMovement == "AUTO-NUDGE-RIGHT") {
    writeMotorPWM(motorSpeed, 0, (int)(motorSpeed * 0.55), 0);
  } else if (currentMovement == "AUTO-NUDGE-LEFT") {
    writeMotorPWM((int)(motorSpeed * 0.55), 0, motorSpeed, 0);
  }
}

// =====================================================
// ULTRASONIC DISTANCE SENSOR (HC-SR04 with Filter)
// =====================================================
float readSingleDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 22000); // 22ms max (~3.7m)
  if (duration == 0) return 999.0;
  return (duration * 0.0343 / 2.0);
}

// 3-sample median filter for rock-solid distance readings
float getDistance() {
  float r1 = readSingleDistance();
  delayMicroseconds(500);
  float r2 = readSingleDistance();
  delayMicroseconds(500);
  float r3 = readSingleDistance();

  // Median calculation
  if ((r1 <= r2 && r2 <= r3) || (r3 <= r2 && r2 <= r1)) return r2;
  if ((r2 <= r1 && r1 <= r3) || (r3 <= r1 && r1 <= r2)) return r1;
  return r3;
}

// =====================================================
// INFRARED SENSORS
// =====================================================
bool leftBlocked() {
  return digitalRead(LEFT_IR) == LOW;
}

bool rightBlocked() {
  return digitalRead(RIGHT_IR) == LOW;
}

// =====================================================
// CONTINUOUS AUTONOMOUS MODE
// =====================================================
void automaticMode() {
  unsigned long now = millis();

  // Active evasion turn handling
  if (autoTurning) {
    if (now - autoTurnStart >= AUTO_TURN_TIME) {
      autoTurning = false;
      // Resume continuous forward drive immediately!
      moveForward();
      currentMovement = "AUTO-FORWARD";
    }
    return;
  }

  // Periodic sensor checks
  if (now - lastAutoCheck < AUTO_CHECK_INTERVAL) return;
  lastAutoCheck = now;

  float distance = getDistance();
  bool leftObstacle = leftBlocked();
  bool rightObstacle = rightBlocked();

  // Front obstacle evasion (< 28 cm)
  if (distance > 1.5 && distance < FRONT_OBSTACLE_DISTANCE) {
    if (!leftObstacle && rightObstacle) {
      turnLeft();
      autoTurning = true;
      autoTurnStart = now;
      currentMovement = "AUTO-AVOID-LEFT";
    } else {
      turnRight();
      autoTurning = true;
      autoTurnStart = now;
      currentMovement = "AUTO-AVOID-RIGHT";
    }
    return;
  }

  // Row edge steering via IR
  if (leftObstacle && !rightObstacle) {
    // Steer gently right
    writeMotorPWM(motorSpeed, 0, (int)(motorSpeed * 0.55), 0);
    currentMovement = "AUTO-NUDGE-RIGHT";
  } else if (rightObstacle && !leftObstacle) {
    // Steer gently left
    writeMotorPWM((int)(motorSpeed * 0.55), 0, motorSpeed, 0);
    currentMovement = "AUTO-NUDGE-LEFT";
  } else {
    // Both clear or both aligned -> drive forward continuously
    moveForward();
    currentMovement = "AUTO-FORWARD";
  }
}

// =====================================================
// API ROUTE HANDLERS
// =====================================================
void handleRoot() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  float v = getBatteryVoltage();
  int pct = calculateBatteryPercent(v);

  String msg = "AGRI ROVER READY\n";
  msg += "IP: " + WiFi.localIP().toString() + "\n";
  msg += "Movement: " + currentMovement + "\n";
  msg += "Speed: " + String(motorSpeed) + "\n";
  msg += "Auto Mode: " + String(autoMode ? "ON" : "OFF") + "\n";
  msg += "Battery Voltage: " + String(v, 2) + " V (" + String(pct) + "%)\n";
  msg += "Distance: " + String(getDistance(), 1) + " cm\n";

  server.send(200, "text/plain", msg);
}

void handleCommand() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  if (!server.hasArg("move")) {
    server.send(400, "text/plain", "Missing move parameter");
    return;
  }

  String cmd = server.arg("move");
  cmd.toLowerCase();
  cmd.trim();

  Serial.print("Cmd: ");
  Serial.println(cmd);

  if (cmd == "forward" || cmd == "start" || cmd == "move_forward") {
    autoMode = false;
    autoTurning = false;
    moveForward();
  } else if (cmd == "backward" || cmd == "move_backward") {
    autoMode = false;
    autoTurning = false;
    moveBackward();
  } else if (cmd == "left" || cmd == "move_left") {
    autoMode = false;
    autoTurning = false;
    turnLeft();
  } else if (cmd == "right" || cmd == "move_right") {
    autoMode = false;
    autoTurning = false;
    turnRight();
  } else if (cmd == "stop") {
    autoMode = false;
    autoTurning = false;
    stopMotors();
  } else if (cmd == "auto_on" || cmd == "auto") {
    autoMode = true;
    autoTurning = false;
    currentMovement = "AUTO-FORWARD";
    moveForward();
  } else if (cmd == "auto_off") {
    autoMode = false;
    autoTurning = false;
    stopMotors();
  } else {
    server.send(400, "text/plain", "Unknown cmd");
    return;
  }

  server.send(200, "text/plain", "OK");
}

void handleSpeed() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  int newSpeed = motorSpeed;
  if (server.hasArg("value")) {
    newSpeed = server.arg("value").toInt();
  } else if (server.hasArg("speed")) {
    newSpeed = server.arg("speed").toInt();
  } else {
    server.send(400, "text/plain", "Missing speed value");
    return;
  }

  motorSpeed = constrain(newSpeed, 60, 255);
  Serial.print("Speed updated: ");
  Serial.println(motorSpeed);

  // Apply speed immediately to active movement
  applyCurrentMovement();

  server.send(200, "text/plain", "SPEED OK");
}

void handleHeartbeat() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "text/plain", "ALIVE");
}

void handleTelemetry() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  float distance = getDistance();
  bool left = leftBlocked();
  bool right = rightBlocked();
  float battery = getBatteryVoltage();
  int batteryPct = calculateBatteryPercent(battery);

  String json = "{";
  json += "\"device\":\"AGRI_ROVER\"";
  json += ",\"wifi_connected\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false");
  json += ",\"ip\":\"" + WiFi.localIP().toString() + "\"";
  json += ",\"rssi\":" + String(WiFi.RSSI());
  json += ",\"distance_cm\":" + String(distance, 1);
  json += ",\"left_blocked\":" + String(left ? "true" : "false");
  json += ",\"right_blocked\":" + String(right ? "true" : "false");
  json += ",\"battery_voltage\":" + String(battery, 2);
  json += ",\"battery_percent\":" + String(batteryPct);
  json += ",\"speed\":" + String(motorSpeed);
  json += ",\"auto_mode\":" + String(autoMode ? "true" : "false");
  json += ",\"movement\":\"" + currentMovement + "\"";
  json += ",\"uptime_ms\":" + String(millis());
  json += "}";

  server.send(200, "application/json", json);
}

void handleStatus() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "{\"device\":\"AGRI_ROVER\",\"status\":\"ONLINE\",\"ip\":\"" + WiFi.localIP().toString() + "\",\"uptime_ms\":" + String(millis()) + "}";
  server.send(200, "application/json", json);
}

// =====================================================
// WIFI CONNECTION (Phone Hotspot)
// =====================================================
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false); // Disable WiFi sleep for rock-solid low latency

  Serial.println();
  Serial.println("Connecting Rover to Hotspot: " + String(WIFI_SSID));

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 35) {
    delay(400);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✓ ROVER CONNECTED | IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("WiFi connect failed, will keep retrying in loop");
  }
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  // 1. DISABLE ESP32 BROWNOUT DETECTOR
  // Prevents ESP32 from restarting due to motor startup current surges!
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  delay(500);

  Serial.println("\n================================");
  Serial.println("       AGRI ROVER BOOT");
  Serial.println("================================");

  pinMode(LEFT_IR, INPUT);
  pinMode(RIGHT_IR, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BATTERY_PIN, INPUT);

  setupPWM();
  stopMotors();
  connectWiFi();

  // Web API Routes
  server.on("/", handleRoot);
  server.on("/cmd", handleCommand);
  server.on("/speed", handleSpeed);
  server.on("/heartbeat", handleHeartbeat);
  server.on("/telemetry", handleTelemetry);
  server.on("/status", handleStatus);

  server.enableCORS(true);
  server.begin();

  Serial.println("✓ WebServer running on Port 80");
}

// =====================================================
// MAIN LOOP
// =====================================================
void loop() {
  server.handleClient();

  // Periodic WiFi check without destroying state
  unsigned long now = millis();
  if (now - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = now;
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Reconnecting WiFi...");
      WiFi.reconnect();
    }
  }

  // Continuous Autonomous Execution
  if (autoMode) {
    automaticMode();
  }
}
