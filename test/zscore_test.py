
from lib.prediction import ZScoreCalculator, parser_usia_bulan
from pygrowup import Calculator
import pandas as pd
import pprint



# calculator = ZScoreCalculator()
calc = Calculator(adjust_height_data=False, include_cdc=False)

def calculate_zscore(age_months: int, weight_kg: float, height_cm: float, sex: str) -> dict:
    """
    Menghitung Z-scores menggunakan pygrowup library
    
    Args:
        age_months: Usia dalam bulan
        weight_kg: Berat badan dalam kg
        height_cm: Tinggi badan dalam cm  
        sex: Jenis kelamin ('M' untuk male, 'F' untuk female)
    
    Returns:
        dict: Z-scores untuk BB/U, TB/U, dan BB/TB
    """
    try:
        # Weight-for-age (BB/U)
        z_wfa = calc.wfa(measurement=weight_kg, age_in_months=age_months, sex=sex)
        
        # Length/Height-for-age (TB/U) 
        z_hfa = calc.lhfa(measurement=height_cm, age_in_months=age_months, sex=sex)
        
        # Weight-for-height (BB/TB)
        z_wfh = calc.wfh(measurement=weight_kg, age_in_months=age_months, sex=sex, height=height_cm)
        
        return {
            "bbu": z_wfa,
            "tbu": z_hfa, 
            "bbtb": z_wfh
        }
    except Exception as e:
        print(f"Error calculating z-scores: {e}")
        return {
            "bbu": None,
            "tbu": None,
            "bbtb": None
        }



mydata = [
    {
        "nama":"M. FAJRI",
        "jenis_kelamin":"M",  # pygrowup menggunakan 'M' untuk male
        "bb_lahir":3,
        "tb_lahir":50,
        "usia":parser_usia_bulan(1, 4),  # 1 tahun 4 bulan
        "berat":10,
        "tinggi":79
    },
    {
        "nama":"NIA KAMELIA R", 
        "jenis_kelamin":"F",  # pygrowup menggunakan 'F' untuk female
        "bb_lahir":3,
        "tb_lahir":50,
        "usia":parser_usia_bulan(1, 9),  # 1 tahun 9 bulan
        "berat":9.2,
        "tinggi":76
    }
]

pprint.pprint(mydata)

for data in mydata:
    print(f"\n=== Analisis Z-Score untuk {data['nama']} ===")
    print(f"Jenis Kelamin: {data['jenis_kelamin']}")
    print(f"Usia: {data['usia']} bulan")
    print(f"Berat: {data['berat']} kg, Tinggi: {data['tinggi']} cm")
    print(f"BB Lahir: {data['bb_lahir']} kg, TB Lahir: {data['tb_lahir']} cm")
    
    # Calculate Z-scores
    result = calculate_zscore(data['usia'], data['berat'], data['tinggi'], data['jenis_kelamin'])
    
    if result['bbu'] is not None:
        print(f"\nHasil Z-Scores:")
        print(f"  BB/U (Weight-for-Age): {result['bbu']}")
        print(f"  TB/U (Height-for-Age): {result['tbu']}")
        print(f"  BB/TB (Weight-for-Height): {result['bbtb']}")
        
        # Interpretasi hasil
        print(f"\nInterpretasi:")
        
        pprint.pprint(result)
        
        # Interpretasi BB/U
        if result['bbu'] < -3:
            status_bbu = "Sangat Kurang (Severely Underweight)"
        elif result['bbu'] < -2:
            status_bbu = "Kurang (Underweight)"
        elif result['bbu'] > 2:
            status_bbu = "Risiko Lebih (Risk of Overweight)"
        else:
            status_bbu = "Normal"
        print(f"  Status BB/U: {status_bbu}")
        
        # Interpretasi TB/U  
        if result['tbu'] < -3:
            status_tbu = "Sangat Pendek (Severely Stunted)"
        elif result['tbu'] < -2:
            status_tbu = "Pendek (Stunted)"
        else:
            status_tbu = "Normal"
        print(f"  Status TB/U: {status_tbu}")
        
        # Interpretasi BB/TB
        if result['bbtb'] < -3:
            status_bbtb = "Sangat Kurus (Severely Wasted)"
        elif result['bbtb'] < -2:
            status_bbtb = "Kurus (Wasted)"
        elif result['bbtb'] > 2:
            status_bbtb = "Gemuk (Obese)"
        else:
            status_bbtb = "Normal"
        print(f"  Status BB/TB: {status_bbtb}")
    else:
        print("❌ Gagal menghitung Z-scores")
    
    print("-" * 50)