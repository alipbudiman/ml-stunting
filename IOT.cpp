#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoBLE.h>
#include "Arduino_LED_Matrix.h"
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>

// === KONFIGURASI WIFI & SERVER ===
const char* ssid = "YOUR_WIFI_SSID";        // Ganti dengan SSID WiFi Anda
const char* password = "YOUR_WIFI_PASSWORD"; // Ganti dengan password WiFi Anda
const char* serverAddress = "192.168.1.100"; // Ganti dengan IP server Anda
const int serverPort = 5000;

WiFiClient wifiClient;
HttpClient httpClient = HttpClient(wifiClient, serverAddress, serverPort);

// === INISIALISASI KOMPONEN ===
LiquidCrystal_I2C lcd(0x27, 12, 2);     // LCD 12x2
ArduinoLEDMatrix matrix;

// === GAMBAR LED MATRIX (ikon timbangan) ===
byte image[8][12] = {
  { 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0 },
  { 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0 },
  { 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0 },
  { 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0 },
  { 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0 },
  { 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 },
  { 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0 },
  { 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0 }
};

// === VARIABEL BERAT ===
float berat = 0.0;
float previousBerat = -1;
bool beratLocked = false;
unsigned long beratLastUpdate = 0;
const unsigned long beratLockDuration = 4000;

// === VARIABEL TINGGI ===
long currentTinggi = 150;
long previousTinggi = -1;
bool tinggiLocked = false;
unsigned long tinggiLastUpdate = 0;
const unsigned long tinggiLockDuration = 4000;

// === STATUS WIFI & PENGIRIMAN DATA ===
bool wifiConnected = false;
bool dataSent = false;
bool dataReset = false;  // Status reset data device

// === PIN HC-SR04 ===
const int trigPin = 3;
const int echoPin = 2;

bool sudahMulai = false;

// === FUNGSI KONEKSI WIFI ===
void connectWiFi() {
  Serial.println("Menghubungkan ke WiFi...");
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connect...");
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println();
    Serial.println("WiFi terhubung!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi OK");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP());
    delay(2000);
  } else {
    wifiConnected = false;
    Serial.println("WiFi gagal terhubung!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Gagal");
    delay(2000);
  }
}

// === KONFIGURASI DEVICE ID ===
const String DEVICE_ID = "IOT_001";  // Ganti dengan ID unik device Anda

// === FUNGSI RESET DATA DEVICE ===
bool resetDeviceData() {
  if (!wifiConnected) {
    Serial.println("WiFi tidak terhubung, tidak bisa reset data");
    return false;
  }
  
  Serial.println("Reset data device...");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Reset Data...");
  
  // Kirim HTTP POST request untuk reset
  httpClient.beginRequest();
  httpClient.post("/reset/" + DEVICE_ID);
  httpClient.sendHeader("Content-Type", "application/json");
  httpClient.endRequest();
  
  // Baca response
  int statusCode = httpClient.responseStatusCode();
  String response = httpClient.responseBody();
  
  Serial.print("Reset Status Code: ");
  Serial.println(statusCode);
  Serial.print("Reset Response: ");
  Serial.println(response);
  
  if (statusCode == 200) {
    lcd.setCursor(0, 1);
    lcd.print("Reset OK!");
    Serial.println("Data device berhasil direset!");
    dataReset = true;  // Set status reset berhasil
    delay(2000);
    return true;
  } else {
    lcd.setCursor(0, 1);
    lcd.print("Reset Gagal!");
    Serial.println("Gagal reset data device!");
    dataReset = false;  // Set status reset gagal
    delay(2000);
    return false;
  }
}

// === FUNGSI KIRIM DATA KE SERVER ===
bool sendDataToServer(float bb, float tb) {
  if (!wifiConnected) {
    Serial.println("WiFi tidak terhubung, tidak bisa kirim data");
    return false;
  }
  
  Serial.println("Mengirim data ke server...");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Kirim Data...");
  
  // Buat JSON payload dengan Device ID
  StaticJsonDocument<300> doc;
  doc["bb"] = bb;
  doc["tb"] = tb;
  doc["did"] = DEVICE_ID;  // Tambahkan Device ID
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.print("JSON Data: ");
  Serial.println(jsonString);
  
  // Kirim HTTP POST request
  httpClient.beginRequest();
  httpClient.post("/recive");
  httpClient.sendHeader("Content-Type", "application/json");
  httpClient.sendHeader("Content-Length", jsonString.length());
  httpClient.beginBody();
  httpClient.print(jsonString);
  httpClient.endRequest();
  
  // Baca response
  int statusCode = httpClient.responseStatusCode();
  String response = httpClient.responseBody();
  
  Serial.print("Status Code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);
  
  if (statusCode == 200) {
    lcd.setCursor(0, 1);
    lcd.print("ID:");
    lcd.print(DEVICE_ID);
    Serial.println("Data berhasil dikirim!");
    delay(2000);
    return true;
  } else {
    lcd.setCursor(0, 1);
    lcd.print("Gagal!");
    Serial.println("Gagal kirim data!");
    delay(2000);
    return false;
  }
}

void setup() {
  Serial.begin(9600);

  // LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sistem Start...");
  delay(1000);

  // LED Matrix
  matrix.begin();
  matrix.renderBitmap(image, 8, 12); // tampilkan ikon timbangan

  // WiFi Connection
  connectWiFi();

  // Reset data device saat startup
  if (wifiConnected) {
    resetDeviceData();
  }

  // BLE
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Hidupkan BLE...");
  
  if (!BLE.begin()) {
    Serial.println("BLE gagal mulai");
    lcd.setCursor(0, 1);
    lcd.print("BLE Gagal");
    while (1);
  }

  lcd.setCursor(0, 1);
  lcd.print("BLE Siap");
  delay(2000);
  lcd.clear();

  // Ultrasonik
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  BLE.scan(); // Mulai scan BLE
  lcd.setCursor(0, 0);
  lcd.print("Siap Ukur...");
  delay(2000);
  lcd.clear();

  sudahMulai = true;
}

void loop() {
  if (!sudahMulai) return;

  // === PROSES TINGGI ===
  if (!tinggiLocked) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH);
    int distance = (duration * 0.034) / 2;
    currentTinggi = 150 - distance;
    if (currentTinggi > 150) currentTinggi = 150;
    if (currentTinggi < 0) currentTinggi = 0;

    if (currentTinggi != previousTinggi) {
      previousTinggi = currentTinggi;
      tinggiLastUpdate = millis();
    }

    lcd.setCursor(0, 0);
    lcd.print("T: ");
    lcd.print(currentTinggi);
    lcd.print("cm   ");
    lcd.setCursor(0, 1);
    lcd.print("Uk.Tinggi...");

    Serial.print("Tinggi: ");
    Serial.print(currentTinggi);
    Serial.println(" cm");

    if (millis() - tinggiLastUpdate >= tinggiLockDuration && previousTinggi > 0) {
      tinggiLocked = true;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Tinggi LOCK");
      Serial.println("Tinggi terkunci");
      delay(1000);
      lcd.clear();
    }

    delay(1000);
    return;
  }

  // === PROSES BERAT ===
  if (!beratLocked) {
    BLEDevice peripheral = BLE.available();
    if (peripheral) {
      String mac = peripheral.address();
      if (mac == "28:29:47:39:32:70") {  // Ganti MAC sesuai milikmu
        uint8_t mfgData[20];
        int len = peripheral.manufacturerData(mfgData, sizeof(mfgData));

        if (len >= 4) {
          uint8_t b1 = mfgData[2];
          uint8_t b2 = mfgData[3];
          int raw = (b1 << 8) | b2;

          int awal = raw / 100;
          int akhir = raw % 100;
          berat = awal + (akhir / 100.0);

          if (berat != previousBerat) {
            previousBerat = berat;
            beratLastUpdate = millis();
          }

          lcd.setCursor(0, 0);
          lcd.print("B: ");
          lcd.print(berat, 2);  // 2 desimal
          lcd.print("kg    ");
          lcd.setCursor(0, 1);
          lcd.print("Uk.Berat...");

          Serial.print("Berat: ");
          Serial.print(berat, 2);
          Serial.println(" kg");
        }
      }
    }

    if (millis() - beratLastUpdate >= beratLockDuration && previousBerat > 0) {
      beratLocked = true;
      matrix.clear();
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Berat LOCK");
      Serial.println("Berat terkunci");
      delay(1000);
      lcd.clear();
    }

    return;
  }

  // === TAMPILKAN HASIL AKHIR ===
  if (tinggiLocked && beratLocked) {
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(currentTinggi);
    lcd.print("cm");

    lcd.setCursor(0, 1);
    lcd.print("B:");
    lcd.print(berat, 2);
    lcd.print("kg");

    Serial.println("=== HASIL AKHIR ===");
    Serial.print("Tinggi: ");
    Serial.print(currentTinggi);
    Serial.println(" cm");
    Serial.print("Berat: ");
    Serial.print(berat, 2);
    Serial.println(" kg");

    delay(3000); // Tampilan hasil 3 detik

    // Kirim data ke server (hanya sekali dan hanya jika reset berhasil)
    if (!dataSent && dataReset) {
      Serial.println("Mengirim data pengukuran ke server...");
      dataSent = sendDataToServer(berat, (float)currentTinggi);
      
      if (dataSent) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Data Terkirim!");
        lcd.setCursor(0, 1);
        lcd.print("Pengukuran OK");
        delay(3000);
      } else {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Kirim Gagal!");
        lcd.setCursor(0, 1);
        lcd.print("Coba Lagi...");
        delay(3000);
      }
    } else if (!dataReset) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Reset Gagal!");
      lcd.setCursor(0, 1);
      lcd.print("Data Tdk Dikirim");
      delay(3000);
    }

    // Tampilkan hasil final
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(currentTinggi);
    lcd.print("cm");
    lcd.setCursor(0, 1);
    lcd.print("B:");
    lcd.print(berat, 2);
    lcd.print("kg");

    delay(4000); // Tampilan akhir 4 detik

    // Reset untuk pengukuran ulang
    tinggiLocked = false;
    beratLocked = false;
    dataSent = false;
    dataReset = false;  // Reset status untuk pengukuran berikutnya
    previousTinggi = -1;
    previousBerat = -1;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Siap Ukur...");
    delay(2000);
    lcd.clear();
    
    // Reset data di server untuk pengukuran berikutnya
    if (wifiConnected) {
      Serial.println("Reset data untuk pengukuran berikutnya...");
      resetDeviceData();
    }
  }
}

/*
=== KONFIGURASI YANG PERLU DISESUAIKAN ===

1. WiFi Credentials:
   - Ganti "YOUR_WIFI_SSID" dengan nama WiFi Anda
   - Ganti "YOUR_WIFI_PASSWORD" dengan password WiFi Anda

2. Server Configuration:
   - Ganti "192.168.1.100" dengan IP address server Anda
   - Pastikan server berjalan di port 5000

3. BLE MAC Address:
   - Ganti "28:29:47:39:32:70" dengan MAC address timbangan BLE Anda

4. Sensor Configuration:
   - Maksimal tinggi diubah dari 200cm menjadi 150cm
   - Pin ultrasonik: Trig=3, Echo=2

=== FLOW SISTEM ===
1. Sistem start dan connect WiFi
2. Reset data device di server (panggil /reset/{did})
3. Inisialisasi BLE dan sensor ultrasonik
4. Ukur tinggi dengan sensor ultrasonik (lock setelah 4 detik stabil)
5. Ukur berat dengan BLE timbangan (lock setelah 4 detik stabil)
6. Tampilkan hasil dan kirim data ke server (hanya jika reset berhasil)
7. Reset untuk pengukuran berikutnya (panggil /reset/{did} lagi)

=== API ENDPOINT ===
POST /reset/{did} - Reset data device sebelum pengukuran
POST /recive       - Kirim data pengukuran
Content-Type: application/json
Body: {"bb": float, "tb": float, "did": string}

=== DEPENDENCIES ===
- WiFiNINA library
- ArduinoHttpClient library
- ArduinoJson library
- ArduinoBLE library
- LiquidCrystal_I2C library
*/