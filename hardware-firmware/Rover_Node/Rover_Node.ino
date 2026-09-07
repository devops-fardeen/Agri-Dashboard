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

int motorSpeed = 180;

// =====================================================
// BATTERY CALIBRATION (3S LiPo: 11.1V - 12.6V)
// =====================================================
float voltageCalibration = 5.00;

// =====================================================
// AUTONOMOUS CROP ROW FOLLOWING MODE
// =====================================================
const float FRONT_STOP_DISTANCE = 35.0;

bool autoMode = false;
bool autoTurning = false;
unsigned long autoTurnStart = 0;
const unsigned long AUTO_TURN_TIME = 450;

unsigned long lastAutoCheck = 0;
const unsigned long AUTO_CHECK_INTERVAL = 80;

// =====================================================
// PI COMMUNICATION WATCHDOG & HEARTBEAT
// =====================================================
unsigned long lastPiHeartbeat = 0;
const unsigned long PI_TIMEOUT = 3000;

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
// LEFT MOTOR (BTS7960)
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

// =====================================================
// RIGHT MOTOR (BTS7960)
// =====================================================
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

// =====================================================
// STOP
// =====================================================
void stopMotors() {
  ledcWrite(LEFT_RPWM, 0);
  ledcWrite(LEFT_LPWM, 0);
  ledcWrite(RIGHT_RPWM, 0);
  ledcWrite(RIGHT_LPWM, 0);
  currentMovement = "STOP";
}

// =====================================================
// MANUAL STEERING MOVEMENTS
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

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
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
// AUTOMATIC ROW FOLLOWING & COLLISION AVOIDANCE
// =====================================================
void automaticMode() {
  unsigned long now = millis();

  // Handle active timed turn
  if (autoTurning) {
    if (now - autoTurnStart >= AUTO_TURN_TIME) {
      stopMotors();
      autoTurning = false;
    }
    return;
  }

  // Periodic sensor checks
  if (now - lastAutoCheck < AUTO_CHECK_INTERVAL) return;
  lastAutoCheck = now;

  float distance = getDistance();
  bool leftObstacle = leftBlocked();
  bool rightObstacle = rightBlocked();

  // Front obstacle auto-evasion
  if (distance < FRONT_STOP_DISTANCE) {
    stopMotors();

    if (!leftObstacle && rightObstacle) {
      turnLeft();
      autoTurning = true;
      autoTurnStart = now;
    } else if (!rightObstacle && leftObstacle) {
      turnRight();
      autoTurning = true;
      autoTurnStart = now;
    } else if (!leftObstacle && !rightObstacle) {
      turnLeft();
      autoTurning = true;
      autoTurnStart = now;
    } else {
      stopMotors();
    }
    return;
  }

  // Row edge alignment
  if (leftObstacle && !rightObstacle) {
    leftForward(110);
    rightForward(motorSpeed);
    currentMovement = "AUTO-RIGHT";
  } else if (rightObstacle && !leftObstacle) {
    leftForward(motorSpeed);
    rightForward(110);
    currentMovement = "AUTO-LEFT";
  } else if (!leftObstacle && !rightObstacle) {
    moveForward();
  } else {
    stopMotors();
  }
}

void updateHeartbeat() {
  lastPiHeartbeat = millis();
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

  server.send(200, "text/plain", message);
}

void handleCommand() {
  if (!server.hasArg("move")) {
    server.send(400, "text/plain", "Missing command");
    return;
  }

  String command = server.arg("move");
  command.toLowerCase();
  updateHeartbeat();

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
    stopMotors();
    currentMovement = "AUTO";
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
  if (!server.hasArg("value")) {
    server.send(400, "text/plain", "Missing speed");
    return;
  }

  int newSpeed = server.arg("value").toInt();
  motorSpeed = constrain(newSpeed, 50, 255);
  updateHeartbeat();
  server.send(200, "text/plain", "SPEED OK");
}

void handleHeartbeat() {
  updateHeartbeat();
  server.send(200, "text/plain", "ALIVE");
}

void handleTelemetry() {
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

  // API Route Registrations
  server.on("/", handleRoot);
  server.on("/cmd", handleCommand);
  server.on("/speed", handleSpeed);
  server.on("/heartbeat", handleHeartbeat);
  server.on("/telemetry", handleTelemetry);
  server.on("/status", handleStatus);

  server.begin();
  lastPiHeartbeat = millis();

  Serial.println("✓ Rover WebServer API started on Port 80");
}

// =====================================================
// MAIN CONTROL LOOP
// =====================================================
void loop() {
  server.handleClient();

  // Wi-Fi Reconnect Handling
  if (WiFi.status() != WL_CONNECTED) {
    stopMotors();
    autoMode = false;
    autoTurning = false;
    currentMovement = "WIFI LOST";

    unsigned long now = millis();
    if (now - lastWiFiReconnectAttempt >= WIFI_RECONNECT_INTERVAL) {
      lastWiFiReconnectAttempt = now;
      Serial.println("WiFi lost. Attempting reconnect to hotspot...");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    return;
  }

  // Safety Watchdog (Auto-stop if Pi does not send heartbeat)
  if (millis() - lastPiHeartbeat > PI_TIMEOUT) {
    stopMotors();
    autoMode = false;
    autoTurning = false;
    currentMovement = "SAFETY STOP";
  }

  // Autonomous Mode execution
  if (autoMode) {
    automaticMode();
  }
}
