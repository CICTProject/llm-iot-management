Using Edge AI for health anomalies detection.

## Scenario:
- Alert patient's health anomalies to nurse/doctors computers

We have health sensors distributed in room that check patients's health constantly, these health sensors containing blood pressure, temperature, cardinal... (health information). When it detects health risks, the sensor will alert to the nurses and doctors its predictions, using EdgeAI and LLM.

## Edge AI
This is the process using AI algorithms and AI models on IOT devices (in this case, health sensors).

It processes data locally on small devices, using Neural Network or Deep Learning models.

The reason we choosing this approach is EdgeAI can work on real-time, preserve data privacy.
[resource](https://www.ibm.com/fr-fr/think/topics/edge-vs-cloud-ai)

## Data
- Health care dataset: https://www.kaggle.com/datasets/prasad22/healthcare-dataset
- Health risk dataset: https://www.kaggle.com/datasets/ludocielbeckett/health-risk-prediction-anonymized-real-data/data

## How to build
### Layer 1: Edge AI (On the Sensor / IoT Device)
We train the model on the Kaggle healthcare dataset (blood pressure, temperature, heart rate, etc.) to classify readings as normal or anomalous.

Then, we convert the model to a lightweight format so it fits on small hardware.

We test by running inference locally, when the sensor takes a reading, the model scores it immediately without sending raw data to a server. The model never sends raw patient vitals over a network but only the result (e.g., "anomaly detected, confidence 94%") gets transmitted to preserve privacy.

## Steps
### Step 1: Data Preparation
Download the Kaggle dataset, clean it, and define what counts as an "anomaly".
### Step 2: Train the Edge Model
Train a small classifier (Random Forest, or a small neural net). Then, distill to a smaller net. Convert to TFLite. This simulates what runs on the sensor.
### Step 3: Simulate the Sensor
We write a Python script that reads rows from the dataset and simulates a sensor sending data + running the edge model.
### Step 4: CrewAI Pipeline (Trang's part)
Wire up your agents.py / tasks.py / crew.py so that when an anomaly is detected, the crew processes it and produces a structured alert.
### Step 5: Build the Dashboard
A simple web UI (React) where nurses/doctors see live alerts coming in with severity, patient info, and recommendations.
### Step 6: Connect via ONOS
Configure the network routing so sensor messages reach your CrewAI backend.

## Sensor
We use ESP32 - a sensor being used commonly in healthcare.
Spec:
- RAM: 520KB. Model must fit in ~100–200KB max.
- Flash: 4MB. Stored model budget. 
- CPU: 240 MHz Xtensa LX6 -> No FPU for heavy math
- Battery operated: Inference must be fast & low-power

# note
add module joblib and scikit-learn to poetry
right now: 
pip install joblib
pip install scikit-learn