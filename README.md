# ECU Calibration & Combustion Analytics Dashboard

> **Experimental Study of Air-Fuel Ratio (AFR) and Ignition Timing on Combustion Characteristics Using Engine Control Unit (ECU)**

A comprehensive dashboard for analyzing combustion characteristics, fuel injection parameters, and engine control unit calibration data from the Suzuki GSXR600 platform.

---

## 📋 Project Overview

This project is an **interactive data analytics and visualization platform** designed to support experimental research on engine combustion optimization. It provides real-time telemetry, Lambda (λ) correction analysis, and combustion characteristic mapping using iso-octane (C₈H₁₈) as a surrogate fuel.

**Key Focus Areas:**
- **Air-Fuel Ratio (AFR) Optimization**: Lambda (λ) correction and fuel trim calculations
- **Ignition Timing Analysis**: BTDC (Before Top Dead Center) advancement studies
- **Combustion Characteristics**: Real-time metrics including power output, emissions, and efficiency
- **ECU Calibration**: Dynamic fuel injection pulse width (PW) tuning and parameter mapping

**Platform:** Suzuki GSXR600 Motorcycle Engine  
**Institution:** RV College of Engineering  
**Fuel Surrogate:** Iso-octane (C₈H₁₈)

---

## 🎯 Features

- **Real-Time Telemetry Dashboard**: Monitor RPM, TPS, Lambda, fuel trim, and ignition advance in real-time
- **Lambda Correction Engine**: Automatic fuel pulse width adjustment based on target vs. actual air-fuel ratios
- **Combustion Analytics**: Calculate fuel mass, emissions (CO₂, H₂O), and combustion efficiency
- **Interactive Visualizations**: Plotly-based charts for trend analysis and parameter correlation
- **Customizable Calibration Maps**: Adjust engine parameters and observe combustion impacts
- **Multi-Scenario Testing**: Compare different AFR and ignition timing configurations

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly |
| **Language** | Python 3.x |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Experimental-Study-of-Air-Fuel-Ratio-AFR-and-Ignition-Timing-on-Combustion-Characteristics-Using-ECU"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install streamlit pandas numpy plotly
   ```

---

## 🚀 Usage

### Running the Dashboard

```bash
streamlit run ecu_dashboard.py
```

The application will open in your default web browser at `http://localhost:8501`

### Dashboard Navigation

1. **Sidebar Controls**:
   - Adjust TPS (Throttle Position Sensor) values
   - Modify RPM settings
   - Set target Lambda values
   - Control ignition advance (BTDC)

2. **Main Display**:
   - Real-time metrics (Lambda CF, fuel trim, combustion outputs)
   - Interactive charts for parameter visualization
   - Scenario comparison tools

---

## 🔧 Key Components

### Engine Model (`EngineModel` class)
- **Lambda Correction**: Calculates correction factor (CF) based on target vs. actual lambda
- **Fuel Trim**: Computes pulse width adjustments for precise AFR control
- **Combustion Outputs**: Quantifies fuel delivery and emissions per injection event

### Engine Constants
| Parameter | Value | Unit |
|-----------|-------|------|
| Fuel Molecular Weight (iso-octane) | 114.23 | g/mol |
| CO₂ Molecular Weight | 44.01 | g/mol |
| H₂O Molecular Weight | 18.015 | g/mol |
| Fuel Density | 0.745 | g/cc |
| Injector Flow Rate | 240.0 | cc/min @ 3 bar |

---

## 📊 Data Analysis Capabilities

### AFR & Lambda Analysis
- **Stoichiometric Ratio**: Target lambda = 1.00
- **Rich/Lean Detection**: Identifies combustion efficiency zones
- **Trim Percentage**: Shows fuel injection correction in percentage

### Combustion Metrics
- **Fuel Mass per Injection**: Calculated from injection pulse width
- **CO₂ Emissions**: Derived from complete combustion analysis
- **H₂O Production**: Quantified based on fuel composition
- **Power Output**: Estimated engine output under current conditions

---

## 📁 Project Structure

```
Experimental-Study-of-Air-Fuel-Ratio-AFR-and-Ignition-Timing-on-Combustion-Characteristics-Using-ECU/
├── README.md                  # This file
├── ecu_dashboard.py          # Main Streamlit application
└── .git/                      # Git version control
```

---

## 🔬 Experimental Parameters

### Variable Parameters
- **Throttle Position (TPS)**: 0-100%
- **Engine Speed (RPM)**: 1000-8000 RPM
- **Target Lambda (λ)**: 0.85-1.10 (Lean to Rich)
- **Ignition Advance (BTDC)**: -5° to 35° Before Top Dead Center

### Measured Outputs
- Current Lambda (λ_actual)
- Fuel Trim Percentage
- Fuel Injection Pulse Width (PW)
- CO₂ and H₂O Production
- Combustion Efficiency

---

## 📝 Notes

- The dashboard uses **iso-octane (C₈H₁₈)** as a surrogate fuel for consistent experimental conditions
- All calculations follow **stoichiometric combustion principles**
- The ECU model simulates a **Suzuki GSXR600** engine platform
- Injector specifications are based on OEM 240cc/min flow rating at 3 bar

---

## 🤝 Contributing

This is a research project from RV College of Engineering. For contributions, modifications, or inquiries, please contact the project team.

---

## 📄 License

[Specify License - e.g., MIT, Research Use Only, etc.]

---

## 👥 Authors & Acknowledgments

- **Research Institution**: RV College of Engineering
- **Project Focus**: Experimental combustion analysis and ECU calibration optimization

---

## 📞 Support & Contact

For questions or technical support regarding this project, please reach out to the development team at RV College of Engineering.

---

**Last Updated**: 2026-07-27
