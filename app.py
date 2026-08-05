from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Load the trained model
model = joblib.load("model.joblib")

app = FastAPI(title="Iris Classifier API")

# Define the input data format (4 characteristics of the iris)
class IrisFeatures(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Health Check Interface (Required in production environments; K8s uses it to determine whether a service is alive)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Forecast API
@app.post("/predict")
def predict(features: IrisFeatures):
    data = np.array([[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width
    ]])
    prediction = model.predict(data)
    species = ["setosa", "versicolor", "virginica"]
    return {"prediction": species[int(prediction[0])]}

# uvicorn app:app --reload --port 8000

"""
curl http://127.0.0.1:8000/health
{"status":"ok"}


curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
{"prediction":"setosa"}
"""



