#include <Arduino.h>
#include <Wire.h>
#include <LoRa.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// =====================================================
// NODE CONFIGURATION
// Slave 1 = 1, Slave 2 = 2
// =====================================================
#define NODE_ID 1

// =====================================================
// SHT30 AIR TEMPERATURE & HUMIDITY (I2C)
// =====================================================
#define I2C_SDA 21
#define I2C_SCL 22
#define SHT30_ADDR 0x44  // Change to 0x45 if ADDR is pulled HIGH

// =====================================================
// SOIL MOISTURE SENSOR (ADC1)
// =====================================================
#define SOIL_MOISTURE_PIN 34

// =====================================================
// DS18B20 SOIL TEMPERATURE (OneWire)
// Requires 4.7kΩ pull-up resistor between GPIO 4 and 3.3V
// =====================================================
#define DS18B20_PIN 4

OneWire oneWire(DS18B20_PIN);
DallasTemperature soilTempSensor(&oneWire);

// =====================================================
// LORA SX1278 RA-02 (SPI)
// =====================================================
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_SS     5
#define LORA_RST   14
#define LORA_DIO0  26
#define LORA_FREQUENCY 433E6

// =====================================================
// TIMING & SENSOR VARIABLES
// =====================================================
unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL = 4000; // ms

float airTemperature = -999.0;
float airHumidity = -999.0;
float soilTemperature = -999.0;
int soilMoistureRaw = -1;
int soilMoisturePercent = -1;

// =====================================================
// SHT30 CRC CHECK
// =====================================================
uint8_t sht30CRC(uint8_t *data, uint8_t length) {
  uint8_t crc = 0xFF;
  for (uint8_t i = 0; i < length; i++) {
    crc ^= data[i];
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x80) {
        crc = (crc << 1) ^ 0x31;
      } else {
        crc <<= 1;
      }
    }
  }
  return crc;
}

// =====================================================
// READ SHT30
// =====================================================
bool readSHT30(float &temperature, float &humidity) {
  Wire.beginTransmission(SHT30_ADDR);
  Wire.write(0x2C);
  Wire.write(0x06); // High repeatability measurement
  if (Wire.endTransmission() != 0) {
    return false;
  }

  delay(25);
  Wire.requestFrom((uint8_t)SHT30_ADDR, (uint8_t)6);
  if (Wire.available() != 6) {
    return false;
  }

  uint8_t data[6];
  for (int i = 0; i < 6; i++) {
    data[i] = Wire.read();
  }

  if (sht30CRC(data, 2) != data[2] || sht30CRC(data + 3, 2) != data[5]) {
    return false;
  }

  uint16_t rawT = ((uint16_t)data[0] << 8) | data[1];
  uint16_t rawH = ((uint16_t)data[3] << 8) | data[4];

  temperature = -45.0 + 175.0 * ((float)rawT / 65535.0);
  humidity = 100.0 * ((float)rawH / 65535.0);
  humidity = constrain(humidity, 0.0, 100.0);
  return true;
}

// =====================================================
// READ SOIL MOISTURE
// =====================================================
void readSoilMoisture() {
  long sum = 0;
  for (int i = 0; i < 16; i++) {
    sum += analogRead(SOIL_MOISTURE_PIN);
    delayMicroseconds(50);
  }
  soilMoistureRaw = sum / 16;

  // Detect disconnected or floating sensor
  if (soilMoistureRaw < 100 || soilMoistureRaw > 4050) {
    soilMoisturePercent = -1; // Disconnected indicator
    return;
  }

  // Calibration points:
  // In air / Dry = ~3200
  // In water / Wet = ~1300
  const int DRY_VALUE = 3200;
  const int WET_VALUE = 1300;
  soilMoisturePercent = map(soilMoistureRaw, DRY_VALUE, WET_VALUE, 0, 100);
  soilMoisturePercent = constrain(soilMoisturePercent, 0, 100);
}

// =====================================================
// READ SOIL TEMPERATURE
// =====================================================
void readSoilTemperature() {
  soilTempSensor.requestTemperatures();
  float t = soilTempSensor.getTempCByIndex(0);
  // DS18B20 returns -127 or 85 on read errors
  if (t <= -126.0 || t >= 85.0 || t == 0.00) {
    soilTemperature = -999.0; // Disconnected indicator
  } else {
    soilTemperature = t;
  }
}

// =====================================================
// SEND LORA PACKET
// =====================================================
void sendLoRaData() {
  LoRa.beginPacket();
  LoRa.printf("NODE=%d,T=%.2f,H=%.2f,SM=%d,SMRAW=%d,ST=%.2f",
    NODE_ID,
    airTemperature,
    airHumidity,
    soilMoisturePercent,
    soilMoistureRaw,
    soilTemperature
  );
  LoRa.endPacket();

  Serial.println("================================");
  Serial.printf(">> [TX LORA NODE %d]\n", NODE_ID);
  Serial.printf("Air Temp:  %s °C\n", (airTemperature > -900) ? String(airTemperature, 2).c_str() : "--");
  Serial.printf("Humidity:  %s %%\n", (airHumidity > -900) ? String(airHumidity, 2).c_str() : "--");
  Serial.printf("Soil Moist: %s %% (Raw: %d)\n", (soilMoisturePercent >= 0) ? String(soilMoisturePercent).c_str() : "--", soilMoistureRaw);
  Serial.printf("Soil Temp: %s °C\n", (soilTemperature > -900) ? String(soilTemperature, 2).c_str() : "--");
  Serial.println("================================");
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(600);

  Serial.println("\n================================");
  Serial.printf("  AGRISMART SLAVE NODE %d INITIALIZING\n", NODE_ID);
  Serial.println("================================");

  analogReadResolution(12);
  analogSetPinAttenuation(SOIL_MOISTURE_PIN, ADC_11db);

  Wire.begin(I2C_SDA, I2C_SCL);
  soilTempSensor.begin();

  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  Serial.println("Starting LoRa Radio at 433 MHz...");

  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("[ERROR] LoRa Radio Initialization FAILED!");
    Serial.println("Check SPI wiring: SCK=18, MISO=19, MOSI=23, NSS=5, RST=14, DIO0=26");
    while (true) {
      delay(1000);
    }
  }

  LoRa.setTxPower(17);
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.enableCrc();

  Serial.println("✓ LoRa Radio Initialized Successfully!");
  Serial.printf("✓ SLAVE NODE %d READY — Broadcasting every 4s\n", NODE_ID);
}

// =====================================================
// MAIN LOOP
// =====================================================
void loop() {
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();

    // 1. Read SHT30
    if (!readSHT30(airTemperature, airHumidity)) {
      airTemperature = -999.0;
      airHumidity = -999.0;
    }

    // 2. Read Soil Moisture & Soil Temperature
    readSoilMoisture();
    readSoilTemperature();

    // 3. Transmit to Master ESP32 Gateway
    sendLoRaData();
  }
}