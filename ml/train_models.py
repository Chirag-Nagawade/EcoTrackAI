import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from feature_engineering import perform_feature_engineering

def train_and_evaluate():
    # Load dataset
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'personal_carbon_footprint_behavior.csv')
    df = pd.read_csv(data_path)
    
    # Feature Engineering
    X, y, feature_names = perform_feature_engineering(df, is_train=True)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Multiple Linear Regression': LinearRegression(),
        'Decision Tree Regressor': DecisionTreeRegressor(random_state=42),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42),
        'AdaBoost Regressor': AdaBoostRegressor(n_estimators=50, random_state=42)
    }
    
    results = []
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    best_r2 = -float('inf')
    best_model_name = None
    
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results.append({
            'Model': name,
            'MAE': round(mae, 4),
            'RMSE': round(rmse, 4),
            'R2 Score': round(r2, 4)
        })
        
        # Save model
        model_filename = name.replace(' ', '_').lower() + '.pkl'
        joblib.dump(model, os.path.join(models_dir, model_filename))
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            
        # Extract Feature Importance if Random Forest
        if name == 'Random Forest Regressor':
            importances = model.feature_importances_
            feature_importance = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values(by='Importance', ascending=False)
            
            # Save feature importance to json
            feature_importance_dict = feature_importance.to_dict(orient='records')
            with open(os.path.join(models_dir, 'feature_importance.json'), 'w') as f:
                json.dump(feature_importance_dict, f, indent=4)
                
    # Save results to json
    with open(os.path.join(models_dir, 'model_metrics.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Training Completed.")
    print(f"Best Model: {best_model_name} with R2 = {best_r2}")
    
    results_df = pd.DataFrame(results)
    print("\nModel Comparison:")
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    train_and_evaluate()
