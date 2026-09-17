#include <Arduino.h>
#include <Wire.h>
#include <LoRa.h>
#include <BH1750.h>
#include <Adafruit_BMP280.h>

// =====================================================
// I2C
// =====================================================

#define I2C_SDA 21
#define I2C_SCL 22

// =====================================================
// RAIN SENSOR
// =====================================================

#define RAIN_SENSOR_PIN 32

// =====================================================
// WATER LEVEL SENSOR
// =====================================================

#define WATER_LEVEL_PIN 34

// =====================================================
// RELAYS
// =====================================================

#define RELAY1_PIN 25
#define RELAY2_PIN 27

// Many relay modules are active LOW.
// Change to false if your relay is active HIGH.

#define RELAY_ACTIVE_LOW true

// =====================================================
// LORA SX1278 RA-02
// =====================================================

#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_SS     5
#define LORA_RST   14
#define LORA_DIO0  26

#define LORA_FREQUENCY 433E6

// =====================================================
// SENSOR OBJECTS
// =====================================================

BH1750 lightSensor;

Adafruit_BMP280 bmp;

// =====================================================
// SENSOR VALUES
// =====================================================

int rainRaw = 0;
int waterLevelRaw = 0;

float lightLux = 0;
float pressure = 0;
float bmpTemperature = 0;

// =====================================================
// SLAVE DATA STRUCTURE
// =====================================================

struct SlaveData {

  int nodeID;

  float airTemperature;
  float airHumidity;

  int soilMoisture;
  int soilMoistureRaw;

  float soilTemperature;

  int rssi;

  unsigned long lastReceived;

  bool received;

};

// =====================================================
// TWO SLAVE NODES
// =====================================================

SlaveData slave1 = {
  1,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  false
};

SlaveData slave2 = {
  2,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  false
};

// =====================================================
// RELAY CONTROL
// =====================================================

void setRelay(int pin, bool on) {

  if (RELAY_ACTIVE_LOW) {

    digitalWrite(pin, on ? LOW : HIGH);

  } else {

    digitalWrite(pin, on ? HIGH : LOW);

  }

}

// =====================================================
// READ LOCAL SENSORS
// =====================================================

void readLocalSensors() {

  rainRaw =
    analogRead(RAIN_SENSOR_PIN);

  waterLevelRaw =
    analogRead(WATER_LEVEL_PIN);

  lightLux =
    lightSensor.readLightLevel();

  bmpTemperature =
    bmp.readTemperature();

  pressure =
    bmp.readPressure() / 100.0F;

}

// =====================================================
// PRINT LOCAL SENSORS
// =====================================================

void printLocalSensors() {

  Serial.println();
  Serial.println("========== MASTER SENSORS ==========");

  Serial.print("Rain Raw: ");
  Serial.println(rainRaw);

  Serial.print("Water Level Raw: ");
  Serial.println(waterLevelRaw);

  Serial.print("Light: ");
  Serial.print(lightLux);
  Serial.println(" lux");

  Serial.print("BMP Temperature: ");
  Serial.print(bmpTemperature);
  Serial.println(" °C");

  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  Serial.println("====================================");

}

// =====================================================
// PARSE SLAVE PACKET
// =====================================================

bool parseSlavePacket(String packet) {

  int nodeID;

  float airT;
  float airH;

  int soilM;
  int soilRaw;

  float soilT;

  int parsed = sscanf(
    packet.c_str(),
    "NODE=%d,T=%f,H=%f,SM=%d,SMRAW=%d,ST=%f",
    &nodeID,
    &airT,
    &airH,
    &soilM,
    &soilRaw,
    &soilT
  );

  if (parsed != 6) {

    Serial.println("Invalid LoRa packet:");
    Serial.println(packet);

    return false;

  }

  SlaveData *node = nullptr;

  if (nodeID == 1) {

    node = &slave1;

  } else if (nodeID == 2) {

    node = &slave2;

  } else {

    Serial.print("Unknown node ID: ");
    Serial.println(nodeID);

    return false;

  }

  node->nodeID = nodeID;

  node->airTemperature = airT;

  node->airHumidity = airH;

  node->soilMoisture = soilM;

  node->soilMoistureRaw = soilRaw;

  node->soilTemperature = soilT;

  node->rssi = LoRa.packetRssi();

  node->lastReceived = millis();

  node->received = true;

  return true;

}

// =====================================================
// PRINT SLAVE DATA
// =====================================================

void printSlaveData(SlaveData &node) {

  Serial.println();

  Serial.print("========== SLAVE NODE ");
  Serial.print(node.nodeID);
  Serial.println(" ==========");

  Serial.print("Air Temperature: ");
  Serial.print(node.airTemperature);
  Serial.println(" °C");

  Serial.print("Air Humidity: ");
  Serial.print(node.airHumidity);
  Serial.println(" %");

  Serial.print("Soil Moisture: ");
  Serial.print(node.soilMoisture);
  Serial.println(" %");

  Serial.print("Soil Raw: ");
  Serial.println(node.soilMoistureRaw);

  Serial.print("Soil Temperature: ");
  Serial.print(node.soilTemperature);
  Serial.println(" °C");

  Serial.print("LoRa RSSI: ");
  Serial.print(node.rssi);
  Serial.println(" dBm");

  Serial.println("====================================");

}

// =====================================================
// RECEIVE LORA
// =====================================================

void receiveLoRa() {

  int packetSize = LoRa.parsePacket();

  if (!packetSize) {
    return;
  }

  String packet = "";

  while (LoRa.available()) {

    packet += (char)LoRa.read();

  }

  Serial.println();
  Serial.print("Received: ");
  Serial.println(packet);

  if (parseSlavePacket(packet)) {

    if (packet.indexOf("NODE=1") >= 0) {

      printSlaveData(slave1);

    }

    if (packet.indexOf("NODE=2") >= 0) {

      printSlaveData(slave2);

    }

  }

}

// =====================================================
// IRRIGATION LOGIC
// =====================================================

// This is a simple prototype control logic.
//
// IMPORTANT:
// Calibrate soil moisture and rain thresholds.
// Do not use this to operate pumps unattended
// until you test the relay and sensor behavior.

void irrigationControl() {

  bool rainDetected = rainRaw < 1500;

  // Check each node separately.
  // If a node has not sent data recently,
  // keep its pump OFF.

  bool node1Online =
    slave1.received &&
    (millis() - slave1.lastReceived < 30000);

  bool node2Online =
    slave2.received &&
    (millis() - slave2.lastReceived < 30000);

  bool pump1On = false;
  bool pump2On = false;

  if (node1Online && !rainDetected) {

    if (slave1.soilMoisture < 30) {

      pump1On = true;

    }

  }

  if (node2Online && !rainDetected) {

    if (slave2.soilMoisture < 30) {

      pump2On = true;

    }

  }

  setRelay(RELAY1_PIN, pump1On);

  setRelay(RELAY2_PIN, pump2On);

  Serial.println();
  Serial.println("========== IRRIGATION ==========");

  Serial.print("Rain Detected: ");
  Serial.println(rainDetected ? "YES" : "NO");

  Serial.print("Pump 1: ");
  Serial.println(pump1On ? "ON" : "OFF");

  Serial.print("Pump 2: ");
  Serial.println(pump2On ? "ON" : "OFF");

  Serial.println("================================");

}

// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("SIH 2026 MASTER NODE");
  Serial.println("================================");

  // ADC
  analogReadResolution(12);

  analogSetPinAttenuation(
    RAIN_SENSOR_PIN,
    ADC_11db
  );

  analogSetPinAttenuation(
    WATER_LEVEL_PIN,
    ADC_11db
  );

  // Relay setup
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);

  // Start with pumps OFF
  setRelay(RELAY1_PIN, false);
  setRelay(RELAY2_PIN, false);

  // I2C
  Wire.begin(I2C_SDA, I2C_SCL);

  // BH1750
  if (lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {

    Serial.println("GY-302 initialized");

  } else {

    Serial.println("GY-302 initialization FAILED");

  }

  // BMP280
  if (bmp.begin(0x76)) {

    Serial.println("BMP280 initialized");

  } else if (bmp.begin(0x77)) {

    Serial.println("BMP280 initialized at 0x77");

  } else {

    Serial.println("BMP280 initialization FAILED");

  }

  // LoRa
  LoRa.setPins(
    LORA_SS,
    LORA_RST,
    LORA_DIO0
  );

  Serial.println("Starting LoRa...");

  if (!LoRa.begin(LORA_FREQUENCY)) {

    Serial.println("LoRa initialization FAILED!");

    while (true) {
      delay(1000);
    }

  }

  LoRa.setTxPower(17);

  LoRa.setSpreadingFactor(7);

  LoRa.setSignalBandwidth(125E3);

  LoRa.setCodingRate4(5);

  LoRa.enableCrc();

  Serial.println("LoRa initialized successfully");

  Serial.println("MASTER NODE READY");

}

// =====================================================
// LOOP
// =====================================================

void loop() {

  receiveLoRa();

  static unsigned long lastSensorRead = 0;

  static unsigned long lastIrrigation = 0;

  if (millis() - lastSensorRead >= 5000) {

    lastSensorRead = millis();

    readLocalSensors();

    printLocalSensors();

  }

  if (millis() - lastIrrigation >= 5000) {

    lastIrrigation = millis();

    irrigationControl();

  }

}