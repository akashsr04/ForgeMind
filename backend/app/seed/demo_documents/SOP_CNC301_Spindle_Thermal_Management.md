# SOP-CNC301: High-Speed Spindle Thermal and Vibration Protocols

**Document ID:** DOC-CNC301-2024  
**Asset Type:** cnc  
**Equipment:** Precision CNC Station CNC-301 (Apex APX-5AX-300)  
**Document Type:** manual  
**Version:** 3.0  
**Source:** CNC Machining Cell Operating Manual  

---

## 1. Machine Architecture
- 5-axis synchronous machining center with 12,000 RPM motorized direct-drive spindle.
- Flood coolant required whenever spindle exceeds 4,000 RPM. Coolant supplied by Coolant Pump P-201.

---

## 2. Dependency Risk & Interlocks
- **Upstream Coolant Interlock:** If coolant line pressure drops below 2.5 bar, CNC-301 automatically pauses cutting cycle within 10 seconds to avoid thermal shock and tool breakage.
- **Infeed Starvation:** If Main Infeed Conveyor C-101 stops or derates below 0.6 m/s, CNC-301 enters standby feed-hold, buffering up to 3 parts before complete cycle pause.

---

## 3. Maintenance Procedures
1. **Spindle Runout and Dynamic Balance Test:**
   - Downtime: 30 minutes. Measure TIR (Total Indicator Reading) with dial test indicator.
2. **Flood Coolant Flush and Nozzle Alignment:**
   - Downtime: 15 minutes. Check fluid velocity and clear swarf chips from manifold.
