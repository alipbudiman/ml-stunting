import pandas as pd
from lib.prediction import PredictionInput, Prediction, ZScoreCalculator
from lib.prediction import parser_usia_bulan, parser_usia_tahun, parser_gender, parser_usia_from_string

calculator = ZScoreCalculator()
prediksi = Prediction()

match_res = 0
not_match_res = 0

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
    zscore_result = calculator.calculate_zscore(parser_usia_bulan(2, 3), berat, tinggi, parser_gender(jenis_kelamin))
    
    if zscore_result['calculated']:        
        # Gunakan Z-score yang dihitung dan manual untuk BB/U
        data_anak = PredictionInput(
            jenis_kelamin=jenis_kelamin,
            bb_lahir=bb_lahir,
            tb_lahir=tb_lahir,
            usia=usia,
            berat=berat,
            tinggi=tinggi,
            zs_bbu=zscore_result['bbu'],  # Masih manual (belum ada implementasi BB/U)
            zs_tbu=zscore_result['tbu'],  # Hasil perhitungan otomatis
            zs_bbtb=zscore_result['bbtb']  # Hasil perhitungan otomatis
        )
        
        # Prediksi
        prediksi = Prediction()
        hasil_prediksi = prediksi.predict(data_anak)
        
        
        print(f"Hasil Prediksi:")
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
            
def test_with_data():
    print("=== Test with Data ===")
    df = pd.read_csv('stunting/data-stunting.csv')
    
    # Data cleaning - hapus missing values
    df_clean = df.dropna().copy()
    
    for index, row in df_clean.iterrows():
        usia = parser_usia_from_string(row['Usia'])
        if not usia:
            raise Exception(f"Invalid age format: {row['Usia']}")
        
        # Hitung Z-score otomatis
        usia_tahun = usia.tahun
        usia_bulan = usia.bulan
        usia_hari = usia.hari
        
        if usia_tahun < 1:
            continue
                
        zscore_result = calculator.calculate_zscore(parser_usia_bulan(usia_tahun, usia_bulan), row['Berat'], row['Tinggi'], parser_gender(row['Jenis Kelamin']))

        if zscore_result['calculated']:
            # Gunakan Z-score yang dihitung dan manual untuk BB/U
            data_anak = PredictionInput(
                jenis_kelamin=row['Jenis Kelamin'],
                bb_lahir=row['BB lahir'],
                tb_lahir=row['TB lahir'],
                usia=parser_usia_tahun(usia_tahun, usia_bulan, usia_hari),
                berat=row['Berat'],
                tinggi=row['Tinggi'],
                zs_bbu=zscore_result['bbu'],  # Masih manual (belum ada implementasi BB/U)
                zs_tbu=zscore_result['tbu'],  # Hasil perhitungan otomatis
                zs_bbtb=zscore_result['bbtb']  # Hasil perhitungan otomatis
            )

            hasil_prediksi = prediksi.predict(data_anak)
            
            if hasil_prediksi.tbu.lower() == row['BB/U'].lower() and \
               hasil_prediksi.bbu.lower() == row['TB/U'].lower() and \
               hasil_prediksi.bbtb.lower() == row['BB/TB'].lower():
                global match_res
                match_res += 1
            else:
                # print(f"Mismatch for {index + 1}:")
                # print(f"  Prediksi TB/U: {hasil_prediksi.tbu} (expected: {row['BB/U']})")
                # print(f"  Prediksi BB/U: {hasil_prediksi.bbu} (expected: {row['TB/U']})")
                # print(f"  Prediksi BB/TB: {hasil_prediksi.bbtb} (expected: {row['BB/TB']})")
                global not_match_res
                not_match_res += 1
                
        else:
            print(f"Error menghitung Z-score: {zscore_result.get('error', 'Unknown error')}")
    
    print("Match Results:", match_res)
    print("Not Match Results:", not_match_res)
    
    # buat presentase akurasinya
    total = match_res + not_match_res
    if total > 0:
        accuracy = (match_res / total) * 100
        print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    # predict_with_auto_zscore()
    # predict_with_manual_zscore()
    # test_individual_zscore()
    test_with_data()
