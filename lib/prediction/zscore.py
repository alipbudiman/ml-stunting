from pygrowup import Calculator
import pandas as pd
import logging

from .models import ZscoreResults

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZScoreCalculator():
    def __init__(self):
        # Initialize the pygrowup calculator
        self.calc = Calculator(adjust_height_data=False, include_cdc=False)

    def calculate_zscore(self, age_months: int, weight_kg: float, height_cm: float, sex: str) -> ZscoreResults:
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
            logger.debug(f"Z-score calculation: age_months={age_months}, weight_kg={weight_kg}, height_cm={height_cm}, sex={sex}")
            
            # Weight-for-age (BB/U)
            z_wfa = self.calc.wfa(measurement=weight_kg, age_in_months=age_months, sex=sex)
            logger.debug(f"Weight-for-Age Z-score: {z_wfa}")
            
            # Length/Height-for-age (TB/U) 
            z_hfa = self.calc.lhfa(measurement=height_cm, age_in_months=age_months, sex=sex)
            logger.debug(f"Height-for-Age Z-score: {z_hfa}")
            
            # Weight-for-height (BB/TB)
            z_wfh = self.calc.wfh(measurement=weight_kg, age_in_months=age_months, sex=sex, height=height_cm)
            logger.debug(f"Weight-for-Height Z-score: {z_wfh}")
            
            return ZscoreResults(
                calculated=True,
                bbu=z_wfa,
                tbu=z_hfa,
                bbtb=z_wfh
            )
        except Exception as e:
            logger.error(f"Error calculating z-scores: {e}")
            return ZscoreResults(
                calculated=False,
                bbu=None,
                tbu=None,
                bbtb=None
            )