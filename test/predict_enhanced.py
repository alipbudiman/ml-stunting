from lib.prediction import PredictionInput, Prediction
from lib.prediction.zscore import ZScoreCalculator, calculate_zscore_from_data

def parser_usia_bulan(tahun: int, bulan: int) -> int:
    """Menghitung usia dalam bulan"""
    return tahun * 12 + bulan

def parser_usia_tahun(tahun: int, bulan: int, hari: int) -> float:
    """Menghitung usia dalam tahun"""
    return tahun + (bulan / 12) + (hari / 365)

# Contoh penggunaan dengan menghitung Z-score otomatis
def predict_with_auto_zscore():
    print("=== Prediksi dengan Auto Z-Score Calculation ===")
    
    # Data anak
    jenis_kelamin = 'P'
    bb_lahir = 2.9
    tb_lahir = 48
    usia = parser_usia_tahun(2, 3, 15)
    berat = 13.8
    tinggi = 89
    
    print(f"Data anak:")
    print(f"- Jenis kelamin: {jenis_kelamin}")
    print(f"- Usia: {usia:.2f} tahun ({int(usia*12)} bulan)")
    print(f"- Berat: {berat} kg")
    print(f"- Tinggi: {tinggi} cm")
    
    # Hitung Z-score otomatis
    zscore_result = calculate_zscore_from_data(jenis_kelamin, tinggi, berat, usia)
    
    if zscore_result['calculated']:
        print(f"\\nZ-scores yang dihitung:")
        print(f"- ZS BB/TB: {zscore_result['zs_bbtb']}")
        print(f"- ZS TB/U: {zscore_result['zs_tbu']}")
        
        # Gunakan Z-score yang dihitung dan manual untuk BB/U
        data_anak = PredictionInput(
            jenis_kelamin=jenis_kelamin,
            bb_lahir=bb_lahir,
            tb_lahir=tb_lahir,
            usia=usia,
            berat=berat,
            tinggi=tinggi,
            zs_bbu=-0.15,  # Masih manual (belum ada implementasi BB/U)
            zs_tbu=zscore_result['zs_tbu'],  # Hasil perhitungan otomatis
            zs_bbtb=zscore_result['zs_bbtb']  # Hasil perhitungan otomatis
        )
        
        # Prediksi
        prediksi = Prediction()
        hasil_prediksi = prediksi.predict(data_anak)
        
        print(f"\\nHasil Prediksi:")
        print(f"- Prediksi TB/U: {hasil_prediksi.tbu}")
        print(f"- Prediksi BB/U: {hasil_prediksi.bbu}")
        print(f"- Prediksi BB/TB: {hasil_prediksi.bbtb}")
    else:
        print(f"Error menghitung Z-score: {zscore_result.get('error', 'Unknown error')}")

# Contoh penggunaan manual (seperti sebelumnya)
def predict_with_manual_zscore():
    print("\\n=== Prediksi dengan Manual Z-Score ===")
    
    usia = parser_usia_tahun(2, 3, 15)
    print(f"Usia: {usia:.2f} tahun")

    data_anak = PredictionInput(
        jenis_kelamin='P',
        bb_lahir=2.9,
        tb_lahir=48,
        usia=usia,
        berat=13.8,
        tinggi=89,
        zs_bbu=-0.15,
        zs_tbu=-1.77,
        zs_bbtb=1.18
    )

    prediksi = Prediction()
    hasil_prediksi = prediksi.predict(data_anak)
    print(f"Prediksi TB/U: {hasil_prediksi.tbu}")
    print(f"Prediksi BB/U: {hasil_prediksi.bbu}")
    print(f"Prediksi BB/TB: {hasil_prediksi.bbtb}")

# Contoh perhitungan Z-score individual
def test_individual_zscore():
    print("\\n=== Test Individual Z-Score Calculations ===")
    
    calculator = ZScoreCalculator()
    
    # Test BB/TB
    print("1. Z-Score BB/TB:")
    zs_bbtb = calculator.calculate_bbtb_zscore('male', 89, 13.4)
    print(f"   Anak laki-laki (tinggi=89cm, berat=13.4kg): {zs_bbtb}")
    
    # Test TB/U
    print("2. Z-Score TB/U:")
    zs_tbu = calculator.calculate_tbu_zscore('female', 27, 88)  # 27 bulan, 88cm
    print(f"   Anak perempuan (27 bulan, tinggi=88cm): {zs_tbu}")
    
    # Test berbagai usia
    print("3. Z-Score TB/U untuk berbagai usia:")
    for usia_bulan in [12, 18, 24, 30, 36]:
        try:
            zs = calculator.calculate_tbu_zscore('male', usia_bulan, 80)
            print(f"   {usia_bulan} bulan (tinggi=80cm): {zs}")
        except Exception as e:
            print(f"   {usia_bulan} bulan: Error - {e}")

if __name__ == "__main__":
    predict_with_auto_zscore()
    predict_with_manual_zscore()
    test_individual_zscore()
