import sys
import joblib
import numpy as np
import pandas as pd
import warnings
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

            modelpath = "D:/NEW PROJECT/mlstunting/sourceml/models/"
            # Load model XGBoost
            self.models['tbu'] = joblib.load(modelpath + "model_tbu.pkl")
            self.models['bbu'] = joblib.load(modelpath + "model_bbu.pkl")
            self.models['bbtb'] = joblib.load(modelpath + "model_bbtb.pkl")

            # Load encoders
            self.encoders = joblib.load(modelpath + "encoders.pkl")

            print("✅ Model dan encoder berhasil dimuat!")
            print(f"   - Model TB/U: {type(self.models['tbu']).__name__}")
            print(f"   - Model BB/U: {type(self.models['bbu']).__name__}")
            print(f"   - Model BB/TB: {type(self.models['bbtb']).__name__}")
            
        except FileNotFoundError as e:
            print(f"❌ Error: File model tidak ditemukan - {e}")
            print("   Pastikan file .pkl ada di direktori yang sama")
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
    
    