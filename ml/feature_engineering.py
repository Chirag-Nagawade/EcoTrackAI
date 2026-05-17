import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
import os

def perform_feature_engineering(df, is_train=True):
    """
    Performs feature engineering on the provided dataframe.
    If is_train=True, it fits the scaler and encoder, and saves them.
    If is_train=False, it loads the saved preprocessors and transforms the data.
    """
    df = df.copy()
    
    # 1. Drop irrelevant columns
    if 'user_id' in df.columns:
        df = df.drop(columns=['user_id'])
        
    if 'carbon_impact_level' in df.columns and is_train:
        # We drop the categorical target if it's there
        df = df.drop(columns=['carbon_impact_level'])
        
    # 2. Extract target if available and during training
    target_col = 'carbon_footprint_kg'
    y = None
    if target_col in df.columns:
        y = df[target_col].values
        df = df.drop(columns=[target_col])
        
    # 3. Create new features
    if 'electricity_kwh' in df.columns and 'renewable_usage_pct' in df.columns:
        df['fossil_fuel_electricity_kwh'] = df['electricity_kwh'] * (100 - df['renewable_usage_pct']) / 100.0
    
    # Identify categorical and numerical columns
    categorical_cols = ['day_type', 'transport_mode', 'food_type']
    # If there are columns in df that are not in categorical_cols, they are numerical
    numerical_cols = [col for col in df.columns if col not in categorical_cols]
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    preprocessor_path = os.path.join(models_dir, 'preprocessor.pkl')
    
    if is_train:
        # Define the ColumnTransformer for OneHotEncoding and Scaling
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_cols),
                ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_cols)
            ])
        
        X_processed = preprocessor.fit_transform(df)
        
        # Save the preprocessor
        joblib.dump(preprocessor, preprocessor_path)
        
        # Get feature names for importance later
        num_features = numerical_cols
        cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_cols).tolist()
        feature_names = num_features + cat_features
        
        joblib.dump(feature_names, os.path.join(models_dir, 'feature_names.pkl'))
        
        return X_processed, y, feature_names
    else:
        # Inference mode
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError("Preprocessor not found. Please train models first.")
            
        preprocessor = joblib.load(preprocessor_path)
        # Ensure input df has the same columns in the same order as expected by preprocessor
        # (ColumnTransformer usually relies on column names if input is DataFrame)
        X_processed = preprocessor.transform(df)
        return X_processed

if __name__ == "__main__":
    print("Feature Engineering module loaded.")
    print("Feature Engineering module loaded.")
