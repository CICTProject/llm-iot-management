# MCP Agent Tools for ESP-32 Cam-based in Medical IoT Environments

## 1.1 Device Monitoring Agent

---

## 1.2 Edge Anomaly Detection Agent

---

## 1.3 Device Orchestration Agent

---

## 1.4 Plan Validation 
### 1.4.1 Naive Sensor Activation (Baseline)

- Objective: continuous corridor monitoring by keeping all sensing devices and services active at all times, without any prioritization, sequencing, or contextual awareness. This baseline serves as a reference for evaluating more intelligent activation strategies.
- Assumptions: Linear corridor deployment; each device has a motion sensor and ESP32 camera; fixed local coverage; no prediction/optimization.
- Algorithm:
  - All devices in the corridor are activated simultaneously.
  - Motion sensors continuously monitor their respective areas.
  - When motion is detected by any device, its ESP32 camera immediately streams video.
  - Devices and services remain active indefinitely, regardless of activity level.

Pseudocode

```text
INPUT:
- D = {d1, d2, ..., dn}  // all corridor devices

INITIALIZATION:
  FOR each device di in D:
      activate(di)
      enable_motion_sensor(di)
      enable_camera(di)

LOOP:
  WHILE system is running:
      FOR each device di in D:
          IF motion_detected(di):
              request_video(di)
```

Limitations:
- Extremely high energy consumption due to permanent activation of all sensors and cameras
- Redundant video streaming, especially in low-activity periods
- No adaptation to patient behavior or environmental context
- Poor scalability as the number of devices increases

### 3.1 Cellulaire Sequential Corridor Activation 

- Objective: Ensure corridor monitoring by activating devices sequentially from the nearest patient room, requesting video only when motion is detected.
- Assumptions: Linear corridor deployment; each device has a motion sensor and ESP32 camera; fixed local coverage; no prediction/optimization; 20s per device.
- Algorithm:
  - Identify the device nearest to the patient room.
  - Activate devices one-by-one along the corridor.
  - For each device, keep it active for 20 seconds.
  - During activation: if motion is detected, request video stream from the ESP32 camera; otherwise, do nothing.
  - Deactivate device and move to the next; repeat indefinitely.

Pseudocode:

```text
INPUT:
- D = {d1, d2, ..., dn}  // devices ordered along corridor from nearest room
- T_active = 20 seconds

LOOP:
  FOR each device di in D:
      activate(di)
      start timer T_active

      WHILE timer not expired:
          IF motion_detected(di):
              request_video(di)

      deactivate(di)
```

Limitations:
- High energy consumption; activates devices even during low-probability periods
- No awareness of patient behavior patterns
- Poor scalability; fixed 20s window irrespective of context

### 1.4.2 Probabilistic & Spatially Optimized Activation (Energy-Efficient)

- Objective: Minimize energy by activating only necessary devices using the probability γ of patient egress [1] and spatial coverage (x, y, z, r) [7] using Python library.
- Concepts:
  - Patient movement probability γ ∈ [0, 1] derived from time-of-day, history, medical context.
  - Device model: di = (xi, yi, zi, ri) with sensing radius ri.
  - Coverage optimization: select the minimal subset of devices covering the predicted “risk zone”.
- Risk Zone: R(γ) = R_min + γ × (R_max − R_min)
- Behavior:
  - Higher γ → larger risk radius, more aggressive monitoring; lower γ → smaller radius, fewer devices.

Pseudocode:

```text
INPUT:
- D = {d1, d2, ..., dn}  // all devices
- Patient room position P(xp, yp, zp)
- γ in [0,1]
- T_base = base activation time
- R_min, R_max

// Step 1: Compute risk zone
R = R_min + γ * (R_max - R_min)
RiskZone = sphere(center = P, radius = R)

// Step 2: Candidate devices
C = {}
FOR each di in D:
    IF intersects(coverage(di), RiskZone):
        add di to C

// Step 3: Coverage optimization (approximate set/disk cover)
A = minimal_cover(C, RiskZone)

// Step 4: Activation
FOR each di in A:
    activate(di)
    IF motion_detected(di):
        request_video(di)

// Step 5: Dynamic deactivation
wait(T_base * γ)
FOR each di in A:
    deactivate(di)
```

Notes:
- A can be approximated with greedy disk-cover (pick device covering most uncovered area iteratively).
- T_base × γ provides adaptive activation duration (longer when risk is higher).
- Suitable for real-time updates: recompute γ and A on sliding windows.

Further Explanation (Principal Concept):

- Time Optimization (Gamma Distribution): In the base of Poisson distribution inspiration of patient movements in hospital corridors (leaving and returning to rooms) are random and independent events but in total the distribution is possibly calculated and predicted thanks to probabilistic distribution. However, Poisson models **event counts** (\(N(t)\): number of movements in time interval \(t\)), not **event timing**, it assumes a constant average movement rate \(\lambda\), which totally unsuitable for **real-time sensor activation** (for example, patient motion detection in 8 AM equal to 9PM). In a Poisson process, inter-event time follows an **exponential distribution**. However, exponential distributions are memoryless, too simplistic for human behavior. To better model patient behavior, we use a **Gamma distribution** for the waiting time \(T\) until patient exits the room, meaning motion occurs \(T \sim \text{Gamma}(k, \theta)\), Where \(k\) (shape) is the regularity of behavior and \(\theta\) (scale) is the average waiting duration. \[f_T(t) = \frac{1}{\Gamma(k)\theta^k} t^{k-1} e^{-t/\theta}, \quad t \ge 0\]. The motion probability increases over time and is used to decide **when and how many devices to activate**. \[\gamma(t) = P(T \le t) = F(t)\]

- Space Optimization (Heuristic algorithm): In the context of spatial 3-D space coverage motion device for activity maximization under Smart Cities environment[2], heuristic algorithms have demonstrated the ability to maximize coverage while adhering to resource constraints, such as budget limits. Translating this principle to our motion-sensing and camera-based monitoring system, the “budget” corresponds to energy consumption, which must be minimized while ensuring adequate coverage of potential patient movements. By leveraging camera coverage and strategic placement, we can implement a collaboration-based local search algorithm, which combines local search optimization with coordinated allocation among multiple devices. This approach allows the system to dynamically select the minimal subset of devices that collectively cover the predicted “risk zone” of patient activity. Consequently, the algorithm reduces redundant activations, ensures all critical areas are monitored, and optimizes energy usage by activating only those devices that are necessary at a given moment, thereby balancing coverage effectiveness and energy efficiency. 

---

## 1.5 Network Auto-Configuration Agent

---

## 1.6 Deployment Monitoring Agent

---

## 2. References

[1] Python Gamma Probabilistic Algorithm Library: https://pythonguides.com/python-scipy-gamma/

[2] Camera Placement in Smart Cities for Maximizing Weighted Coverage With Budget Limit. IEEE Sensors Journal. Available: https://ieeexplore.ieee.org/abstract/document/7968252

[3] Hidden Markov Model-Based Fall Detection With Motion Sensor Orientation Calibration: A Case for Real-Life Home Monitoring. IEEE Journal of Biomedical and Health Informatics. Available: https://ieeexplore.ieee.org/abstract/document/8171718

[4] Orientation Optimization for Full-View Coverage Using Rotatable Camera Sensors. IEEE Internet of Things Journal. Available: https://ieeexplore.ieee.org/abstract/document/8824113

[5] Gamma-modulated Wavelet model for Internet of Things traffic. 2017 IEEE International Conference on Communications (ICC). Available: https://ieeexplore.ieee.org/abstract/document/7996506

[6] Camera Planning for Physical Safety of Outdoor Electronic Devices: Perspective and Analysis. IEEE/CAA Journal of Automatica Sinica. Available: https://ieeexplore.ieee.org/abstract/document/10916675

[7] Meta-heuristic ALgorithms in Python: https://mealpy.readthedocs.io/en/latest/pages/general/introduction.html
