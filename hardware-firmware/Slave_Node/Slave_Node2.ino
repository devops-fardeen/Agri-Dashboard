#include <Arduino.h>
#include <Wire.h>
#include <LoRa.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// =====================================================
// NODE CONFIGURATION
// =====================================================

// Slave 1 = 1
// Slave 2 = 2

#define NODE_ID 2

// =====================================================
// SHT30
// =====================================================

#define I2C_SDA 21
#define I2C_SCL 22

#define SHT30_ADDR 0x44

// =====================================================
// SOIL MOISTURE SENSOR
// =====================================================

#define SOIL_MOISTURE_PIN 34

// =====================================================
// DS18B20 SOIL TEMPERATURE
// =====================================================

#define DS18B20_PIN 4

OneWire oneWire(DS18B20_PIN);
DallasTemperature soilTempSensor(&oneWire);

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
// TIMING
// =====================================================

unsigned long lastSendTime = 0;

const unsigned long SEND_INTERVAL = 5000;

// =====================================================
// SENSOR VARIABLES
// =====================================================

float airTemperature = 0;
float airHumidity = 0;
float soilTemperature = 0;

int soilMoistureRaw = 0;
int soilMoisturePercent = 0;

// =====================================================
// SHT30 CRC
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
  Wire.write(0x06);

  if (Wire.endTransmission() != 0) {
    return false;
  }

  delay(20);

  Wire.requestFrom(SHT30_ADDR, 6);

  if (Wire.available() != 6) {
    return false;
  }

  uint8_t data[6];

  for (int i = 0; i < 6; i++) {
    data[i] = Wire.read();
  }

  if (sht30CRC(data, 2) != data[2]) {
    return false;
  }

  if (sht30CRC(data + 3, 2) != data[5]) {
    return false;
  }

  uint16_t rawTemperature =
    ((uint16_t)data[0] << 8) | data[1];

  uint16_t rawHumidity =
    ((uint16_t)data[3] << 8) | data[4];

  temperature =
    -45.0 + 175.0 * ((float)rawTemperature / 65535.0);

  humidity =
    100.0 * ((float)rawHumidity / 65535.0);

  return true;
}

// =====================================================
// READ SOIL MOISTURE
// =====================================================

void readSoilMoisture() {

  soilMoistureRaw = analogRead(SOIL_MOISTURE_PIN);

  // IMPORTANT:
  // Calibrate these values for your sensor.
  //
  // Dry soil usually gives a higher reading
  // Wet soil usually gives a lower reading
  //
  // Change these after testing.

  const int DRY_VALUE = 3200;
  const int WET_VALUE = 1300;

  soilMoisturePercent = map(
    soilMoistureRaw,
    DRY_VALUE,
    WET_VALUE,
    0,
    100
  );

  soilMoisturePercent =
    constrain(soilMoisturePercent, 0, 100);
}

// =====================================================
// READ SOIL TEMPERATURE
// =====================================================

void readSoilTemperature() {

  soilTempSensor.requestTemperatures();

  soilTemperature =
    soilTempSensor.getTempCByIndex(0);
}

// =====================================================
// SEND LORA DATA
// =====================================================

void sendLoRaData() {

  LoRa.beginPacket();

  LoRa.print("NODE=");
  LoRa.print(NODE_ID);

  LoRa.print(",T=");
  LoRa.print(airTemperature, 2);

  LoRa.print(",H=");
  LoRa.print(airHumidity, 2);

  LoRa.print(",SM=");
  LoRa.print(soilMoisturePercent);

  LoRa.print(",SMRAW=");
  LoRa.print(soilMoistureRaw);

  LoRa.print(",ST=");
  LoRa.print(soilTemperature, 2);

  LoRa.endPacket();

  Serial.println("================================");
  Serial.print("Sent from Slave Node ");
  Serial.println(NODE_ID);

  Serial.print("Air Temperature: ");
  Serial.print(airTemperature);
  Serial.println(" °C");

  Serial.print("Air Humidity: ");
  Serial.print(airHumidity);
  Serial.println(" %");

  Serial.print("Soil Moisture: ");
  Serial.print(soilMoisturePercent);
  Serial.println(" %");

  Serial.print("Soil Moisture Raw: ");
  Serial.println(soilMoistureRaw);

  Serial.print("Soil Temperature: ");
  Serial.print(soilTemperature);
  Serial.println(" °C");

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
  Serial.print("SIH 2026 SLAVE NODE ");
  Serial.println(NODE_ID);
  Serial.println("================================");

  // ADC configuration
  analogReadResolution(12);

  analogSetPinAttenuation(
    SOIL_MOISTURE_PIN,
    ADC_11db
  );

  // I2C
  Wire.begin(I2C_SDA, I2C_SCL);

  // DS18B20
  soilTempSensor.begin();

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

  Serial.println("Slave node ready");

}

// =====================================================
// LOOP
// =====================================================

void loop() {

  if (millis() - lastSendTime >= SEND_INTERVAL) {

    lastSendTime = millis();

    // Read sensors

    bool shtOK =
      readSHT30(airTemperature, airHumidity);

    if (!shtOK) {

      Serial.println("SHT30 read failed!");

      airTemperature = -999;
      airHumidity = -999;

    }

    readSoilMoisture();

    readSoilTemperature();

    // Send data

    sendLoRaData();

  }

}