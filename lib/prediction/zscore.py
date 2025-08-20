from pygrowup import Observation
import pandas as pd
import logging

from .models import ZscoreResults

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZScoreCalculator():
    def __init__(self):
        # Initialize using pygrowup2 Observation-based approach
        logger.info("Initializing ZScore calculator using pygrowup2")

    def calculate_zscore(self, age_months: int, weight_kg: float, height_cm: float, sex: str) -> ZscoreResults:
        """
        Menghitung Z-scores menggunakan pygrowup2 library
        
        Args:
            age_months: Usia dalam bulan
            weight_kg: Berat badan dalam kg
            height_cm: Tinggi badan dalam cm  
            sex: Jenis kelamin ('M' untuk male, 'F' untuk female)
        
        Returns:
            ZscoreResults: Z-scores untuk BB/U, TB/U, dan BB/TB
        """
        try:
            logger.debug(f"Z-score calculation: age_months={age_months}, weight_kg={weight_kg}, height_cm={height_cm}, sex={sex}")
            
            # Convert sex to pygrowup2 format
            sex_pygrowup = Observation.MALE if sex.upper() in ['M', 'L', 'MALE', 'LAKI'] else Observation.FEMALE
            
            # Create observation object
            obs = Observation(sex=sex_pygrowup, age_in_months=age_months)
            
            # Weight-for-age (BB/U)
            z_wfa = obs.weight_for_age(weight_kg)
            logger.debug(f"Weight-for-Age Z-score: {z_wfa}")
            
            # Length/Height-for-age (TB/U) 
            z_hfa = obs.length_or_height_for_age(height_cm)
            logger.debug(f"Height-for-Age Z-score: {z_hfa}")
            
            # Weight-for-height (BB/TB)
            z_wfh = obs.weight_for_height(weight_kg, height_cm)
            logger.debug(f"Weight-for-Height Z-score: {z_wfh}")
            
            return ZscoreResults(
                calculated=True,
                bbu=float(z_wfa) if z_wfa is not None else None,
                tbu=float(z_hfa) if z_hfa is not None else None,
                bbtb=float(z_wfh) if z_wfh is not None else None
            )
        except Exception as e:
            logger.error(f"Error calculating z-scores: {e}")
            return ZscoreResults(
                calculated=False,
                bbu=None,
                tbu=None,
                bbtb=None
            )