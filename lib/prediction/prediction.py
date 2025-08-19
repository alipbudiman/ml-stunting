import sys
import joblib
import numpy as np
import pandas as pd
import warnings
import os
from pathlib import Path
warnings.filterwarnings('ignore')

from .models import PredictionInput, PredictionOutput

class Prediction:
    def __init__(self):
        """Inisialisasi class dan load model"""
        self.models = {}
        self.encoders = {}
        self.__load_models()
    
    def __load_models(self):
        """Load semua model dan encoder dari file .pkl"""
        try:
            print("🔄 Loading model dan encoder...")

            # Auto-detect model path
            # Get current file directory
            current_dir = Path(__file__).parent
            # Navigate to project root and find models directory
            project_root = current_dir.parent.parent  # Go up 2 levels from lib/prediction/
            modelpath = project_root / "models"
            
            # Convert to string for compatibility
            modelpath_str = str(modelpath) + os.sep
            
            print(f"📁 Model path: {modelpath_str}")
            
            # Check if models directory exists
            if not modelpath.exists():
                raise FileNotFoundError(f"Models directory not found: {modelpath}")
            
            # Load model XGBoost
            self.models['tbu'] = joblib.load(modelpath_str + "model_tbu.pkl")
            self.models['bbu'] = joblib.load(modelpath_str + "model_bbu.pkl")
            self.models['bbtb'] = joblib.load(modelpath_str + "model_bbtb.pkl")

            # Load encoders
            self.encoders = joblib.load(modelpath_str + "encoders.pkl")

            print("✅ Model dan encoder berhasil dimuat!")
            print(f"   - Model TB/U: {type(self.models['tbu']).__name__}")
            print(f"   - Model BB/U: {type(self.models['bbu']).__name__}")
            print(f"   - Model BB/TB: {type(self.models['bbtb']).__name__}")
            
        except FileNotFoundError as e:
            print(f"❌ Error: File model tidak ditemukan - {e}")
            print("   Pastikan file .pkl ada di direktori models/")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)
    
    def predict(self, data: PredictionInput):
        """
        Melakukan prediksi status gizi anak berdasarkan input
        """
        try:
            if data.jenis_kelamin not in ['L', 'P']:
                raise ValueError("Jenis kelamin harus 'L' atau 'P'")
            
            if not (1 <= data.usia <= 5):
                raise ValueError("Usia harus antara 1-5 tahun")

            gender_encoded = self.encoders['gender'].transform([data.jenis_kelamin])[0]

            input_data = np.array([[
                gender_encoded, data.bb_lahir, data.tb_lahir, data.usia,
                data.berat, data.tinggi, data.zs_bbu, data.zs_tbu, data.zs_bbtb
            ]])
            
            pred_tbu = self.models['tbu'].predict(input_data)[0]
            pred_bbu = self.models['bbu'].predict(input_data)[0]
            pred_bbtb = self.models['bbtb'].predict(input_data)[0]
            
            hasil_tbu = self.encoders['tbu'].inverse_transform([pred_tbu])[0]
            hasil_bbu = self.encoders['bbu'].inverse_transform([pred_bbu])[0]  
            hasil_bbtb = self.encoders['bbtb'].inverse_transform([pred_bbtb])[0]
            
            return PredictionOutput(
                tbu=hasil_tbu,
                bbu=hasil_bbu,
                bbtb=hasil_bbtb
            )
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            raise
    
    def penangana_gejalan(bbu: str, tbu: str, bbtb: str):
        """
        Menentukan penanganan berdasarkan hasil prediksi
        Gabungkan rekomendasi dari tabel CSV sesuai status input
        """
        # Mapping dari CSV (ringkas, hanya string utama)
        bbu_map = {
            "risiko lebih": "Evaluasi pola makan dan aktivitas fisik. Konseling gizi seimbang (\"Isi Piringku\"), promosi aktivitas fisik, batasi screen time, pemantauan bulanan.",
            "normal": "Pantau tren pertumbuhan (naik/tidak). Lanjutkan pemantauan pertumbuhan bulanan di Posyandu, berikan pujian dan dukungan.",
            "kurang": "Triase Kritis: Ukur TB/PB untuk diagnosis banding wasting vs. stunting. Rujuk ke Puskesmas untuk asesmen lengkap. Tatalaksana berdasarkan diagnosis BB/TB dan TB/U.",
            "sangat kurang": "Rujuk Segera ke Puskesmas: Asesmen lengkap (BB/TB, TB/U, tanda bahaya). Tatalaksana gizi buruk dan/atau stunting berat sesuai protokol.",
        }
        tbu_map = {
            "tinggi": "Evaluasi klinis untuk menyingkirkan kelainan endokrin jika ekstrem (>+3 SD). Umumnya tidak ada intervensi. Lanjutkan pemantauan.",
            "normal": "Pastikan pertumbuhan linear mengikuti kurva. Lanjutkan pemantauan, dukung pola makan sehat.",
            "pendek": "Kaji riwayat 1.000 HPK, skrining anemia & infeksi, evaluasi asupan protein hewani. Intervensi Multi-faktorial: Peningkatan asupan protein hewani, suplementasi mikronutrien (Zinc, Fe), tata laksana infeksi, perbaikan sanitasi (PHBS), stimulasi psikososial.",
            "sangat pendek": "Sama seperti stunted, dengan penekanan pada pencarian penyakit penyerta. Sama seperti stunted, dengan intensitas lebih tinggi dan kemungkinan rujukan ke spesialis.",
        }
        bbtb_map = {
            "obesitas": "Skrining komorbiditas (hipertensi, dislipidemia, dll). Asesmen gaya hidup keluarga. Modifikasi Gaya Hidup: Pola makan sehat terstruktur, peningkatan aktivitas fisik (>60 menit/hari), pengurangan waktu sedentari (<2 jam/hari), modifikasi perilaku keluarga.",
            "gizi lebih": "Sama seperti obesitas.",
            "risiko gizi lebih": "Evaluasi pola makan dan aktivitas fisik. Konseling pencegahan, promosi gaya hidup sehat.",
            "gizi baik": "Pastikan berat badan naik sesuai kurva. Lanjutkan pemantauan dan praktik pemberian makan yang baik.",
            "gizi kurang": "Konfirmasi di Puskesmas, tes nafsu makan, singkirkan komplikasi medis. PMT Pemulihan selama 90 hari, konseling gizi intensif, pemantauan berat badan mingguan.",
            "gizi buruk": "Kegawatdaruratan Medis: Periksa komplikasi (nafsu makan, kesadaran, dehidrasi, dll). Tanpa Komplikasi: Rawat jalan dengan RUTF dan pemantauan mingguan. Dengan Komplikasi: Rawat Inap dan tatalaksana sesuai 10 Langkah WHO (F-75, F-100).",
        }

        # Normalisasi input
        bbu_key = bbu.strip().lower()
        tbu_key = tbu.strip().lower()
        bbtb_key = bbtb.strip().lower()

        # Gabungkan rekomendasi
        rekomendasi = []
        if bbu_key in bbu_map:
            rekomendasi.append(f"BB/U: {bbu_map[bbu_key]}")
        if tbu_key in tbu_map:
            rekomendasi.append(f"TB/U: {tbu_map[tbu_key]}")
        if bbtb_key in bbtb_map:
            rekomendasi.append(f"BB/TB: {bbtb_map[bbtb_key]}")

        if not rekomendasi:
            return "Tidak ada rekomendasi penanganan."
        return " ".join(rekomendasi)