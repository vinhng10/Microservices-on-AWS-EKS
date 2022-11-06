import joblib
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load model and scaler:
artifacts = Path("artifacts")
scaler = joblib.load(artifacts / "scaler.joblib")
model = joblib.load(artifacts / "model.joblib")

# Initialize app:
app = FastAPI()

# Declare data models:
class Point(BaseModel):
    x: float
    y: float
    

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "This is AI prediction microservice."}


@app.post("/predict", status_code=status.HTTP_200_OK)
async def predict(point: Point | None):
    scaled_point = scaler.transform([[point.x, point.y]])
    prediction = model.predict(scaled_point)
    return {"prediction": int(prediction[0])}