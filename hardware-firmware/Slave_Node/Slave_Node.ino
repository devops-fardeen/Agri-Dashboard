#include <WiFi.h>
#include <esp_now.h>
#include "DHT.h"

// =====================================================
// MASTER ESP32 MAC ADDRESS
// =====================================================
uint8_t masterAddress[] = {
  0x30,
  0x76,
  0xF5,
  0xE4,
  0xBC,
  0xFC
};

// =====================================================
// SENSOR PINS
// =====================================================
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define SOIL_PIN 34

// =====================================================
// DHT SENSOR INSTANCE
// =====================================================
DHT dht(DHT_PIN, DHT_TYPE);

// =====================================================
// DATA STRUCTURE (Must match Master Node)
// =====================================================
typedef struct {
  float temperature;
  float humidity;
  int soilRaw;
  int soilPercent;
} SensorData;

SensorData sensorData;

// =====================================================
// ESP-NOW SEND CALLBACK
// =====================================================
void onDataSent(const wifi_tx_info_t *info, esp_now_send_status_t status) {
  Serial.print("ESP-NOW Status: ");
  if (status == ESP_NOW_SEND_SUCCESS) {
    Serial.println("Data sent successfully ✓");
  } else {
    Serial.println("Data send failed ✗");
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
  Serial.println("       AGRI SLAVE NODE");
  Serial.println("================================");

  // 1. Start Sensors
  dht.begin();
  pinMode(SOIL_PIN, INPUT);

  // 2. WiFi Station Mode
  WiFi.mode(WIFI_STA);
  delay(500);

  Serial.print("Slave MAC: ");
  Serial.println(WiFi.macAddress());

  // 3. Initialize ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW initialization failed");
    while (true) {
      delay(1000);
    }
  }

  // 4. Register Send Callback
  esp_now_register_send_cb(onDataSent);

  // 5. Add Master as Peer
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, masterAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add Master peer");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("✓ Master peer added successfully");
  Serial.println("✓ Slave node ready and transmitting");
}

// =====================================================
// MAIN SENSOR LOOP (2s Polling)
// =====================================================
void loop() {
  // 1. Read DHT11 Temp & Humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // 2. Read Soil Moisture Sensor
  int soilRaw = analogRead(SOIL_PIN);

  // 3. Soil Moisture Percentage (Calibrated 4095 dry -> 1500 wet)
  int soilPercent = map(soilRaw, 4095, 1500, 0, 100);
  soilPercent = constrain(soilPercent, 0, 100);

  // 4. Check Sensor Validity
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("⚠️ Warning: DHT11 reading failed, retrying...");
    delay(2000);
    return;
  }

  // 5. Populate Data Struct
  sensorData.temperature = temperature;
  sensorData.humidity = humidity;
  sensorData.soilRaw = soilRaw;
  sensorData.soilPercent = soilPercent;

  // 6. Debug Print
  Serial.println();
  Serial.println("--- [Field Sensor Data] ---");
  Serial.print("Temperature:   "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Humidity:      "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Soil Raw ADC:  "); Serial.println(soilRaw);
  Serial.print("Soil Moisture: "); Serial.print(soilPercent); Serial.println(" %");

  // 7. Transmit to Master via ESP-NOW
  esp_err_t result = esp_now_send(
    masterAddress,
    (uint8_t *)&sensorData,
    sizeof(sensorData)
  );

  if (result == ESP_OK) {
    Serial.println("📡 Sending sensor packet to Master...");
  } else {
    Serial.print("❌ ESP-NOW send error: ");
    Serial.println(result);
  }

  delay(2000);
}
