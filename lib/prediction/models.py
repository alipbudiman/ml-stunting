from pydantic import BaseModel
from typing import Optional

class DataAnakInput(BaseModel):
    """
    Input model for child data. Parameters:
    ```
    nama : str
        Nama anak
    jenis_kelamin : str
        Jenis kelamin ('L' untuk laki-laki, 'P' untuk perempuan)
    bb_lahir : float
        Berat badan lahir dalam kg (contoh: 3.2)
    tb_lahir : float
        Tinggi badan lahir dalam cm (contoh: 50)
    tanggal_lahir : str
        Format `YYYY-MM-DD`
    berat : float
        Berat badan saat ini dalam kg (contoh: 12.5)
    tinggi : float
        Tinggi badan saat ini dalam cm (contoh: 87)
    ```
    """
    nama: str
    jenis_kelamin: str
    bb_lahir: float
    tb_lahir: float
    tanggal_lahir: str
    berat: float
    tinggi: float

class PredictionInput(BaseModel):
    """
    Input model for stunting prediction. Parameters:
    ```    
    jenis_kelamin : str
        Jenis kelamin ('L' untuk laki-laki, 'P' untuk perempuan)
    bb_lahir : float
        Berat badan lahir dalam kg (contoh: 3.2)
    tb_lahir : float
        Tinggi badan lahir dalam cm (contoh: 50)
    usia: float
        Usia anak dalam tahun (contoh: 2.5)
    berat: float
        Berat badan saat ini dalam kg (contoh: 12.5)
    tinggi: float
        Tinggi badan saat ini dalam cm (contoh: 87)
    zs_bbu: Optional[float]
        Z-score Berat Badan menurut Umur (contoh: -1.5)
    zs_tbu: Optional[float]
        Z-score Tinggi Badan menurut Umur (contoh: -2.0)
    zs_bbtb: Optional[float]
        Z-score Berat Badan menurut Tinggi Badan (contoh: -1.0)
    ```
    """
    usia: float
    jenis_kelamin: str
    bb_lahir: float
    tb_lahir: float
    tanggal_lahir: str
    berat: float
    tinggi: float
    zs_bbu: Optional[float]
    zs_tbu: Optional[float]
    zs_bbtb: Optional[float]

class PredictionOutput(BaseModel):
    """
    Output model for stunting prediction results
    """
    tbu: str  # Status Tinggi Badan menurut Umur
    bbu: str  # Status Berat Badan menurut Umur  
    bbtb: str # Status Berat Badan menurut Tinggi Badan

class ParsingUsiaOutput(BaseModel):
    """
    Output model for parsing usia
    tahan: int
    bulan: int
    hari: int
    """
    tahun: int
    bulan: int
    hari: int

class ZscoreResults(BaseModel):
    """
    Output model for Z-score calculation results
    calculated: bool
        Status apakah Z-score berhasil dihitung
    bbu: Optional[float]
        Z-score Berat Badan menurut Umur
    tbu: Optional[float]
        Z-score Tinggi Badan menurut Umur
    bbtb: Optional[float]
        Z-score Berat Badan menurut Tinggi Badan
    """
    calculated: bool
    bbu: Optional[float]
    tbu: Optional[float]
    bbtb: Optional[float]

class PredictionOutputWithMessage(BaseModel):
    """
    Output model for prediction results with message
    """
    data: PredictionOutput
    message: str