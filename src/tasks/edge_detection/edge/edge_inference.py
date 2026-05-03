""" Simulates the Edge AI inference layer that would run ON the health sensor device"""
import json, time, os
import numpy as np
import pandas as pd
import joblib
from dataclasses import dataclass, asdict
from fastapi import FastAPI, Body
from pydantic import BaseModel, ConfigDict
from typing import List

from typing import Optional
# from sklearn.ensemble import RandomForestClassifier
MODEL_PATH = "../cloud/cloud_model.1.0.1/cloud_model.1.0.1.pkl"
SCALER_PATH = "../cloud/cloud_model.1.0.1/standard_scaler.pkl"
METADATA_PATH = "../cloud/cloud_model.1.0.1/metadata_cloud_model.json"

@dataclass
class SensorReading(BaseModel):
    """Raw vitals captured from a patient's bedside sensor."""
    patient_id              : str
    device_id               : str
    respiratory_rate        : float
    oxygen_saturation       : float
    systolic_bp             : float
    # diastolic_bp             : float
    heart_rate              : float
    temperature             : float
    timestamp              : Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_id": "P-001",
                "device_id": "esp-01",
                "respiratory_rate": 28,
                "oxygen_saturation": 92,
                "systolic_bp": 116,
                "heart_rate": 151,
                "temperature": 38.5
            }
        }
    )

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class PredictionResponse(BaseModel):
    patient_id: str
    is_anomaly: bool
    triggered_vitals: List[str]

@dataclass
class AnomalyAlert:
    """ The alert that transmitted over the network to the server."""
    patient_id          : str
    timestamp           : float
    is_anomaly          : bool  # we alert 1 when risk is high
    confidence          : float
    triggered_vitals    : list
    model_version       : str
    device_id           : str

class EdgeAIInference:
    """
    Lightweight inference engine designed to run on alert sensor.
    Loads the trained model once, then scores each incoming sensor reading in real-time.
    """
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at '{MODEL_PATH}'.\n"
            )
        self._model = joblib.load(MODEL_PATH)
        self._scaler = joblib.load(SCALER_PATH)
        # self._model = Pipeline([
        #     ("scaler", joblib.load(SCALER_PATH)),
        #     ("mlp", joblib.load(MODEL_PATH))
        # ])
        with open(METADATA_PATH) as f:
            self._meta = json.load(f)
        self._features = self._meta["feature_columns"]
        self._ranges = self._meta["normal_ranges"]
        self._version = self._meta["model_version"]

    def _engineer_features(self, r: SensorReading) -> np.ndarray:
        """Compute engineered features."""
        feature_map = {
            'respiratory_rate'  : r.respiratory_rate,
            'oxygen_saturation' : r.oxygen_saturation,
            # 'diastolic blood pressure'      : r.diastolic_bp,
            'systolic_bp'       : r.systolic_bp,
            'heart_rate'        : r.heart_rate,
            'temperature'       : r.temperature,
        }
        return pd.DataFrame([[feature_map[f] for f in self._features]], columns=self._features)
    
    def _check_vital_breaches(self, r: SensorReading) -> list:
        """ Return list of vital names that are outside normal range."""
        checks = {
            'respiratory_rate'  : r.respiratory_rate,
            'oxygen_saturation' : r.oxygen_saturation,
            'systolic_bp'       : r.systolic_bp,
            'heart_rate'        : r.heart_rate,
            'temperature'       : r.temperature,
        }
        breached=[]
        for vital, value in checks.items():
            rng = self._ranges.get(vital, {})
            lo, hi = rng.get("min", -999), rng.get("max", 9999)
            if value < lo or value > hi:
                direction = "LOW" if value < lo else "HIGH"
                breached.append(f"{vital}={value} ({direction})")
        return breached
    

    # Public API
    def predict(self, reading: SensorReading) -> AnomalyAlert:
        """ Run inference on a single SensorReading."""
        t0 = time.perf_counter()
        X  = self._engineer_features(reading)
        X_scaled = self._scaler.transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=self._features)
        proba = float(self._model.predict(X_scaled).clip(0, 1)[0])
        pred =  (proba > 0.46)
        is_anom = (pred == 1)
        elapsed = (time.perf_counter() - t0) * 1000

        breaches = self._check_vital_breaches(reading)

        alert = AnomalyAlert(
            patient_id=reading.patient_id,
            timestamp=reading.timestamp,
            is_anomaly=is_anom,
            confidence= round(proba,4),
            triggered_vitals= breaches,
            model_version   = self._version,
            device_id= reading.device_id,
        )

        anom = "ANOMALY" if is_anom else "Normal "
        # Later put on debug log 
        print(f"Probability: {proba}")
        print(f"[EdgeAI] {anom} | patient={reading.patient_id} | {elapsed:.2f}ms")
        return alert
    def to_dict(self, alert: AnomalyAlert) -> dict:
        return asdict(alert)
    

# if __name__ == "__main__":
#     engine = EdgeAIInference()
#     print(f"\nModel loaded.")

#     test_cases = [
#         SensorReading(patient_id="P-001", device_id="esp-01",respiratory_rate=28, oxygen_saturation=92, systolic_bp=116, heart_rate=151,
#                       temperature=38.5,),
#         SensorReading(patient_id="P-002", device_id="esp-02",respiratory_rate=15, oxygen_saturation=98.508265, systolic_bp=131, heart_rate=63,
#                       temperature=37.052049,),
#         SensorReading(patient_id="P-003", device_id="esp-03",respiratory_rate=30, oxygen_saturation=98.508265, systolic_bp=150, heart_rate=15,
#         temperature=42.0,)
#     ]
#     print("\n── Running test cases ──")
#     for r in test_cases:
#         alert = engine.predict(r)
#         if alert.is_anomaly:
#             print(f"  Triggers: {alert.triggered_vitals}\n")

app = FastAPI()
engine = EdgeAIInference()
print("Model loaded.")
@app.post("/predict", response_model=PredictionResponse)
def predict(
    reading: SensorReading = Body(
        ...,
        openapi_examples={
            "anomaly_case": {
                "summary": "Abnormal vitals",
                "value": {
                    "patient_id": "P-001",
                    "device_id": "esp-01",
                    "respiratory_rate": 28,
                    "oxygen_saturation": 92,
                    "systolic_bp": 116,
                    "heart_rate": 151,
                    "temperature": 38.5
                },
            },
            "normal_case": {
                "summary": "Normal vitals",
                "value": {
                    "patient_id": "P-002",
                    "device_id": "esp-02",
                    "respiratory_rate": 15,
                    "oxygen_saturation": 98.5,
                    "systolic_bp": 120,
                    "heart_rate": 70,
                    "temperature": 36.8
                },
            },
        },
    )
    ):
    alert = engine.predict(reading)

    return {
        "patient_id": reading.patient_id,
        "is_anomaly": alert.is_anomaly,
        "triggered_vitals": alert.triggered_vitals,
    }