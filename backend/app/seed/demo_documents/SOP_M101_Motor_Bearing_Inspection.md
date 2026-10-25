# SOP-M101: Electric Induction Motor Diagnostics and Maintenance

**Document ID:** DOC-M101-2024  
**Asset Type:** motor  
**Equipment:** Drive Motor M-101 (Vortex Drive Corp VD-22K-IE4)  
**Document Type:** procedure  
**Version:** 2.1  
**Source:** Plant Engineering Standard Operating Procedures  

---

## 1. Overview and Operational Envelope
The M-101 motor is a continuous-duty 22 kW 4-pole three-phase AC induction motor driving Main Infeed Conveyor C-101.
- Nominal full-load current: 41.5 A
- Operating speed: 1780 RPM (29.6 Hz rotational fundamental)
- Drive-end (DE) bearing: SKF 6312 deep groove ball bearing
- Non-drive-end (NDE) bearing: SKF 6210 deep groove ball bearing

---

## 2. Vibration Severity Criteria (ISO 10816-3 Class II)
Continuous vibration monitoring uses high-frequency triaxial accelerometers mounted on the drive-end bearing housing.
- **Normal Zone (A/B):** Overall velocity <= 2.8 mm/s RMS. Machine operates within nominal design envelope.
- **Alert Zone (C):** Overall velocity > 4.5 mm/s RMS. Indicates incipient bearing inner/outer race spalling, misalignment, or lubrication breakdown. Immediate acoustic and thermal inspection required within 24 hours.
- **Action / Shutdown Zone (D):** Overall velocity >= 7.1 mm/s RMS. Severe mechanical danger of bearing seizure, rotor strike, or shaft shear. Immediate controlled shutdown mandated.

---

## 3. Thermal Runaway and Coincident Indicators
Under normal operating conditions, winding temperature remains between 55°C and 72°C.
- If drive-end bearing temperature rises above 80°C concurrently with vibration exceeding 4.5 mm/s, bearing cage or ball fatigue failure is probable (90% historical concordance).
- When thermal runaway occurs due to bearing friction, power draw (kW) typically exhibits intermittent 10-25% surges due to increased rotational torque resistance.

---

## 4. Mitigating Maintenance Actions
When elevated vibration (4.5 - 6.5 mm/s) and heat (>80°C) are detected:
1. **Action A: Visual and Ultrasonic Inspection (Low Downtime)**
   - Estimated downtime: 20 minutes
   - Procedure: Use airborne ultrasound detector (20-40 kHz) to listen for bearing scrubbing/clicking. Check lubricant level and inspect for shaft discoloration.
2. **Action B: Production Load Derating (Zero Immediate Downtime)**
   - Reduce upstream feeder throughput by 30-50% and motor frequency from 60 Hz to 42 Hz.
   - Reduces mechanical shear stress and thermal generation by ~40%, allowing controlled completion of current batch before emergency stoppage.
3. **Action C: Drive-End Bearing Replacement (Planned Maintenance)**
   - Estimated downtime: 90 minutes; Estimated parts cost: $450.
   - Full replacement of SKF 6312 bearing, fresh synthetic polyurea grease pack, and dynamic laser shaft realignment.
4. **Action D: Full Motor Module Swapping**
   - Estimated downtime: 180 minutes; Estimated replacement cost: $4,200.
   - Recommended only if stator insulation resistance test (Megger) indicates breakdown (< 5 Megohms) or rotor shaft scoring is observed.
