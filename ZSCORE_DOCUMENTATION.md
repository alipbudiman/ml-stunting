# Z-Score Calculator untuk Prediksi Stunting

Dokumentasi implementasi z-score calculator yang mendukung BB/TB (Berat Badan per Tinggi Badan) dan TB/U (Tinggi Badan per Umur).

## 📊 **Data yang Didukung**

### 1. BB/TB (Berat Badan per Tinggi Badan)
- **File**: `rule2_l.csv` (laki-laki), `rule2_p.csv` (perempuan)
- **Format**: Kolom `PB` untuk tinggi badan, kolom SD untuk berat badan
- **Rentang**: Tinggi 45-110 cm

### 2. TB/U (Tinggi Badan per Umur)
- **File**: `rule_l.csv` (laki-laki), `rule_p.csv` (perempuan)
- **Format**: Kolom `USIA` untuk usia (bulan), kolom SD untuk tinggi badan
- **Rentang**: Usia 0-60 bulan

## 🔧 **Perbaikan yang Dilakukan**

### Error yang Diperbaiki:
1. **IndexError "out-of-bounds"**: Validasi input dan penanganan edge cases
2. **TypeError kolom USIA**: Parsing string ke numeric untuk data "24 *"
3. **Nama kolom tidak konsisten**: Penyesuaian dengan format CSV
4. **Missing return statement**: Penambahan fallback return

### Fitur Baru:
1. **Fungsi khusus TB/U**: `get_z_scores_tbu()` 
2. **Interpolasi robust**: Validasi boundary conditions
3. **Ekstrapolasi**: Untuk nilai di luar rentang tabel
4. **Utility functions**: Perhitungan otomatis multiple z-scores

## 🚀 **Cara Penggunaan**

### 1. Import Module
```python
from zscore import ZScoreCalculator, calculate_zscore_from_data
```

### 2. Penggunaan Individual

#### BB/TB (Berat Badan per Tinggi Badan)
```python
calculator = ZScoreCalculator()
zs_bbtb = calculator.calculate_bbtb_zscore('male', 89, 13.4)
print(f"Z-score BB/TB: {zs_bbtb}")  # Output: 1.0
```

#### TB/U (Tinggi Badan per Umur)
```python
calculator = ZScoreCalculator()
zs_tbu = calculator.calculate_tbu_zscore('female', 27, 88)  # 27 bulan, 88cm
print(f"Z-score TB/U: {zs_tbu}")  # Output: -0.09
```

### 3. Penggunaan Otomatis (Multiple Z-scores)
```python
result = calculate_zscore_from_data('P', 89, 13.8, 2.25)
if result['calculated']:
    print(f"BB/TB: {result['zs_bbtb']}")  # Output: 1.15
    print(f"TB/U: {result['zs_tbu']}")   # Output: 0.21
```

### 4. Integrasi dengan Prediksi
```python
from lib.prediction import PredictionInput, Prediction

# Hitung z-scores otomatis
zscore_result = calculate_zscore_from_data('P', 89, 13.8, 2.25)

data_anak = PredictionInput(
    jenis_kelamin='P',
    bb_lahir=2.9,
    tb_lahir=48,
    usia=2.25,
    berat=13.8,
    tinggi=89,
    zs_bbu=-0.15,  # Manual (belum ada implementasi BB/U)
    zs_tbu=zscore_result['zs_tbu'],   # Otomatis
    zs_bbtb=zscore_result['zs_bbtb']  # Otomatis
)

prediksi = Prediction()
hasil = prediksi.predict(data_anak)
```

## 📈 **Metode Perhitungan**

### 1. Interpolasi Linear
- **Tinggi/Usia tidak tepat**: Interpolasi antar 2 nilai terdekat
- **Berat/Tinggi antara SD**: Interpolasi linear untuk z-score

### 2. Ekstrapolasi
- **Di bawah -3 SD**: Ekstrapolasi linear menggunakan slope -3SD ke -2SD
- **Di atas +3 SD**: Ekstrapolasi linear menggunakan slope +2SD ke +3SD

### 3. Validasi Input
- **Rentang usia**: 0-60 bulan untuk TB/U
- **Rentang tinggi**: 45-110 cm untuk BB/TB
- **Error handling**: ValueError dengan pesan informatif

## 🧪 **Test Results**

```
=== Test Z-Score BB/TB Calculation ===
Test 1 - Z-score BB/TB (tinggi=89cm, berat=13.4kg): 1.0
Test 2 - Z-score BB/TB (tinggi=89.2cm, berat=13.4kg): 0.97
Test 3 - Z-score BB/TB (tinggi=89cm, berat=10kg): -2.38

=== Test Z-Score TB/U Calculation ===
Test 5 - Z-score TB/U (12 bulan, tinggi=75cm): -0.3
Test 6 - Z-score TB/U perempuan (24 bulan, tinggi=85cm): -0.44
Test 7 - Z-score TB/U (27 bulan, tinggi=88cm): -0.5
```

## ⚠️ **Catatan Penting**

1. **BB/U belum diimplementasi**: Sementara masih menggunakan nilai manual
2. **Data terbatas**: Rentang usia maksimal 60 bulan (5 tahun)
3. **Format input**: Gender bisa 'L'/'P' atau 'male'/'female'
4. **Usia dalam bulan**: Konversi otomatis dari tahun ke bulan

## 🔮 **Pengembangan Selanjutnya**

1. **Implementasi BB/U**: Perlu data tabel berat badan per umur
2. **Rentang usia lebih luas**: Data untuk anak > 5 tahun
3. **Validasi WHO**: Cross-check dengan standar WHO terbaru
4. **Performance optimization**: Caching untuk lookup yang sering digunakan

---

**Status**: ✅ BB/TB dan TB/U telah berfungsi dengan baik  
**Akurasi**: Sesuai dengan metode interpolasi WHO  
**Testing**: Passed semua test cases  
