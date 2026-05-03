Using Edge AI for health anomalies detection.

## Scenario:
- Alert patient's health anomalies to nurse/doctors computers

We have health sensors distributed in room that check patients's health constantly, these health sensors containing blood pressure, temperature, cardinal... (health information). When it detects health risks, the sensor will alert to the nurses and doctors its predictions, using EdgeAI and LLM.

## Edge AI
This is the process using AI algorithms and AI models on IOT devices (in this case, health sensors).

It processes data locally on small devices, using Neural Network or Deep Learning models.

The reason we choosing this approach is EdgeAI can work on real-time, preserve data privacy.
[resource](https://www.ibm.com/fr-fr/think/topics/edge-vs-cloud-ai)


## How to build
### Edge AI (On the Sensor / IoT Device)
We train the model on the Kaggle healthcare dataset (blood pressure, temperature, heart rate, etc.) to classify readings as normal or anomalous.

Then, we convert the model to a lightweight format so it fits on small hardware.

We test by running inference locally, when the sensor takes a reading, the model scores it immediately without sending raw data to a server. The model never sends raw patient vitals over a network but only the result (e.g., "anomaly detected, confidence 94%") gets transmitted to preserve privacy.

## Sensor
We use ESP32 - a sensor being used commonly in healthcare.
Spec:
- RAM: 520KB. Model must fit in ~100–200KB max.
- Flash: 4MB. Stored model budget. 
- CPU: 240 MHz Xtensa LX6 -> No FPU for heavy math
- Battery operated: Inference must be fast & low-power

## Running the Application
```bash
python -m poetry run uvicorn edge.edge_inference.py:app --host 0.0.0.0 --port 8001

```