# ML Stunting - Setup dan Testing Guide

## 🚀 Setup Backend

### 1. Install Dependencies
```bash
cd "d:\NEW PROJECT\mlstunting\sourceml"
pip install -r requirements.txt
```

### 2. Jalankan Server
```bash
python main.py
```

Server akan berjalan di: `http://localhost:5000`

### 3. Test API Endpoints

#### Health Check
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

#### Reset Device
```bash
curl -X POST http://localhost:5000/reset/IOT_001
```

#### Send Data (Simulasi IoT)
```bash
curl -X POST http://localhost:5000/recive \
  -H "Content-Type: application/json" \
  -d '{"did": "IOT_001", "tb": 120.5, "bb": 25.3}'
```

#### Get Device Data
```bash
curl http://localhost:5000/devices/IOT_001
curl http://localhost:5000/devices
```

#### WebSocket Status
```bash
curl http://localhost:5000/ws/status
```

## 🌐 Frontend Testing

### 1. Buka File HTML
- Buka `websocket_test.html` di browser
- Atau double-click file tersebut

### 2. Testing Steps

1. **Pastikan Server URL benar**: `localhost:5000`
2. **Masukkan Device ID**: `IOT_001`
3. **Reset Device**: Click "Reset Device Data"
4. **Connect WebSocket**: Click "Connect"
5. **Send Test Data**: Input height/weight dan click "Send Test Data"
6. **Monitor Real-time**: Data akan muncul di display

### 3. Troubleshooting

#### Error: "Failed to fetch"
- ✅ Pastikan server berjalan di `http://localhost:5000`
- ✅ CORS sudah diaktifkan di backend
- ✅ Tidak ada firewall yang blocking

#### Error: WebSocket connection failed
- ✅ Pastikan WebSocket endpoint benar: `ws://localhost:5000/ws/data/{device_id}`
- ✅ Device ID sudah benar
- ✅ Server sudah running

## 🔧 IoT Device Setup

### 1. Update IOT.cpp
```cpp
// Konfigurasi yang perlu disesuaikan:
const String DEVICE_ID = "IOT_001";        // ← Unique per device
const char* ssid = "YOUR_WIFI_SSID";       // ← Your WiFi
const char* password = "YOUR_WIFI_PASSWORD"; // ← Your WiFi password
const char* serverAddress = "192.168.1.100"; // ← Your server IP
```

### 2. Arduino Libraries
Install libraries berikut via Arduino IDE:
- `WiFiNINA`
- `ArduinoHttpClient` 
- `ArduinoJson`
- `ArduinoBLE`
- `LiquidCrystal_I2C`

### 3. Hardware Setup
- Arduino Nano 33 IoT (atau compatible)
- I2C LCD Display
- HC-SR04 Ultrasonic Sensor  
- BLE Weight Scale
- LED Matrix (Arduino UNO R4)

## 📊 Testing Script

### 1. Jalankan Python Test
```bash
python test_device_reset.py
```

### 2. Expected Output
```
🚀 Starting Device Reset & Data Flow Tests
==================================================

1. Test Reset Device
🔄 Testing reset for device: IOT_001
Status Code: 200
Response: {'status': 200, 'message': 'Data reset successfully'}

2. Test Send Data
📡 Testing send data for device: IOT_001
Status Code: 200
Response: {'status': 200, 'message': 'Data received successfully for device IOT_001'}

✅ All tests passed! Device reset and data flow working correctly.
```

## 🎯 Flow Testing

### Complete Flow Test:
1. **Start Backend**: `python main.py`
2. **Reset Device**: `POST /reset/IOT_001`
3. **Connect WebSocket**: `ws://localhost:5000/ws/data/IOT_001`
4. **Send Data**: `POST /recive` dengan data IoT
5. **Verify Real-time**: Data muncul di WebSocket client
6. **Check Status**: `GET /ws/status`

## 🚨 Common Issues

### CORS Error
- ✅ Pastikan `CORSMiddleware` sudah ditambahkan di `main.py`
- ✅ Restart server setelah menambahkan CORS

### WebSocket Connection Refused
- ✅ Pastikan server running di port 5000
- ✅ Check firewall settings
- ✅ Device ID format benar

### Data Not Updating
- ✅ Check WebSocket connection status
- ✅ Verify device ID matching
- ✅ Check server logs for errors

## 📱 Multi-Device Testing

### Test Multiple Devices:
1. Reset `IOT_001`: `POST /reset/IOT_001`
2. Reset `IOT_002`: `POST /reset/IOT_002`
3. Connect to `IOT_001`: `ws://localhost:5000/ws/data/IOT_001`
4. Connect to `IOT_002`: `ws://localhost:5000/ws/data/IOT_002`
5. Send data untuk masing-masing device
6. Verify data isolation (each client only gets their device data)

✅ **Sistem siap untuk production dengan multi-device support!**
