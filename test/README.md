# 🏥 Sistem Prediksi Status Gizi Anak dengan XGBoost

Sistem machine learning untuk memprediksi status gizi anak berdasarkan data antropometri menggunakan algoritma XGBoost.

## 🎯 Fitur Utama

- **Prediksi TB/U** (Tinggi Badan menurut Umur) - Deteksi stunting
- **Prediksi BB/U** (Berat Badan menurut Umur) - Deteksi underweight
- **Prediksi BB/TB** (Berat Badan menurut Tinggi Badan) - Deteksi wasting/obesitas
- Interface yang user-friendly dengan menu interaktif
- Validasi input otomatis
- Interpretasi hasil yang mudah dipahami

## 📊 Akurasi Model

| Model | Akurasi |
|-------|---------|
| TB/U Model | 99.60% |
| BB/U Model | 99.60% |
| BB/TB Model | 100.00% |

## 📋 Requirements

### File yang Diperlukan
- `model_tbu.pkl` - Model untuk prediksi TB/U
- `model_bbu.pkl` - Model untuk prediksi BB/U  
- `model_bbtb.pkl` - Model untuk prediksi BB/TB
- `encoders.pkl` - Encoder untuk transformasi data

### Python Packages
```bash
pip install joblib numpy pandas xgboost scikit-learn
```

## 🚀 Cara Penggunaan

### 1. Menjalankan Program Interaktif
```bash
python main.py
```

Program akan menampilkan menu:
1. **Demo dengan Contoh Data** - Melihat prediksi dengan data contoh
2. **Input Data Manual** - Input data anak secara manual
3. **Contoh Penggunaan Cepat** - Prediksi sederhana
4. **Keluar** - Mengakhiri program

### 2. Menggunakan dalam Kode Python

```python
from main import PrediksiStatusGizi

# Inisialisasi sistem
sistem = PrediksiStatusGizi()

# Prediksi sederhana
hasil = sistem.prediksi(
    jenis_kelamin='L',    # 'L' = Laki-laki, 'P' = Perempuan
    bb_lahir=3.2,        # Berat badan lahir (kg)
    tb_lahir=50,         # Tinggi badan lahir (cm)
    usia=2,              # Usia (tahun, 1-5)
    berat=12.5,          # Berat badan sekarang (kg)
    tinggi=87,           # Tinggi badan sekarang (cm)
    zs_bbu=-0.5,         # Z-score BB/U
    zs_tbu=-0.8,         # Z-score TB/U
    zs_bbtb=0.2          # Z-score BB/TB
)

print(hasil)
# Output: {'TB/U': 'Normal', 'BB/U': 'Normal', 'BB/TB': 'Gizi Baik'}
```

### 3. Prediksi dengan Detail
```python
# Prediksi dengan output detail
hasil = sistem.prediksi_detail(
    nama_anak="Ahmad",
    jenis_kelamin='L',
    bb_lahir=3.2,
    tb_lahir=50,
    usia=2,
    berat=12.5,
    tinggi=87,
    zs_bbu=-0.5,
    zs_tbu=-0.8,
    zs_bbtb=0.2
)
```

## 📊 Parameter Input

| Parameter | Deskripsi | Contoh |
|-----------|-----------|--------|
| `jenis_kelamin` | Jenis kelamin anak | 'L' atau 'P' |
| `bb_lahir` | Berat badan lahir (kg) | 3.2 |
| `tb_lahir` | Tinggi badan lahir (cm) | 50 |
| `usia` | Usia anak (tahun) | 2 (1-5 tahun) |
| `berat` | Berat badan saat ini (kg) | 12.5 |
| `tinggi` | Tinggi badan saat ini (cm) | 87 |
| `zs_bbu` | Z-score Berat/Umur | -0.5 |
| `zs_tbu` | Z-score Tinggi/Umur | -0.8 |
| `zs_bbtb` | Z-score Berat/Tinggi | 0.2 |

## 🎯 Output Prediksi

### TB/U (Tinggi Badan menurut Umur)
- **Normal**: Tinggi badan sesuai usia ✅
- **Pendek**: Stunting ringan ⚠️
- **Sangat Pendek**: Stunting berat 🚨

### BB/U (Berat Badan menurut Umur)  
- **Normal**: Berat badan sesuai usia ✅
- **Kurang**: Underweight ⚠️
- **Sangat Kurang**: Severely underweight 🚨
- **Risiko Lebih**: Berisiko overweight ⚠️

### BB/TB (Berat Badan menurut Tinggi Badan)
- **Gizi Baik**: Status gizi baik ✅
- **Gizi Kurang**: Wasting ⚠️
- **Gizi Lebih**: Overweight ⚠️
- **Obesitas**: Obesitas 🚨
- **Risiko Gizi Lebih**: Berisiko overweight ⚠️

## 📁 Struktur File

```
📦 mlstunting/
├── 📄 main.py                 # Program utama
├── 📄 stunting.ipynb         # Notebook training model
├── 📄 data-stunting.csv      # Dataset
├── 📦 model_tbu.pkl          # Model TB/U
├── 📦 model_bbu.pkl          # Model BB/U
├── 📦 model_bbtb.pkl         # Model BB/TB
├── 📦 encoders.pkl           # Encoders
└── 📄 README.md              # Dokumentasi
```

## 💡 Contoh Demo

```bash
🏥 SISTEM PREDIKSI STATUS GIZI ANAK
📊 Menggunakan Model XGBoost

📝 CONTOH 1: Anak dengan Status Gizi Normal
============================================================
👶 Nama Anak: Ahmad
📊 Data Input:
   • Jenis Kelamin: Laki-laki
   • BB Lahir: 3.2 kg
   • Usia: 2 tahun
   • Berat Sekarang: 12.5 kg
   • Tinggi Sekarang: 87 cm

🎯 Hasil Prediksi:
   • TB/U (Tinggi/Umur): Normal ✅
   • BB/U (Berat/Umur): Normal ✅
   • BB/TB (Berat/Tinggi): Gizi Baik ✅
```

## 🔧 Troubleshooting

### Error: File model tidak ditemukan
```bash
❌ Error: File model tidak ditemukan
```
**Solusi**: Pastikan file `.pkl` ada di folder yang sama dengan `main.py`

### Error: Jenis kelamin harus 'L' atau 'P'
**Solusi**: Gunakan 'L' untuk laki-laki atau 'P' untuk perempuan

### Error: Usia harus antara 1-5 tahun
**Solusi**: Model hanya dilatih untuk anak usia 1-5 tahun

## 📈 Model Development

Model ini dilatih menggunakan:
- **Algorithm**: XGBoost (Extreme Gradient Boosting)
- **Dataset**: 1.240 anak (usia 1-5 tahun)
- **Features**: 9 fitur antropometri
- **Hyperparameters**: Optimal tuning untuk akurasi maksimal
- **Validation**: 80% training, 20% testing

## 👨‍💻 Author

Developed by AI Assistant (2025)

## 📄 License

This project is for educational and research purposes.

---

**⚠️ Disclaimer**: Sistem ini adalah alat bantu prediksi. Untuk diagnosis medis yang akurat, konsultasikan dengan tenaga kesehatan profesional.
