"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Standalone ECU Calibration & Combustion Analytics Dashboard                 ║
║  RV College of Engineering - Experimental Study                              ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  Platform: Suzuki GSXR600 | Surrogate: Iso-octane (C8H18)                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECU Telemetry & Combustion Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ENGINE CONSTANTS (From Poster) ──────────────────────────────────────────
# Iso-octane (C8H18) properties
MW_FUEL = 114.23       # g/mol
MW_CO2 = 44.01         # g/mol
MW_H2O = 18.015        # g/mol
DENSITY_FUEL = 0.745   # g/cc
INJECTOR_FLOW = 240.0  # cc/min at 3 bar

# ── CSS THEME (Adapted from Microgrid Project) ────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

html,body,[class*="css"]{ font-family:'Exo 2',sans-serif; }

.stApp {
    background: radial-gradient(ellipse at 50% 50%, rgba(200,50,50,0.05) 0%, #020912 100%);
    color:#e0e0e0!important;
}

h1,h2,h3{ font-family:'Rajdhani',sans-serif!important; letter-spacing:0.04em; color:#ff3333; }

[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#120202 0%,#0a0101 100%)!important;
    border-right:1px solid rgba(255,50,50,0.2)!important;
}

[data-testid="metric-container"]{
    background:linear-gradient(145deg,rgba(255,50,50,0.07),rgba(200,50,50,0.02));
    border:1px solid rgba(255,50,50,0.22); border-radius:8px;
    padding:14px 16px; box-shadow:0 0 10px rgba(255,50,50,0.05);
}

[data-testid="stMetricLabel"] p{
    color:#ff6666!important; font-size:0.75rem!important;
    letter-spacing:0.15em; text-transform:uppercase;
    font-family:'Share Tech Mono',monospace!important;
}

[data-testid="stMetricValue"]{
    font-family:'Rajdhani',sans-serif!important;
    color:#ffffff!important; font-size:1.8rem!important; font-weight:700!important;
    text-shadow:0 0 12px rgba(255,50,50,0.5);
}

.sec-hdr{
    font-family:'Rajdhani',sans-serif!important; font-size:0.9rem!important;
    font-weight:700; letter-spacing:0.2em; color:#ff4444!important;
    text-transform:uppercase; border-bottom:1px solid rgba(255,50,50,0.3);
    padding-bottom:5px; margin:20px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ── MATHEMATICAL ENGINE ───────────────────────────────────────────────────────
class EngineModel:
    def __init__(self):
        self.tps = 5.0
        self.rpm = 1500
        self.target_lambda = 1.00
        self.current_lambda = 0.98
        self.base_pw = 1.6  # ms
        self.ign_adv = 10.0 # BTDC
        
    def calculate_trim(self):
        """Lambda correction factor (CF = L_current / L_target)"""
        cf = self.current_lambda / self.target_lambda
        pw_new = self.base_pw * cf
        trim_pct = ((pw_new - self.base_pw) / self.base_pw) * 100
        return cf, pw_new, trim_pct

    def calculate_combustion_outputs(self, actual_pw):
        """Quantify fuel delivery and emissions per injection event"""
        # Convert PW (ms) to flow based on 240cc/min injector
        # 240 cc/min = 4 cc/sec = 0.004 cc/ms
        flow_vol_cc = actual_pw * 0.004
        mass_fuel_mg = flow_vol_cc * DENSITY_FUEL * 1000
        
        # Stoichiometry: 1 mole C8H18 yields 8 moles CO2 and 9 moles H2O
        moles_fuel = (mass_fuel_mg / 1000) / MW_FUEL
        
        moles_co2 = moles_fuel * 8
        mass_co2_mg = moles_co2 * MW_CO2 * 1000
        
        moles_h2o = moles_fuel * 9
        mass_h2o_mg = moles_h2o * MW_H2O * 1000
        
        return mass_fuel_mg, mass_co2_mg, mass_h2o_mg

# ── PLOTLY DARK THEME HELPER ──────────────────────────────────────────────────
def _dk(fig, h=300, title=""):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,2,2,0.6)",
        font=dict(color="#cccccc", family="Exo 2"), height=h,
        margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=title, font=dict(color="#ff4444", size=14, family="Rajdhani")),
        xaxis=dict(gridcolor="rgba(255,50,50,0.1)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,50,50,0.1)", zeroline=False)
    )
    return fig

# ── MAIN APP INITIALIZATION ───────────────────────────────────────────────────
inject_css()
if 'engine' not in st.session_state:
    st.session_state.engine = EngineModel()

eng = st.session_state.engine

# ── SIDEBAR CONTROLS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ ECU OVERRIDE PANEL")
    
    op_mode = st.selectbox("Operating Condition", 
                           ["Idle (TPS=5%)", "Part Throttle (30%)", "Mid Throttle (60%)", "WOT (100%)"])
    
    # Auto-set baselines based on condition (replicating poster data)
    if "Idle" in op_mode:
        eng.tps, eng.rpm, eng.base_pw = 5.0, 1500, 1.7
    elif "Part" in op_mode:
        eng.tps, eng.rpm, eng.base_pw = 30.0, 4500, 3.2
    elif "Mid" in op_mode:
        eng.tps, eng.rpm, eng.base_pw = 60.0, 8000, 5.5
    else:
        eng.tps, eng.rpm, eng.base_pw = 100.0, 12500, 8.2

    st.markdown('<p class="sec-hdr">Target Variables</p>', unsafe_allow_html=True)
    eng.target_lambda = st.slider("Target AFR (Lambda λ)", 0.85, 1.15, 1.00, 0.01)
    eng.ign_adv = st.slider("Ignition Advance (°BTDC)", 5.0, 40.0, 25.0, 0.5)
    
    st.markdown('<p class="sec-hdr">Sensor Feedback</p>', unsafe_allow_html=True)
    eng.current_lambda = st.slider("Wideband O2 Sensor (λ)", 0.70, 1.30, eng.target_lambda + np.random.uniform(-0.05, 0.05), 0.01)

# ── CALCULATIONS ──────────────────────────────────────────────────────────────
cf, pw_new, trim_pct = eng.calculate_trim()
mass_fuel, mass_co2, mass_h2o = eng.calculate_combustion_outputs(pw_new)

# ── DASHBOARD HEADER ──────────────────────────────────────────────────────────
st.markdown("""
<h1 style="text-align:center;">Standalone ECU: AFR & Ignition Timing Analytics</h1>
<p style="text-align:center;font-family:'Share Tech Mono';color:#aaaaaa;">
SUZUKI GSXR600 PLATFORM | ISO-OCTANE SURROGATE | CLOSED-LOOP LAMBDA CORRECTION
</p>
<hr style="border-color:rgba(255,50,50,0.3);">
""", unsafe_allow_html=True)

# ── TOP METRICS ROW ───────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("RPM", f"{eng.rpm}")
m2.metric("TPS", f"{eng.tps}%")
m3.metric("Ignition Adv", f"{eng.ign_adv}° BTDC")
m4.metric("Target Lambda", f"{eng.target_lambda:.2f}")
m5.metric("Actual Lambda", f"{eng.current_lambda:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Fuel Trim (%)", f"{trim_pct:+.2f}%")
k2.metric("Corrected Pulse Width", f"{pw_new:.3f} ms")
k3.metric("Fuel Mass / Inj", f"{mass_fuel:.1f} mg")
k4.metric("CO₂ Mass / Inj", f"{mass_co2:.1f} mg")

# ── TELEMETRY & MAPPING VISUALIZATIONS ────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📉 Live Telemetry (MoTeC Style)", "🗺️ Fuel Map Surface", "🔥 Combustion Chemistry"])

with tab1:
    st.markdown('<p class="sec-hdr">Simulated Datalogger Traces</p>', unsafe_allow_html=True)
    
    # Generate fake time-series data mirroring the red/blue/green lines in MoTeC
    time_arr = np.linspace(0, 10, 100)
    lam_trace = np.full_like(time_arr, eng.current_lambda) + np.random.normal(0, 0.01, 100)
    rpm_trace = np.full_like(time_arr, eng.rpm) + np.random.normal(0, 50, 100)
    pw_trace = np.full_like(time_arr, pw_new) + np.random.normal(0, 0.05, 100)

    fig_tel = go.Figure()
    fig_tel.add_trace(go.Scatter(x=time_arr, y=lam_trace, name="Lambda 1", line=dict(color="#ff3333", width=2)))
    fig_tel.add_trace(go.Scatter(x=time_arr, y=rpm_trace/10000, name="Engine RPM (x10k)", line=dict(color="#3366ff", width=2)))
    fig_tel.add_trace(go.Scatter(x=time_arr, y=pw_trace, name="Fuel Actual PW (ms)", line=dict(color="#33ff99", width=2)))
    
    fig_tel.update_layout(yaxis_title="Telemetry Values", xaxis_title="Time (s)", hovermode="x unified")
    st.plotly_chart(_dk(fig_tel, 400, "Log Data: Lambda, RPM, and Pulse Width"), use_container_width=True)

with tab2:
    st.markdown('<p class="sec-hdr">Base Fuel Pulse Width Map (VE Representation)</p>', unsafe_allow_html=True)
    
    # Create a 3D surface array approximating a high-revving bike fuel map
    rpms = np.linspace(1000, 14000, 14)
    tpss = np.linspace(0, 100, 11)
    R, T = np.meshgrid(rpms, tpss)
    # Simple mathematical curve to simulate volumetric efficiency/pulse width
    Z = 1.5 + (R/3000) * (T/50)**0.8 - (R/14000)**2
    
    fig_map = go.Figure(data=[go.Surface(z=Z, x=rpms, y=tpss, colorscale='Reds')])
    fig_map.update_layout(
        scene=dict(xaxis_title='RPM', yaxis_title='TPS (%)', zaxis_title='Base PW (ms)',
                   xaxis=dict(gridcolor="rgba(255,50,50,0.2)"),
                   yaxis=dict(gridcolor="rgba(255,50,50,0.2)"),
                   zaxis=dict(gridcolor="rgba(255,50,50,0.2)")),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fff"),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.markdown('<p class="sec-hdr">Stoichiometric Outputs per Injection</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### Combustion Reaction")
        st.latex(r"C_8H_{18} + 12.5O_2 \rightarrow 8CO_2 + 9H_2O")
        st.info(f"**Operating State:** At {eng.tps}% TPS, fuel mass scales to **{mass_fuel:.2f} mg/injection**.")
        
    with c2:
        # Bar chart showing mass outputs
        fig_bar = go.Figure(data=[
            go.Bar(name='Fuel (C8H18)', x=['Reactants/Products'], y=[mass_fuel], marker_color='#ffd700'),
            go.Bar(name='CO2', x=['Reactants/Products'], y=[mass_co2], marker_color='#ff3333'),
            go.Bar(name='H2O', x=['Reactants/Products'], y=[mass_h2o], marker_color='#3366ff')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Mass (mg)")
        st.plotly_chart(_dk(fig_bar, 300, "Mass Balance per Cycle"), use_container_width=True)