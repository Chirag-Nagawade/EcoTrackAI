from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from pymongo import MongoClient
import joblib
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ml.feature_engineering import perform_feature_engineering

app = Flask(__name__)
app.secret_key = 'super_secret_eco_key'

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['carbon_tracker']
collection = db['user_predictions']

# Seed admin user
if not db.users.find_one({"email": "admin@gmail.com"}):
    hashed_password = generate_password_hash("admin123")
    db.users.insert_one({
        "username": "Admin",
        "email": "admin@gmail.com",
        "password": hashed_password
    })

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict['_id'])
        self.username = user_dict.get('username')
        self.email = user_dict.get('email')
        self.password = user_dict.get('password')
        self.is_admin = (self.email == "admin@gmail.com")

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if db.users.find_one({"email": email}):
            flash("Email already exists.")
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
        flash("Account created successfully. Please login.")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_data = db.users.find_one({"email": email})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.")
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.context_processor
def inject_user_stats():
    has_prediction = False
    if current_user.is_authenticated:
        count = collection.count_documents({"user_id": current_user.id}, limit=1)
        has_prediction = (count > 0)
    return dict(has_prediction=has_prediction)

# Load Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_regressor.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
@login_required
def form():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        if not os.path.exists(MODEL_PATH):
            return "Model not trained yet. Please run training pipeline.", 500
            
        model = joblib.load(MODEL_PATH)
        
        # Get data from form
        transport_mode = request.form.get('transport_mode')
        distance_km = float(request.form.get('distance_km', 0))
        electricity_kwh = float(request.form.get('electricity_kwh', 0))
        renewable_usage_pct = float(request.form.get('renewable_usage_pct', 0))
        food_type = request.form.get('food_type')
        waste_generated_kg = float(request.form.get('waste_generated_kg', 0))
        screen_time_hours = float(request.form.get('screen_time_hours', 0))
        eco_actions = int(request.form.get('eco_actions', 0))
        day_type = request.form.get('day_type', 'Weekday') # Default to Weekday
        
        # Create DataFrame
        input_data = pd.DataFrame([{
            'day_type': day_type,
            'transport_mode': transport_mode,
            'distance_km': distance_km,
            'electricity_kwh': electricity_kwh,
            'renewable_usage_pct': renewable_usage_pct,
            'food_type': food_type,
            'screen_time_hours': screen_time_hours,
            'waste_generated_kg': waste_generated_kg,
            'eco_actions': eco_actions
        }])
        
        # Feature Engineering (Inference Mode)
        X_processed = perform_feature_engineering(input_data, is_train=False)
        
        # Predict
        predicted_carbon = float(model.predict(X_processed)[0])
        predicted_carbon = round(predicted_carbon, 2)
        
        # Determine Carbon Level
        if predicted_carbon <= 5:
            carbon_level = "LOW"
        elif predicted_carbon <= 10:
            carbon_level = "MEDIUM"
        else:
            carbon_level = "HIGH"
            
        # Store in MongoDB
        record = {
            "user_id": current_user.id,
            "timestamp": datetime.now(),
            "day_type": day_type,
            "transport_mode": transport_mode,
            "distance_km": distance_km,
            "electricity_kwh": electricity_kwh,
            "renewable_usage_pct": renewable_usage_pct,
            "food_type": food_type,
            "waste_generated_kg": waste_generated_kg,
            "screen_time_hours": screen_time_hours,
            "eco_actions": eco_actions,
            "predicted_carbon": predicted_carbon,
            "carbon_level": carbon_level
        }
        inserted_id = collection.insert_one(record).inserted_id
        
        return redirect(url_for('result', id=str(inserted_id)))
        
    except Exception as e:
        import traceback
        return str(e) + "\n" + traceback.format_exc(), 400

@app.route('/result')
@login_required
def result():
    record_id = request.args.get('id')
    if not record_id:
        return redirect(url_for('home'))
        
    record = collection.find_one({"_id": ObjectId(record_id)})
    if not record:
        return "Record not found", 404
        
    # Ensure user can only see their own records
    if record.get('user_id') != current_user.id:
        return "Unauthorized", 403
        
    return render_template('result.html', record=record)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    if collection.count_documents({"user_id": current_user.id}, limit=1) == 0:
        flash("Please make a prediction first to unlock the dashboard.")
        return redirect(url_for('form'))
    return render_template('dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Unauthorized access.")
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    metrics = []
    feature_imp = []
    
    if current_user.is_admin:
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        metrics_file = os.path.join(models_dir, 'model_metrics.json')
        feature_imp_file = os.path.join(models_dir, 'feature_importance.json')
        
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                
        if os.path.exists(feature_imp_file):
            with open(feature_imp_file, 'r') as f:
                feature_imp = json.load(f)
            
    # Database stats
    user_query = {} if current_user.is_admin else {"user_id": current_user.id}
    total_predictions = collection.count_documents(user_query)
    
    levels = list(collection.aggregate([
        {"$match": user_query},
        {"$group": {"_id": "$carbon_level", "count": {"$sum": 1}}}
    ]))
    
    seven_days_ago = datetime.now() - timedelta(days=7)
    weekly_query = {"timestamp": {"$gte": seven_days_ago}}
    if not current_user.is_admin:
        weekly_query["user_id"] = current_user.id

    weekly_data = list(collection.aggregate([
        {"$match": weekly_query},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "total_carbon": {"$sum": "$predicted_carbon"}
        }},
        {"$sort": {"_id": 1}}
    ]))
    
    impact_breakdown = []
    if not current_user.is_admin:
        latest_prediction = collection.find_one(user_query, sort=[("timestamp", -1)])
        if latest_prediction:
            actual_pred = latest_prediction.get('predicted_carbon', 0)
            if actual_pred and actual_pred > 0:
                dist = latest_prediction.get('distance_km', 0)
                mode = latest_prediction.get('transport_mode', 'Walk')
                kwh = latest_prediction.get('electricity_kwh', 0)
                ren_pct = latest_prediction.get('renewable_usage_pct', 0)
                food = latest_prediction.get('food_type', 'Vegan')
                waste = latest_prediction.get('waste_generated_kg', 0)
                screen = latest_prediction.get('screen_time_hours', 0)

                # Transport emission factor (kg CO2/km)
                trans_factor = {'Car': 0.21, 'Bus': 0.089, 'Train': 0.041, 'Bike': 0.0, 'Walk': 0.0, 'EV': 0.053}
                trans_raw = dist * trans_factor.get(mode, 0)

                # Electricity: fossil portion only (kg CO2/kWh grid avg ~0.5)
                elec_raw = kwh * (1 - ren_pct / 100.0) * 0.5

                # Diet: kg CO2/meal/day rough estimates
                food_factor = {'Vegan': 1.5, 'Veg': 2.0, 'Mixed': 2.5, 'Non-Veg': 3.3}
                food_raw = food_factor.get(food, 1.5)

                # Waste: landfill emission factor ~0.5 kg CO2/kg
                waste_raw = waste * 0.5

                # Screen time: device power ~0.05 kWh/hr * 0.5 kg CO2/kWh
                screen_raw = screen * 0.05 * 0.5

                total_raw = trans_raw + elec_raw + food_raw + waste_raw + screen_raw
                if total_raw > 0:
                    scale = actual_pred / total_raw
                    impact_breakdown = [
                        {"category": "Transport", "impact": round(trans_raw * scale, 2)},
                        {"category": "Electricity", "impact": round(elec_raw * scale, 2)},
                        {"category": "Diet", "impact": round(food_raw * scale, 2)},
                        {"category": "Waste", "impact": round(waste_raw * scale, 2)},
                        {"category": "Screen Time", "impact": round(screen_raw * scale, 2)}
                    ]
                else:
                    # Flat equal split if no raw signal
                    per = round(actual_pred / 5, 2)
                    impact_breakdown = [
                        {"category": "Transport", "impact": per},
                        {"category": "Electricity", "impact": per},
                        {"category": "Diet", "impact": per},
                        {"category": "Waste", "impact": per},
                        {"category": "Screen Time", "impact": per}
                    ]
    
    response = {
        "total_predictions": total_predictions,
        "levels": levels,
        "weekly_data": weekly_data,
        "impact_breakdown": impact_breakdown
    }
    
    if current_user.is_admin:
        response["metrics"] = metrics
        response["feature_importance"] = feature_imp[:10]
        
    return jsonify(response)

@app.route('/api/admin/users_data')
@login_required
def api_admin_users_data():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
        
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    recent_predictions = list(collection.aggregate([
        {"$match": {"timestamp": {"$gte": seven_days_ago}}},
        {"$addFields": {"user_obj_id": {"$toObjectId": "$user_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "user_obj_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$unwind": {"path": "$user_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "username": {"$ifNull": ["$user_info.username", "Unknown User"]},
            "predicted_carbon": {"$round": ["$predicted_carbon", 2]},
            "carbon_level": 1,
            "timestamp": {"$dateToString": {"format": "%Y-%m-%d %H:%M", "date": "$timestamp"}}
        }},
        {"$sort": {"timestamp": -1}}
    ]))
    
    return jsonify(recent_predictions)

@app.route('/simulate', methods=['POST'])
@login_required
def simulate():
    try:
        if not os.path.exists(MODEL_PATH):
            return jsonify({"success": False, "error": "Model not trained."})
            
        model = joblib.load(MODEL_PATH)
        data = request.json
        input_data = pd.DataFrame([{
            'day_type': data.get('day_type', 'Weekday'),
            'transport_mode': data.get('transport_mode'),
            'distance_km': float(data.get('distance_km', 0)),
            'electricity_kwh': float(data.get('electricity_kwh', 0)),
            'renewable_usage_pct': float(data.get('renewable_usage_pct', 0)),
            'food_type': data.get('food_type'),
            'screen_time_hours': float(data.get('screen_time_hours', 0)),
            'waste_generated_kg': float(data.get('waste_generated_kg', 0)),
            'eco_actions': int(data.get('eco_actions', 0))
        }])
        
        X_processed = perform_feature_engineering(input_data, is_train=False)
        predicted_carbon = float(model.predict(X_processed)[0])
        return jsonify({"success": True, "predicted_carbon": round(predicted_carbon, 2)})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e) + " " + traceback.format_exc()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
