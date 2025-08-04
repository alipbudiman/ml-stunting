# ML Stunting - Prediction Testing Guide

## 📋 **Flow Diagram Analysis**

Berdasarkan flow diagram yang Anda berikan:

```
IoT Device → Backend → WebSocket → Frontend
     ↓           ↓
  send bb&tb   broadcast bb&tb
     ↓           ↓
   Backend ←   Frontend (user input + IoT data)
     ↓           ↓
  /predict   fetch & wait for IoT data
     ↓           ↓
  Frontend ←   if data complete → enable predict button
```

## 🎯 **Testing Files**

### 1. **prediction_test.html** - Frontend Testing Interface
- **Lokasi**: `d:\NEW PROJECT\mlstunting\sourceml\prediction_test.html`
- **Fungsi**: Complete UI untuk testing prediction dengan real-time IoT data

### 2. **test_prediction_flow.py** - Automated Testing Script  
- **Lokasi**: `d:\NEW PROJECT\mlstunting\sourceml\test_prediction_flow.py`
- **Fungsi**: Script otomatis untuk test complete flow

## 🌐 **Frontend Implementation (prediction_test.html)**

### **Features:**
- ✅ **Connection Management**: Connect/disconnect ke IoT device via WebSocket
- ✅ **Form Validation**: Real-time validation input user
- ✅ **IoT Data Integration**: Auto-populate BB & TB dari IoT device
- ✅ **Smart Button**: Predict button hanya enable jika semua data lengkap
- ✅ **Result Display**: Tampilan hasil prediction yang comprehensive
- ✅ **Error Handling**: Proper error handling dan logging

### **Input Fields:**

#### **User Input (Manual):**
- ✅ **Nama**: Text input untuk nama anak
- ✅ **Tanggal Lahir**: Date picker (format YYYY-MM-DD)
- ✅ **Jenis Kelamin**: Dropdown (L/P)
- ✅ **BB Lahir**: Birth weight dalam kg
- ✅ **TB Lahir**: Birth height dalam cm

#### **IoT Data (Auto-populated):**
- ✅ **Berat Current**: Auto dari WebSocket (disabled input)
- ✅ **Tinggi Current**: Auto dari WebSocket (disabled input)

### **Button Logic:**
```javascript
// Button hanya enable jika:
const allUserDataFilled = nama && tanggalLahir && jenisKelamin && bbLahir && tbLahir;
const iotDataReceived = true; // Data dari IoT device sudah diterima

if (allUserDataFilled && iotDataReceived) {
    predictBtn.disabled = false;
} else {
    predictBtn.disabled = true;
}
```

## 🔄 **Flow Testing Process**

### **Manual Testing (Frontend):**

1. **Buka prediction_test.html** di browser
2. **Connect ke IoT**: 
   - Server URL: `localhost:5000`
   - Device ID: `IOT_001`
   - Click "Connect to IoT Device"
3. **Fill User Data**:
   - Nama: "Ahmad Budi"
   - Tanggal Lahir: "2021-05-15"
   - Jenis Kelamin: "Laki-laki"
   - BB Lahir: "3.2"
   - TB Lahir: "50"
4. **Wait for IoT Data**: 
   - BB & TB akan auto-populate dari WebSocket
   - Button predict akan enable otomatis
5. **Predict**: Click "🔮 Predict Stunting Status"
6. **View Result**: Hasil prediction akan muncul di bawah

### **Automated Testing (Python Script):**

```bash
cd "d:\NEW PROJECT\mlstunting\sourceml"
python test_prediction_flow.py
```

**Expected Output:**
```
🚀 Starting Complete ML Stunting Flow Test
============================================================

🧪 TEST CASE 1: Ahmad Budi
----------------------------------------
Step 1: Reset Device
🔄 Resetting device: IOT_001
Status Code: 200

Step 2: Send IoT Data  
📡 Sending IoT data: TB=95.5cm, BB=15.2kg
Status Code: 200

Step 3: Predict Stunting
🔮 Testing prediction for: Ahmad Budi
✅ Prediction successful!

📊 PREDICTION SUMMARY:
Child Name: Ahmad Budi
Prediction: Normal Growth
Confidence: 87.35%
Current Weight: 15.2 kg
Current Height: 95.5 cm
```

## 📡 **API Integration**

### **WebSocket Connection:**
```javascript
// Connect to device-specific WebSocket
ws://localhost:5000/ws/data/IOT_001

// Receive real-time data
{
  "did": "IOT_001",
  "tb": 95.5,
  "bb": 15.2,
  "status": "updated",
  "timestamp": 1691161234.567
}
```

### **Prediction API Call:**
```javascript
POST /predict
Content-Type: application/json

{
  "nama": "Ahmad Budi",
  "tanggal_lahir": "2021-05-15",
  "jenis_kelamin": "L",
  "bb_lahir": 3.2,
  "tb_lahir": 50.0,
  "berat": 15.2,    // From IoT
  "tinggi": 95.5    // From IoT
}
```

### **Expected Response:**
```json
{
  "data": {
    "class": "Normal Growth",
    "confidence": 0.8735,
    "zs_bbu": -0.25,
    "zs_tbu": 0.15,
    "zs_bbtb": -0.18
  },
  "message": "Prediction successful"
}
```

## 🎯 **Test Cases**

### **Test Case 1: Normal Growth**
```json
{
  "nama": "Ahmad Budi",
  "tanggal_lahir": "2021-05-15",
  "jenis_kelamin": "L",
  "bb_lahir": 3.2,
  "tb_lahir": 50.0,
  "iot_tb": 95.5,
  "iot_bb": 15.2
}
```

### **Test Case 2: Potential Stunting**
```json
{
  "nama": "Bayu Saputra", 
  "tanggal_lahir": "2022-03-22",
  "jenis_kelamin": "L",
  "bb_lahir": 2.8,
  "tb_lahir": 47.0,
  "iot_tb": 82.1,  // Lower height
  "iot_bb": 11.5   // Lower weight
}
```

### **Test Case 3: Female Child**
```json
{
  "nama": "Siti Aisyah",
  "tanggal_lahir": "2020-12-10", 
  "jenis_kelamin": "P",
  "bb_lahir": 3.0,
  "tb_lahir": 48.5,
  "iot_tb": 105.3,
  "iot_bb": 18.7
}
```

## 🚨 **Error Handling**

### **Common Errors:**

1. **Missing IoT Data:**
   ```
   Button Status: "⏳ Waiting for IoT Data..."
   Button Disabled: true
   ```

2. **Incomplete Form:**
   ```
   Button Status: "⚠️ Complete Personal Data Required"
   Button Disabled: true
   ```

3. **WebSocket Connection Failed:**
   ```
   Status: "Disconnected from IoT Device"
   Log: "❌ WebSocket error: Connection refused"
   ```

4. **API Error Response:**
   ```json
   {
     "detail": "Error calculating Z-scores"
   }
   ```

## 📊 **Result Display**

### **Normal Growth Result:**
```
✅ NORMAL GROWTH
Child Name: Ahmad Budi
Prediction Class: Normal Growth
Confidence Score: 87.35%
Current Weight: 15.2 kg
Current Height: 95.5 cm
```

### **Stunting Detected Result:**
```
⚠️ STUNTING DETECTED
Child Name: Bayu Saputra
Prediction Class: Stunting Risk
Confidence Score: 92.18%
Current Weight: 11.5 kg
Current Height: 82.1 cm
```

## 🔧 **Setup & Running**

### **1. Start Backend:**
```bash
cd "d:\NEW PROJECT\mlstunting\sourceml"
python main.py
```

### **2. Open Frontend:**
```bash
# Buka di browser
file:///d:/NEW%20PROJECT/mlstunting/sourceml/prediction_test.html
```

### **3. Simulate IoT Data (Optional):**
```bash
# Send test data via API
curl -X POST http://localhost:5000/recive \
  -H "Content-Type: application/json" \
  -d '{"did": "IOT_001", "tb": 95.5, "bb": 15.2}'
```

## ✅ **Success Criteria**

1. ✅ **WebSocket Connection**: Successfully connect to IoT device
2. ✅ **Real-time Data**: BB & TB auto-populate dari IoT
3. ✅ **Form Validation**: Button enable hanya jika data lengkap
4. ✅ **API Integration**: Successful call ke `/predict` endpoint
5. ✅ **Result Display**: Proper display hasil prediction
6. ✅ **Error Handling**: Graceful error handling untuk semua skenario

**System siap untuk production dengan complete prediction flow!** 🎉
