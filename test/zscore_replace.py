import re
import numpy as np
import pandas as pd
from pygrowup import Calculator
import logging

# Setup logging untuk debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_usia_to_months(usia_str):
    """Convert usia format 'X Tahun - Y Bulan - Z Hari' ke bulan (int)"""
    if pd.isna(usia_str):
        return np.nan
    
    try:
        # Extract tahun, bulan, hari
        tahun = re.search(r'(\d+) Tahun', str(usia_str))
        bulan = re.search(r'(\d+) Bulan', str(usia_str))
        hari = re.search(r'(\d+) Hari', str(usia_str))
        
        tahun_val = int(tahun.group(1)) if tahun else 0
        bulan_val = int(bulan.group(1)) if bulan else 0
        hari_val = int(hari.group(1)) if hari else 0
        
        # Konversi ke bulan total (hari diabaikan untuk simplifikasi)
        total_months = tahun_val * 12 + bulan_val
        
        return max(1, total_months)  # Minimum 1 bulan untuk pygrowup
    except Exception as e:
        logger.error(f"Error parsing usia '{usia_str}': {e}")
        return np.nan

def validate_input_data(age_months, weight_kg, height_cm, sex):
    """Validasi input data sebelum perhitungan Z-score"""
    errors = []
    
    # Validasi usia (1-60 bulan untuk anak 1-5 tahun)
    if pd.isna(age_months) or age_months < 1 or age_months > 60:
        errors.append(f"Usia tidak valid: {age_months} bulan")
    
    # Validasi berat badan
    if pd.isna(weight_kg) or weight_kg <= 0 or weight_kg > 50:
        errors.append(f"Berat badan tidak valid: {weight_kg} kg")
    
    # Validasi tinggi badan  
    if pd.isna(height_cm) or height_cm < 45 or height_cm > 130:
        errors.append(f"Tinggi badan tidak valid: {height_cm} cm")
    
    # Validasi jenis kelamin
    if sex not in ['L', 'P', 'M', 'F']:
        errors.append(f"Jenis kelamin tidak valid: {sex}")
    
    return errors

def calculate_zscore_robust(age_months: int, weight_kg: float, height_cm: float, sex: str, calc_instance=None) -> dict:
    """
    Menghitung Z-scores menggunakan pygrowup library dengan validasi robust
    
    Args:
        age_months: Usia dalam bulan (1-60)
        weight_kg: Berat badan dalam kg
        height_cm: Tinggi badan dalam cm  
        sex: Jenis kelamin ('L'/'P' atau 'M'/'F')
        calc_instance: Instance Calculator (optional)
    
    Returns:
        dict: Z-scores untuk BB/U, TB/U, dan BB/TB dengan status validasi
    """
    
    # Inisialisasi result dengan default values
    result = {
        "bbu": None,
        "tbu": None, 
        "bbtb": None,
        "status": "error",
        "errors": []
    }
    
    try:
        # Validasi input
        validation_errors = validate_input_data(age_months, weight_kg, height_cm, sex)
        if validation_errors:
            result["errors"] = validation_errors
            result["status"] = "validation_failed"
            return result
        
        # Konversi jenis kelamin ke format pygrowup
        sex_pygrowup = 'M' if sex.upper() in ['L', 'M'] else 'F'
        
        # Gunakan calculator instance yang diberikan atau buat baru
        if calc_instance is None:
            calc_instance = Calculator(adjust_height_data=False, include_cdc=False)
        
        # Perhitungan Z-scores dengan error handling individual
        try:
            z_wfa = calc_instance.wfa(measurement=weight_kg, age_in_months=age_months, sex=sex_pygrowup)
            result["bbu"] = round(float(z_wfa), 2)
        except Exception as e:
            result["errors"].append(f"Error BB/U: {str(e)}")
            
        try:
            z_hfa = calc_instance.lhfa(measurement=height_cm, age_in_months=age_months, sex=sex_pygrowup)
            result["tbu"] = round(float(z_hfa), 2)
        except Exception as e:
            result["errors"].append(f"Error TB/U: {str(e)}")
            
        try:
            z_wfh = calc_instance.wfh(measurement=weight_kg, age_in_months=age_months, sex=sex_pygrowup, height=height_cm)
            result["bbtb"] = round(float(z_wfh), 2)
        except Exception as e:
            result["errors"].append(f"Error BB/TB: {str(e)}")
        
        # Tentukan status akhir
        if all(v is not None for v in [result["bbu"], result["tbu"], result["bbtb"]]):
            result["status"] = "success"
        elif any(v is not None for v in [result["bbu"], result["tbu"], result["bbtb"]]):
            result["status"] = "partial_success"
        else:
            result["status"] = "failed"
            
        return result
        
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        result["status"] = "fatal_error"
        logger.error(f"Fatal error in calculate_zscore_robust: {e}")
        return result

# Load data dan processing
if __name__ == "__main__":
    df = pd.read_csv('stunting/data-stunting.csv')
    
    # Data cleaning - hapus missing values
    df_clean = df.dropna().copy()
    
    print(f"Data setelah menghapus missing values: {len(df_clean)} records")
    
    # Inisialisasi calculator
    calc = Calculator(adjust_height_data=False, include_cdc=False)
    
    print("\nMemulai perhitungan Z-scores dengan method yang diperbaiki...")
    
    success_count = 0
    error_count = 0
    
    for index, row in df_clean.iterrows():
        if index % 10 == 0:  # Progress indicator
            print(f"Processing row {index}/{len(df_clean)}")
        
        # Gunakan function yang sudah diperbaiki
        result = calculate_zscore_robust(
            age_months=parse_usia_to_months(row['Usia']),
            weight_kg=float(row['Berat']),
            height_cm=float(row['Tinggi']),
            sex=str(row['Jenis Kelamin']),
            calc_instance=calc
        )
        
        if result["status"] == "success":
            df_clean.at[index, 'ZS BB/U'] = result['bbu']
            df_clean.at[index, 'ZS TB/U'] = result['tbu']
            df_clean.at[index, 'ZS BB/TB'] = result['bbtb']
            success_count += 1
        else:
            logger.warning(f"Row {index} failed: {result['errors']}")
            error_count += 1
    
    # Simpan ke csv baru
    df_clean.to_csv('stunting/data-stunting-zscore.csv', index=False)
    
    print(f"\n=== HASIL PROCESSING ===")
    print(f"Data berhasil disimpan ke 'data-stunting-zscore.csv'")
    print(f"Total records: {len(df_clean)}")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {success_count/len(df_clean)*100:.1f}%")
