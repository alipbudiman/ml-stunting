"""
Comprehensive ML Pipeline Improvements
=====================================

This script implements improvements across 4 key areas:
1. Fix calculation errors (already completed in zscore_replace.py)
2. Dataset expansion and quality enhancement
3. Robust validation methods
4. Ensemble methods for production readiness

Author: Enhanced by AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class StuntingMLPipeline:
    """
    Enhanced ML Pipeline untuk prediksi stunting dengan improvements:
    - Dataset expansion strategies
    - Robust validation methods  
    - Ensemble methods
    - Better error handling
    """
    
    def __init__(self, data_path='stunting/data-stunting-zscore-corrected.csv'):
        self.data_path = data_path
        self.df = None
        self.X = None
        self.y = None
        self.models = {}
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def load_and_prepare_data(self):
        """Load data with corrected Z-scores and prepare for modeling"""
        print("=== LOADING AND PREPARING DATA ===")
        
        # Load corrected dataset
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Dataset loaded: {len(self.df)} records")
        except FileNotFoundError:
            print(f"File {self.data_path} not found. Using original dataset...")
            self.df = pd.read_csv('stunting/data-stunting.csv')
            
        # Basic info
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        
        # Check for missing values
        missing_info = self.df.isnull().sum()
        if missing_info.sum() > 0:
            print("\nMissing values found:")
            print(missing_info[missing_info > 0])
        else:
            print("No missing values found ✓")
            
        # Print available columns for debugging
        print(f"\nAvailable columns: {list(self.df.columns)}")
            
        return self.df
    
    def data_quality_analysis(self):
        """Comprehensive data quality analysis"""
        print("\n=== DATA QUALITY ANALYSIS ===")
        
        # Class distribution
        target_column = None
        if 'Status Gizi' in self.df.columns:
            target_column = 'Status Gizi'
        elif 'BB/TB' in self.df.columns:
            target_column = 'BB/TB'
        elif 'Naik Berat Badan' in self.df.columns:
            target_column = 'Naik Berat Badan'
            
        if target_column:
            status_counts = self.df[target_column].value_counts()
            print(f"\nTarget variable ({target_column}) distribution:")
            for status, count in status_counts.items():
                print(f"  {status}: {count} ({count/len(self.df)*100:.1f}%)")
                
            # Check for class imbalance
            min_class = status_counts.min()
            max_class = status_counts.max()
            imbalance_ratio = max_class / min_class
            print(f"\nClass imbalance ratio: {imbalance_ratio:.2f}")
            if imbalance_ratio > 3:
                print("⚠️  Significant class imbalance detected!")
        else:
            print("No suitable target column found for classification")
                
        # Feature statistics
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        print(f"\nNumeric features statistics:")
        print(self.df[numeric_cols].describe())
        
        # Outlier detection
        print(f"\nOutlier detection (values beyond 3 std):")
        for col in numeric_cols:
            if col in ['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']:
                outliers = len(self.df[abs(self.df[col]) > 3])
                if outliers > 0:
                    print(f"  {col}: {outliers} outliers ({outliers/len(self.df)*100:.1f}%)")
    
    def expand_dataset_features(self):
        """Create additional features to expand the dataset"""
        print("\n=== FEATURE EXPANSION ===")
        
        # BMI calculation
        if 'Berat' in self.df.columns and 'Tinggi' in self.df.columns:
            self.df['BMI'] = self.df['Berat'] / ((self.df['Tinggi']/100) ** 2)
            print("✓ Added BMI feature")
            
        # Age categories
        if 'Usia' in self.df.columns:
            # Convert age to numeric if it's not
            if self.df['Usia'].dtype == 'object':
                self.df['Usia_numeric'] = self.df['Usia'].str.extract(r'(\d+)').astype(float)
            else:
                self.df['Usia_numeric'] = self.df['Usia']
                
            # Age categories
            self.df['Age_Category'] = pd.cut(self.df['Usia_numeric'], 
                                           bins=[0, 12, 24, 36, 48, 60], 
                                           labels=['0-12mo', '12-24mo', '24-36mo', '36-48mo', '48-60mo'])
            print("✓ Added age categories")
            
        # Z-score combinations
        zscore_cols = ['ZS BB/U', 'ZS TB/U', 'ZS BB/TB']
        if all(col in self.df.columns for col in zscore_cols):
            # Combined Z-score indicator
            self.df['ZScore_Risk_Count'] = (self.df[zscore_cols] < -2).sum(axis=1)
            
            # Severe malnutrition indicator
            self.df['Severe_Malnutrition'] = (self.df[zscore_cols] < -3).any(axis=1).astype(int)
            
            # Z-score average
            self.df['ZScore_Average'] = self.df[zscore_cols].mean(axis=1)
            
            print("✓ Added Z-score derived features")
            
        print(f"Dataset expanded to {self.df.shape[1]} features")
        return self.df
    
    def prepare_features(self):
        """Prepare features for modeling"""
        print("\n=== FEATURE PREPARATION ===")
        
        # Select features for modeling
        feature_cols = []
        
        # Numeric features
        numeric_features = ['Berat', 'Tinggi', 'ZS BB/U', 'ZS TB/U', 'ZS BB/TB']
        if 'BMI' in self.df.columns:
            numeric_features.append('BMI')
        if 'ZScore_Risk_Count' in self.df.columns:
            numeric_features.extend(['ZScore_Risk_Count', 'Severe_Malnutrition', 'ZScore_Average'])
        if 'Usia_numeric' in self.df.columns:
            numeric_features.append('Usia_numeric')
            
        feature_cols.extend(numeric_features)
        
        # Categorical features
        categorical_features = []
        if 'Jenis Kelamin' in self.df.columns:
            categorical_features.append('Jenis Kelamin')
        if 'Age_Category' in self.df.columns:
            categorical_features.append('Age_Category')
            
        # Encode categorical features
        df_processed = self.df.copy()
        for cat_col in categorical_features:
            if cat_col in df_processed.columns:
                df_processed[f'{cat_col}_encoded'] = self.label_encoder.fit_transform(df_processed[cat_col].astype(str))
                feature_cols.append(f'{cat_col}_encoded')
        
        # Prepare X and y
        self.X = df_processed[feature_cols].fillna(0)
        
        # Determine target column
        if 'Status Gizi' in df_processed.columns:
            self.y = df_processed['Status Gizi']
        elif 'BB/TB' in df_processed.columns:
            self.y = df_processed['BB/TB']
        else:
            # Create binary stunting classification based on Z-scores
            print("Creating binary stunting classification based on Z-scores...")
            stunting_condition = (
                (df_processed['ZS TB/U'] < -2) |  # Height-for-age stunting
                (df_processed['ZS BB/U'] < -2)    # Weight-for-age underweight
            )
            self.y = stunting_condition.map({True: 'Stunting', False: 'Normal'})
            print("Target variable created: Stunting vs Normal based on WHO standards")
        
        print(f"Features selected: {feature_cols}")
        print(f"Feature matrix shape: {self.X.shape}")
        print(f"Target classes: {self.y.value_counts().to_dict()}")
        
        return self.X, self.y
    
    def robust_validation_setup(self):
        """Setup robust cross-validation strategy"""
        print("\n=== ROBUST VALIDATION SETUP ===")
        
        # Stratified K-Fold for balanced splits
        self.cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        print("✓ Stratified 5-Fold Cross-Validation configured")
        
        # Train-test split with stratification
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42, stratify=self.y
        )
        
        print(f"Training set: {self.X_train.shape[0]} samples")
        print(f"Test set: {self.X_test.shape[0]} samples")
        
        # Scale features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print("✓ Feature scaling applied")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def handle_class_imbalance(self):
        """Handle class imbalance using adaptive strategy"""
        print("\n=== HANDLING CLASS IMBALANCE ===")
        
        # Check current distribution
        class_counts = pd.Series(self.y_train).value_counts()
        print("Original class distribution:")
        print(class_counts)
        
        # For severe imbalance, combine rare classes or use different strategy
        min_samples_for_smote = 6  # SMOTE requires at least 6 samples
        rare_classes = class_counts[class_counts < min_samples_for_smote]
        
        if len(rare_classes) > 0:
            print(f"\nRare classes detected (< {min_samples_for_smote} samples): {list(rare_classes.index)}")
            print("Using simplified binary classification: Normal vs At-Risk")
            
            # Create binary classification: Normal vs At-Risk
            def simplify_classes(status):
                if status == 'Gizi Baik':
                    return 'Normal'
                else:
                    return 'At-Risk'
            
            # Apply to both train and test sets
            self.y_train_simplified = self.y_train.apply(simplify_classes)
            self.y_test_simplified = self.y_test.apply(simplify_classes)
            
            # Check new distribution
            simplified_counts = pd.Series(self.y_train_simplified).value_counts()
            print("\nSimplified class distribution:")
            print(simplified_counts)
            
            # Apply SMOTE to simplified classes
            if simplified_counts.min() >= min_samples_for_smote:
                smote = SMOTE(random_state=42, k_neighbors=min(5, simplified_counts.min()-1))
                self.X_train_balanced, self.y_train_balanced = smote.fit_resample(self.X_train_scaled, self.y_train_simplified)
                self.y_test = self.y_test_simplified  # Update test set too
            else:
                print("Using original imbalanced data with class weights")
                self.X_train_balanced = self.X_train_scaled
                self.y_train_balanced = self.y_train_simplified
                self.y_test = self.y_test_simplified
            
            # Encode labels for XGBoost compatibility
            self.target_label_encoder = LabelEncoder()
            self.y_train_balanced = self.target_label_encoder.fit_transform(self.y_train_balanced)
            self.y_test = self.target_label_encoder.transform(self.y_test)
        else:
            # Apply SMOTE normally
            k_neighbors = min(5, class_counts.min()-1)
            smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
            self.X_train_balanced, self.y_train_balanced = smote.fit_resample(self.X_train_scaled, self.y_train)
            
            # Encode labels for XGBoost compatibility
            self.target_label_encoder = LabelEncoder()
            self.y_train_balanced = self.target_label_encoder.fit_transform(self.y_train_balanced)
            self.y_test = self.target_label_encoder.transform(self.y_test)
        
        # Check final distribution
        balanced_counts = pd.Series(self.y_train_balanced).value_counts()
        print("\nFinal balanced class distribution:")
        if hasattr(self, 'target_label_encoder'):
            # Show original labels if encoded
            original_labels = self.target_label_encoder.inverse_transform(balanced_counts.index)
            for i, (encoded, count) in enumerate(balanced_counts.items()):
                print(f"  {original_labels[i]} ({encoded}): {count}")
        else:
            print(balanced_counts)
        
        return self.X_train_balanced, self.y_train_balanced
    
    def train_individual_models(self):
        """Train individual models for ensemble"""
        print("\n=== TRAINING INDIVIDUAL MODELS ===")
        
        # Define models with class weight handling
        models = {
            'XGBoost': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
        }
        
        # Train and evaluate each model
        cv_scores = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Cross-validation
            cv_score = cross_val_score(model, self.X_train_balanced, self.y_train_balanced, 
                                     cv=self.cv_strategy, scoring='accuracy')
            cv_scores[name] = cv_score
            
            # Train on full training set
            model.fit(self.X_train_balanced, self.y_train_balanced)
            self.models[name] = model
            
            # Test set performance
            test_score = model.score(self.X_test_scaled, self.y_test)
            
            print(f"  CV Score: {cv_score.mean():.4f} (+/- {cv_score.std()*2:.4f})")
            print(f"  Test Score: {test_score:.4f}")
        
        return cv_scores
    
    def create_ensemble_model(self):
        """Create ensemble model using voting"""
        print("\n=== CREATING ENSEMBLE MODEL ===")
        
        # Select best performing models for ensemble
        estimators = [
            ('xgb', self.models['XGBoost']),
            ('rf', self.models['RandomForest']),
            ('gb', self.models['GradientBoosting'])
        ]
        
        # Create voting classifier
        self.ensemble_model = VotingClassifier(
            estimators=estimators,
            voting='soft'  # Use probability-based voting
        )
        
        # Train ensemble
        self.ensemble_model.fit(self.X_train_balanced, self.y_train_balanced)
        
        # Evaluate ensemble
        ensemble_cv_score = cross_val_score(self.ensemble_model, self.X_train_balanced, 
                                          self.y_train_balanced, cv=self.cv_strategy, scoring='accuracy')
        ensemble_test_score = self.ensemble_model.score(self.X_test_scaled, self.y_test)
        
        print(f"Ensemble CV Score: {ensemble_cv_score.mean():.4f} (+/- {ensemble_cv_score.std()*2:.4f})")
        print(f"Ensemble Test Score: {ensemble_test_score:.4f}")
        
        return self.ensemble_model
    
    def comprehensive_evaluation(self):
        """Comprehensive model evaluation"""
        print("\n=== COMPREHENSIVE EVALUATION ===")
        
        # Predictions
        y_pred_ensemble = self.ensemble_model.predict(self.X_test_scaled)
        
        # Classification report
        print("Ensemble Model Classification Report:")
        print(classification_report(self.y_test, y_pred_ensemble))
        
        # Feature importance (from XGBoost)
        if 'XGBoost' in self.models:
            feature_importance = self.models['XGBoost'].feature_importances_
            feature_names = self.X.columns
            
            # Create feature importance DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': feature_importance
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Feature Importances:")
            print(importance_df.head(10))
            
        return y_pred_ensemble
    
    def run_complete_pipeline(self):
        """Run the complete enhanced ML pipeline"""
        print("🚀 STARTING COMPREHENSIVE ML PIPELINE")
        print("="*50)
        
        try:
            # Step 1: Load and prepare data
            self.load_and_prepare_data()
            
            # Step 2: Data quality analysis
            self.data_quality_analysis()
            
            # Step 3: Feature expansion
            self.expand_dataset_features()
            
            # Step 4: Feature preparation
            self.prepare_features()
            
            # Step 5: Robust validation setup
            self.robust_validation_setup()
            
            # Step 6: Handle class imbalance
            self.handle_class_imbalance()
            
            # Step 7: Train individual models
            cv_scores = self.train_individual_models()
            
            # Step 8: Create ensemble model
            self.create_ensemble_model()
            
            # Step 9: Comprehensive evaluation
            predictions = self.comprehensive_evaluation()
            
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*50)
            
            return {
                'models': self.models,
                'ensemble': self.ensemble_model,
                'cv_scores': cv_scores,
                'predictions': predictions,
                'test_accuracy': self.ensemble_model.score(self.X_test_scaled, self.y_test)
            }
            
        except Exception as e:
            print(f"❌ Pipeline failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main function to run the comprehensive improvements"""
    
    # Initialize pipeline
    pipeline = StuntingMLPipeline()
    
    # Run complete pipeline
    results = pipeline.run_complete_pipeline()
    
    if results:
        print(f"\n📊 FINAL RESULTS SUMMARY:")
        print(f"   • Best Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"   • Models Trained: {len(results['models'])}")
        print(f"   • Ensemble Created: ✓")
        print(f"   • Validation Strategy: Stratified 5-Fold CV")
        print(f"   • Class Imbalance: Handled with SMOTE")
        
        # Save ensemble model (optional)
        try:
            import joblib
            joblib.dump(results['ensemble'], 'stunting_ensemble_model.pkl')
            print(f"   • Model Saved: stunting_ensemble_model.pkl")
        except:
            print(f"   • Model Saving: Failed (joblib not available)")

if __name__ == "__main__":
    main()
