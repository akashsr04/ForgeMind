# ForgeMind: Data Provenance, Synthesis & Digital Twin Simulation

## 1. Synthetic Data Generation Strategy

To ensure zero dependencies on private industrial datasets or paid APIs, ForgeMind provides a deterministic, reproducible synthetic data generation pipeline.

### Seeded Plant Topology
The demo manufacturing plant comprises 7 interconnected assets:
1. **Raw Material Feeder F-01** (Feeder, Capacity: 350 kg/h, Feeds Conveyor)
2. **Drive Motor M-101** (22 kW Induction Motor, Drives Conveyor, Cooled by Pump)
3. **Main Infeed Conveyor C-101** (Conveyor, Feeds CNC Station)
4. **Coolant Circulation Pump P-201** (Fluid Pump, Cooled loops for Motor and CNC)
5. **Precision CNC Station CNC-301** (5-Axis Machining Center, Bottleneck 300 units/h)
6. **Optical Quality Inspection INS-401** (Vision QA, Feeds Packaging)
7. **Robotic Packaging Cell PKG-501** (Packaging Delta Robot)

### Sensor Baselines & Anomaly Profiles
- **Drive Motor M-101:**
  - `vibration` (mm/s): Baseline $2.1 \pm 0.15$, Warning Threshold $4.5$, Severe Shutdown $7.1$.
  - `temperature` (°C): Baseline $62.0 \pm 0.5$, Warning Threshold $80.0$, Trip Limit $95.0$.
  - `power_draw` (kW): Baseline $15.2 \pm 0.2$, Surges to $19.0$ during mechanical drag.
- **Coolant Pump P-201:**
  - `flow_rate` (L/min): Baseline $48.0 \pm 0.8$, Cavitation alert below $30.0$.
  - `pressure` (bar): Baseline $4.2 \pm 0.08$.

---

## 2. Discrete-Event Digital Twin Simulation Engine

### Capacity and Throughput Propagation
The factory operates as a sequential production line with auxiliary dependencies:
$$\text{Throughput} = \min_{a \in \text{Critical Path}} \left( C_a \cdot \eta_a \right)$$

Where:
- $C_a$ is the nominal design capacity of asset $a$.
- $\eta_a \in [0.0, 1.0]$ is the effective capacity factor.
- Motor drives conveyor: $\eta_{\text{conveyor}} \le \eta_{\text{motor}}$.
- Coolant starvation: if $\eta_{\text{pump}} < 0.3$, thermal interlock trips CNC spindle ($\eta_{\text{cnc}} = 0$).

### Intervention Scenarios
1. **Outage:** Target asset capacity set to $0.0$.
2. **Derating:** Operating speed/load reduced to factor $\alpha \in [0.1, 0.9]$.
3. **Inspection:** Brief 20-minute planned stoppage with ultrasonic probe placement.
4. **Repair:** Planned overhaul restoring asset to $\eta = 1.0$ with parts cost.

### Financial and Downtime Metrics
- **Factory Downtime Valuation:** $\$1,500$ per hour of unproduced baseline capacity.
- **Cost Calculation:**
$$\text{Total Cost} = \text{Direct Parts/Labor Cost} + (\Delta \text{Downtime Hours} \times \$1500/\text{hr})$$

---

## 3. Multi-Criteria Action Decision Scoring

Candidate actions are scored and ranked transparently:
$$\text{Score} = w_{\text{risk}} \cdot \Delta R - w_{\text{downtime}} \cdot D - w_{\text{cost}} \cdot C - w_{\text{unc}} \cdot U$$

- $\Delta R$: Proportional reduction in catastrophic failure risk $[0, 1]$.
- $D$: Estimated production downtime in minutes.
- $C$: Direct financial cost in dollars.
- $U$: Uncertainty penalty based on evidence confidence level (Low: $0.2$, Medium: $0.5$, High: $1.0$).
- Weights default to $w_{\text{risk}}=100.0, w_{\text{downtime}}=0.5, w_{\text{cost}}=0.1, w_{\text{unc}}=20.0$.
