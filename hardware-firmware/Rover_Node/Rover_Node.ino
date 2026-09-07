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
// SPEED & MOVEMENT STATE
// =====================================================
int motorSpeed = 190;
String currentMovement = "STOP";

// =====================================================
// AUTONOMOUS PATROL & PLANT SCANNING ROUTINE
// Routine: Drive 1.5s -> Stop 1.0s to scan plant with phone camera -> Drive 1.5s
// Obstacle: If distance <= 25cm, stop & use IR left/right to find clear path!
// =====================================================
const unsigned long PATROL_MOVE_DURATION = 1500; // ms: Move forward along crop row
const unsigned long SCAN_PAUSE_DURATION  = 1000; // ms: Stop 1 second to capture phone camera AI photo
const unsigned long EVADE_TURN_DURATION  = 400;  // ms: Turn away from detected obstacle
const float FRONT_OBSTACLE_THRESHOLD_CM  = 25.0; // cm: Obstacle detection distance

enum AutoState {
  STATE_PATROL_FORWARD,   // Moving to next plant
  STATE_SCAN_PAUSE,       // Stopped 1s for plant diagnosis photo
  STATE_EVADE_OBSTACLE    // Steering around front obstacle
};

bool autoMode = false;
AutoState autoPhase = STATE_PATROL_FORWARD;
unsigned long phaseStartTime = 0;

unsigned long lastSensorCheck = 0;
const unsigned long SENSOR_CHECK_INTERVAL = 50; // ms

unsigned long lastSerialLog = 0;
const unsigned long SERIAL_LOG_INTERVAL = 1000; // ms

unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 5000;

// Battery Divider Calibration (3S LiPo: 11.1V - 12.6V)
float voltageCalibration = 5.00;

// =====================================================
// BATTERY VOLTAGE & PERCENTAGE CALCULATION
// =====================================================
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

float getBatteryVoltage() {
  long rawSum = 0;
  for (int i = 0; i < 20; i++) {
    rawSum += analogRead(BATTERY_PIN);
    delayMicroseconds(50);
  }
  float avgRaw = (float)rawSum / 20.0;
  float pinVoltage = (avgRaw / 4095.0) * 3.3;
  return pinVoltage * voltageCalibration;
}

// =====================================================
// MOTOR CONTROL PRIMITIVES (Universal analogWrite)
// =====================================================
void leftForward(int speed) {
  speed = constrain(speed, 0, 255);
  analogWrite(LEFT_RPWM, speed);
  analogWrite(LEFT_LPWM, 0);
}

void leftBackward(int speed) {
  speed = constrain(speed, 0, 255);
  analogWrite(LEFT_RPWM, 0);
  analogWrite(LEFT_LPWM, speed);
}

void rightForward(int speed) {
  speed = constrain(speed, 0, 255);
  analogWrite(RIGHT_RPWM, speed);
  analogWrite(RIGHT_LPWM, 0);
}

void rightBackward(int speed) {
  speed = constrain(speed, 0, 255);
  analogWrite(RIGHT_RPWM, 0);
  analogWrite(RIGHT_LPWM, speed);
}

void stopMotors() {
  analogWrite(LEFT_RPWM, 0);
  analogWrite(LEFT_LPWM, 0);
  analogWrite(RIGHT_RPWM, 0);
  analogWrite(RIGHT_LPWM, 0);
  currentMovement = "STOP";
}

void moveForward() {
  leftForward(motorSpeed);
  rightForward(motorSpeed);
  currentMovement = "FORWARD";
}

void moveBackward() {
  leftBackward(motorSpeed);
  rightBackward(motorSpeed);
  currentMovement = "BACKWARD";
}

void turnLeft() {
  leftBackward(motorSpeed);
  rightForward(motorSpeed);
  currentMovement = "LEFT";
}

void turnRight() {
  leftForward(motorSpeed);
  rightBackward(motorSpeed);
  currentMovement = "RIGHT";
}

// =====================================================
// SENSORS (Ultrasonic & Infrared)
// =====================================================
float getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 18000); // 18ms timeout (~3m)
  if (duration <= 0) return 999.0;
  float distance = (duration * 0.0343) / 2.0;

  // Filter out noise glitches
  if (distance < 3.0 || distance > 350.0) return 999.0;
  return distance;
}

bool leftBlocked() {
  return digitalRead(LEFT_IR) == LOW; // Low means obstacle detected
}

bool rightBlocked() {
  return digitalRead(RIGHT_IR) == LOW; // Low means obstacle detected
}

// =====================================================
// AUTONOMOUS ROUTINE: PATROL -> STOP 1s (SCAN) -> PATROL
// WITH IR-ASSISTED OBSTACLE EVASION
// =====================================================
void runAutonomousPatrolAndScan() {
  unsigned long now = millis();

  // 1. Check front obstacle periodically
  if (now - lastSensorCheck >= SENSOR_CHECK_INTERVAL) {
    lastSensorCheck = now;
    float distance = getDistance();

    // If an obstacle is detected in front, switch to evasion immediately!
    if (distance <= FRONT_OBSTACLE_THRESHOLD_CM && autoPhase != STATE_EVADE_OBSTACLE) {
      stopMotors();
      bool leftClear = !leftBlocked();
      bool rightClear = !rightBlocked();

      if (leftClear && !rightClear) {
        // Left is open -> Turn Left
        turnLeft();
        currentMovement = "EVADE-LEFT";
      } else if (rightClear && !leftClear) {
        // Right is open -> Turn Right
        turnRight();
        currentMovement = "EVADE-RIGHT";
      } else if (leftClear && rightClear) {
        // Both sides open -> Turn Right
        turnRight();
        currentMovement = "EVADE-RIGHT";
      } else {
        // Both sides blocked -> Back up
        moveBackward();
        currentMovement = "EVADE-BACK";
      }

      autoPhase = STATE_EVADE_OBSTACLE;
      phaseStartTime = now;
      return;
    }
  }

  // 2. State Machine: Patrol -> Scan 1s -> Patrol
  switch (autoPhase) {
    case STATE_PATROL_FORWARD:
      // Driving forward along crop row
      leftForward(motorSpeed);
      rightForward(motorSpeed);
      currentMovement = "PATROL-FORWARD";

      if (now - phaseStartTime >= PATROL_MOVE_DURATION) {
        // Pause 1 second at this crop plant for phone camera scanning!
        stopMotors();
        currentMovement = "SCANNING PLANT";
        autoPhase = STATE_SCAN_PAUSE;
        phaseStartTime = now;
      }
      break;

    case STATE_SCAN_PAUSE:
      // Stopped in front of plant for 1.0 second so camera takes clear leaf photo
      stopMotors();
      currentMovement = "SCANNING PLANT";

      if (now - phaseStartTime >= SCAN_PAUSE_DURATION) {
        // Resume moving forward to next plant!
        leftForward(motorSpeed);
        rightForward(motorSpeed);
        currentMovement = "PATROL-FORWARD";
        autoPhase = STATE_PATROL_FORWARD;
        phaseStartTime = now;
      }
      break;

    case STATE_EVADE_OBSTACLE:
      // Performing evasion maneuver
      if (now - phaseStartTime >= EVADE_TURN_DURATION) {
        // Evasion completed -> Resume forward patrol!
        leftForward(motorSpeed);
        rightForward(motorSpeed);
        currentMovement = "PATROL-FORWARD";
        autoPhase = STATE_PATROL_FORWARD;
        phaseStartTime = now;
      }
      break;
  }
}

// =====================================================
// API ROUTE HANDLERS
// =====================================================
void handleRoot() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  float v = getBatteryVoltage();
  int pct = calculateBatteryPercent(v);

  String msg = "AGRI ROVER ONLINE\n";
  msg += "IP: " + WiFi.localIP().toString() + "\n";
  msg += "Movement: " + currentMovement + "\n";
  msg += "Speed: " + String(motorSpeed) + "\n";
  msg += "Auto Mode: " + String(autoMode ? "ON" : "OFF") + "\n";
  msg += "Battery: " + String(v, 2) + " V (" + String(pct) + "%)\n";
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

  Serial.print(">>> Web Command Received: ");
  Serial.println(cmd);

  if (cmd == "forward" || cmd == "start" || cmd == "move_forward") {
    autoMode = false;
    moveForward();
  } else if (cmd == "backward" || cmd == "move_backward") {
    autoMode = false;
    moveBackward();
  } else if (cmd == "left" || cmd == "move_left") {
    autoMode = false;
    turnLeft();
  } else if (cmd == "right" || cmd == "move_right") {
    autoMode = false;
    turnRight();
  } else if (cmd == "stop") {
    autoMode = false;
    stopMotors();
  } else if (cmd == "auto_on" || cmd == "auto") {
    autoMode = true;
    autoPhase = STATE_PATROL_FORWARD;
    phaseStartTime = millis();
    moveForward();
    currentMovement = "PATROL-FORWARD";
    Serial.println("✓ Auto Mode ENGAGED: Patrol -> Scan (1s) -> Patrol Loop Active!");
  } else if (cmd == "auto_off") {
    autoMode = false;
    stopMotors();
    Serial.println("✓ Auto Mode DISENGAGED — Stopped.");
  } else {
    server.send(400, "text/plain", "Unknown command");
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
    server.send(400, "text/plain", "Missing speed parameter");
    return;
  }

  motorSpeed = constrain(newSpeed, 60, 255);
  Serial.print(">>> Speed Updated to: ");
  Serial.println(motorSpeed);

  if (currentMovement == "FORWARD" || currentMovement == "PATROL-FORWARD") {
    moveForward();
  } else if (currentMovement == "BACKWARD") {
    moveBackward();
  } else if (currentMovement == "LEFT") {
    turnLeft();
  } else if (currentMovement == "RIGHT") {
    turnRight();
  }

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
  WiFi.setSleep(false);

  Serial.println();
  Serial.print("Connecting to Hotspot: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 35) {
    delay(400);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("================================");
    Serial.println("✓ AGRI ROVER CONNECTED!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.println("================================");
  } else {
    Serial.println("WiFi connect failed, will keep retrying in loop");
  }
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  // Disable Brownout detector for BTS7960 motor current surges
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  delay(400);

  Serial.println("\n================================");
  Serial.println("    AGRI ROVER INITIALIZING");
  Serial.println("================================");

  // Motor PWM pins
  pinMode(LEFT_RPWM, OUTPUT);
  pinMode(LEFT_LPWM, OUTPUT);
  pinMode(RIGHT_RPWM, OUTPUT);
  pinMode(RIGHT_LPWM, OUTPUT);

  // Sensors
  pinMode(LEFT_IR, INPUT_PULLUP);
  pinMode(RIGHT_IR, INPUT_PULLUP);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BATTERY_PIN, INPUT);

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

  Serial.println("✓ Rover Web API ready on Port 80");
}

// =====================================================
// MAIN LOOP
// =====================================================
void loop() {
  server.handleClient();

  // Periodic WiFi reconnection check
  unsigned long now = millis();
  if (now - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = now;
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Reconnecting WiFi...");
      WiFi.reconnect();
    }
  }

  // Autonomous Patrol & Scanning Routine
  if (autoMode) {
    runAutonomousPatrolAndScan();
  }

  // Serial Diagnostic Telemetry (Every 1 second)
  if (now - lastSerialLog >= SERIAL_LOG_INTERVAL) {
    lastSerialLog = now;
    float dist = getDistance();
    Serial.printf("[STATUS] Mode: %s | Phase: %s | Spd: %d | Dist: %.1fcm | L_IR: %d | R_IR: %d\n",
      autoMode ? "AUTO" : "MANUAL",
      currentMovement.c_str(),
      motorSpeed,
      dist,
      leftBlocked(),
      rightBlocked()
    );
  }
}
