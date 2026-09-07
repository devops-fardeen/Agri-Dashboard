#include <WiFi.h>
#include <WebServer.h>

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
// PWM CONFIGURATION
// =====================================================
#define PWM_FREQ       1000
#define PWM_RESOLUTION 8

int motorSpeed = 190;

// =====================================================
// BATTERY CALIBRATION (3S LiPo: 11.1V - 12.6V)
// =====================================================
float voltageCalibration = 5.00;

// =====================================================
// AUTONOMOUS CROP ROW FOLLOWING MODE
// =====================================================
const float FRONT_OBSTACLE_DISTANCE = 30.0; // cm

bool autoMode = false;
bool autoTurning = false;
unsigned long autoTurnStart = 0;
const unsigned long AUTO_TURN_TIME = 450; // ms for turn evasion

unsigned long lastAutoCheck = 0;
const unsigned long AUTO_CHECK_INTERVAL = 60; // ms

String currentMovement = "STOP";

unsigned long lastWiFiReconnectAttempt = 0;
const unsigned long WIFI_RECONNECT_INTERVAL = 5000;

// =====================================================
// PWM SETUP
// =====================================================
void setupPWM() {
  ledcAttach(LEFT_RPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(LEFT_LPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(RIGHT_RPWM, PWM_FREQ, PWM_RESOLUTION);
  ledcAttach(RIGHT_LPWM, PWM_FREQ, PWM_RESOLUTION);

  ledcWrite(LEFT_RPWM, 0);
  ledcWrite(LEFT_LPWM, 0);
  ledcWrite(RIGHT_RPWM, 0);
  ledcWrite(RIGHT_LPWM, 0);
}

// =====================================================
// MOTOR CONTROL PRIMITIVES (BTS7960)
// =====================================================
void leftForward(int speed) {
  speed = constrain(speed, 0, 255);
  ledcWrite(LEFT_RPWM, speed);
  ledcWrite(LEFT_LPWM, 0);
}

void leftBackward(int speed) {
  speed = constrain(speed, 0, 255);
  ledcWrite(LEFT_RPWM, 0);
  ledcWrite(LEFT_LPWM, speed);
}

void rightForward(int speed) {
  speed = constrain(speed, 0, 255);
  ledcWrite(RIGHT_RPWM, speed);
  ledcWrite(RIGHT_LPWM, 0);
}

void rightBackward(int speed) {
  speed = constrain(speed, 0, 255);
  ledcWrite(RIGHT_RPWM, 0);
  ledcWrite(RIGHT_LPWM, speed);
}

void stopMotors() {
  ledcWrite(LEFT_RPWM, 0);
  ledcWrite(LEFT_LPWM, 0);
  ledcWrite(RIGHT_RPWM, 0);
  ledcWrite(RIGHT_LPWM, 0);
  currentMovement = "STOP";
}

// =====================================================
// DIRECTIONAL MOVEMENTS
// =====================================================
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
// ULTRASONIC DISTANCE SENSOR (HC-SR04)
// =====================================================
float getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 25000); // 25ms timeout (~4m max)
  if (duration == 0) return 999.0;
  return (duration * 0.0343 / 2.0);
}

// =====================================================
// INFRARED OBSTACLE SENSORS
// =====================================================
bool leftBlocked() {
  return digitalRead(LEFT_IR) == LOW;
}

bool rightBlocked() {
  return digitalRead(RIGHT_IR) == LOW;
}

// =====================================================
// BATTERY VOLTAGE MONITOR (ADC)
// =====================================================
float getBatteryVoltage() {
  int raw = analogRead(BATTERY_PIN);
  float voltage = (raw / 4095.0) * 3.3;
  voltage *= voltageCalibration;
  return voltage;
}

// =====================================================
// CONTINUOUS AUTONOMOUS ROW FOLLOWING & EVASION
// =====================================================
void automaticMode() {
  unsigned long now = millis();

  // Handle active timed turn for collision avoidance
  if (autoTurning) {
    if (now - autoTurnStart >= AUTO_TURN_TIME) {
      autoTurning = false;
      // Immediately resume continuous forward drive after turn!
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

  // Front obstacle auto-evasion (< 30 cm)
  if (distance > 1.0 && distance < FRONT_OBSTACLE_DISTANCE) {
    if (!leftObstacle && rightObstacle) {
      turnLeft();
      autoTurning = true;
      autoTurnStart = now;
      currentMovement = "AUTO-AVOID-LEFT";
    } else if (!rightObstacle && leftObstacle) {
      turnRight();
      autoTurning = true;
      autoTurnStart = now;
      currentMovement = "AUTO-AVOID-RIGHT";
    } else {
      turnRight();
      autoTurning = true;
      autoTurnStart = now;
      currentMovement = "AUTO-AVOID-RIGHT";
    }
    return;
  }

  // Crop row boundary following via IR sensors
  if (leftObstacle && !rightObstacle) {
    // Left row detected -> steer gently right without stopping
    leftForward(motorSpeed);
    rightForward((int)(motorSpeed * 0.55));
    currentMovement = "AUTO-NUDGE-RIGHT";
  } else if (rightObstacle && !leftObstacle) {
    // Right row detected -> steer gently left without stopping
    leftForward((int)(motorSpeed * 0.55));
    rightForward(motorSpeed);
    currentMovement = "AUTO-NUDGE-LEFT";
  } else {
    // Both sides clear or centered -> continuous forward drive!
    moveForward();
    currentMovement = "AUTO-FORWARD";
  }
}

// =====================================================
// API ROUTE HANDLERS
// =====================================================
void handleRoot() {
  String message = "================================\n";
  message += "       AGRI ROVER ONLINE\n";
  message += "================================\n";
  message += "IP: " + WiFi.localIP().toString() + "\n";
  message += "RSSI: " + String(WiFi.RSSI()) + " dBm\n";
  message += "Movement: " + currentMovement + "\n";
  message += "Speed: " + String(motorSpeed) + "\n";
  message += "Auto Mode: " + String(autoMode ? "ON" : "OFF") + "\n";
  message += "Battery Voltage: " + String(getBatteryVoltage(), 2) + " V\n";
  message += "Distance: " + String(getDistance(), 1) + " cm\n";
  message += "================================\n";

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "text/plain", message);
}

void handleCommand() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  if (!server.hasArg("move")) {
    server.send(400, "text/plain", "Missing move argument");
    return;
  }

  String command = server.arg("move");
  command.toLowerCase();
  command.trim();

  Serial.print("Received Rover Command: ");
  Serial.println(command);

  // Manual continuous navigation:
  // Starts immediately and keeps running until STOP or next command!
  if (command == "forward" || command == "start" || command == "move_forward") {
    autoMode = false;
    autoTurning = false;
    moveForward();
  } else if (command == "backward" || command == "move_backward") {
    autoMode = false;
    autoTurning = false;
    moveBackward();
  } else if (command == "left" || command == "move_left") {
    autoMode = false;
    autoTurning = false;
    turnLeft();
  } else if (command == "right" || command == "move_right") {
    autoMode = false;
    autoTurning = false;
    turnRight();
  } else if (command == "stop") {
    autoMode = false;
    autoTurning = false;
    stopMotors();
  } else if (command == "auto_on" || command == "auto") {
    autoMode = true;
    autoTurning = false;
    currentMovement = "AUTO-FORWARD";
    moveForward(); // Start moving forward immediately in Auto Mode!
  } else if (command == "auto_off") {
    autoMode = false;
    autoTurning = false;
    stopMotors();
  } else {
    server.send(400, "text/plain", "Unknown command");
    return;
  }

  server.send(200, "text/plain", "OK");
}

void handleSpeed() {
  server.sendHeader("Access-Control-Allow-Origin", "*");

  if (!server.hasArg("value")) {
    server.send(400, "text/plain", "Missing value argument");
    return;
  }

  int newSpeed = server.arg("value").toInt();
  motorSpeed = constrain(newSpeed, 60, 255);
  Serial.print("Speed Updated: ");
  Serial.println(motorSpeed);

  // Apply speed immediately to active movement
  if (currentMovement == "FORWARD" || currentMovement == "AUTO" || currentMovement == "AUTO-FORWARD") {
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

  // Approximate 3S LiPo percentage (9.6V empty -> 12.6V full)
  int batteryPct = constrain((int)(((battery - 9.6) / 3.0) * 100), 0, 100);

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

  String json = "{";
  json += "\"device\":\"AGRI_ROVER\"";
  json += ",\"status\":\"ONLINE\"";
  json += ",\"ip\":\"" + WiFi.localIP().toString() + "\"";
  json += ",\"rssi\":" + String(WiFi.RSSI());
  json += ",\"uptime_ms\":" + String(millis());
  json += "}";

  server.send(200, "application/json", json);
}

// =====================================================
// WIFI CONNECTION (Phone Hotspot)
// =====================================================
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(500);

  Serial.println();
  Serial.println("==============================");
  Serial.println("Connecting Rover to Hotspot...");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);
  Serial.println("==============================");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("==============================");
    Serial.println("       AGRI ROVER READY");
    Serial.println("==============================");
    Serial.print("Rover IP:  "); Serial.println(WiFi.localIP());
    Serial.print("Gateway:   "); Serial.println(WiFi.gatewayIP());
    Serial.print("RSSI:      "); Serial.print(WiFi.RSSI()); Serial.println(" dBm");
    Serial.println("==============================");
  } else {
    Serial.println("WIFI CONNECTION FAILED - Will retry in loop");
  }
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("        AGRI ROVER BOOT");
  Serial.println("================================");

  pinMode(LEFT_IR, INPUT);
  pinMode(RIGHT_IR, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BATTERY_PIN, INPUT);

  setupPWM();
  stopMotors();
  connectWiFi();

  // Register API Endpoints
  server.on("/", handleRoot);
  server.on("/cmd", handleCommand);
  server.on("/speed", handleSpeed);
  server.on("/heartbeat", handleHeartbeat);
  server.on("/telemetry", handleTelemetry);
  server.on("/status", handleStatus);

  server.enableCORS(true);
  server.begin();

  Serial.println("✓ Rover WebServer API started on Port 80");
}

// =====================================================
// MAIN CONTROL LOOP
// =====================================================
void loop() {
  server.handleClient();

  // Wi-Fi Connection Monitor
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long now = millis();
    if (now - lastWiFiReconnectAttempt >= WIFI_RECONNECT_INTERVAL) {
      lastWiFiReconnectAttempt = now;
      Serial.println("WiFi lost. Attempting reconnect to hotspot...");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    return;
  }

  // Continuous Autonomous Execution
  if (autoMode) {
    automaticMode();
  }
}
