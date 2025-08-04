from .models import ParsingUsiaOutput

def parser_usia_bulan(tahun: int, bulan: int) -> int:
    """Menghitung usia dalam bulan"""
    return tahun * 12 + bulan

def parser_usia_tahun(tahun: int, bulan: int, hari: int) -> float:
    """Menghitung usia dalam tahun"""
    return tahun + (bulan / 12) + (hari / 365)

def parser_gender(gender: str) -> str:
    """Parser untuk jenis kelamin"""
    if gender == 'L':
        return 'M'
    elif gender == 'P':
        return 'F'
    else:
        raise ValueError("Jenis kelamin tidak valid")

def parser_usia_from_string(usia_str: str) -> ParsingUsiaOutput:
    """Parser usia dari string format 'X tahun Y bulan' menjadi bulan"""
    import re
    
    try:
        # Regex untuk menangkap tahun, bulan, dan hari
        tahun = re.search(r'(\d+)\s*tahun', usia_str.lower())
        bulan = re.search(r'(\d+)\s*bulan', usia_str.lower())
        hari = re.search(r'(\d+)\s*hari', usia_str.lower())
        tahun_val = int(tahun.group(1)) if tahun else 0
        bulan_val = int(bulan.group(1)) if bulan else 0
        hari_val = int(hari.group(1)) if hari else 0

        return ParsingUsiaOutput(
            tahun=tahun_val,
            bulan=bulan_val,
            hari=hari_val
        )      
    except Exception as e:
        print(f"Error parsing usia '{usia_str}': {e}")
        raise ValueError("Format usia tidak valid")

# parse tanggal lahir (timestamp) return tahun, bulan, hari anak itu sekarang
def parse_tanggal_lahir(tanggal_lahir: str) -> ParsingUsiaOutput:
    """Parser tanggal lahir dari string format 'YYYY-MM-DD' menjadi tahun, bulan, hari"""
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(tanggal_lahir, '%Y-%m-%d')
        today = datetime.now()
        delta = today - date_obj
        
        tahun = delta.days // 365
        bulan = (delta.days % 365) // 30
        hari = (delta.days % 365) % 30
        
        return ParsingUsiaOutput(
            tahun=tahun,
            bulan=bulan,
            hari=hari
        )
    except ValueError as e:
        print(f"Error parsing tanggal lahir '{tanggal_lahir}': {e}")
        raise ValueError("Format tanggal lahir tidak valid")