# EcoTrack AI 🌿

EcoTrack AI is a Carbon Footprint tracking platform powered by Machine Learning pipelines. It helps calculate, predict, and analyze carbon footprints using regression models.

---

## 📂 Project Structure

*   `app.py`: Main Flask web application and APIs.
*   `requirements.txt`: Python package dependencies.
*   `data/`: Carbon footprint behavior dataset.
*   `ml/`: Model training, preprocessing, and visual analytics scripts.
*   `models/`: Serialized ML models and preprocessor pipelines.

---

## ⚙️ Execution Steps

Follow these basic commands to run the application locally:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```
*Access the site in your browser at: `http://127.0.0.1:5000`*

### 3. Run Machine Learning Scripts (Optional)
If you want to train models or regenerate evaluation graphics:

*   **Run Feature Engineering:**
    ```bash
    python ml/feature_engineering.py
    ```
*   **Train & Save Models:**
    ```bash
    python ml/train_models.py
    ```

