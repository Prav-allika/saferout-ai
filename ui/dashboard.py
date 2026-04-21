"""
SafeRoute AI - Interactive Dashboard
Real-time vehicle monitoring with multi-agent system
"""

import streamlit as st
import plotly.graph_objects as go
from collections import deque
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.sensors import Vehicle
from agents.orchestrator import Orchestrator

# ── Color Palette ──────────────────────────────────────────────────────────────
C_PINK = "#FE9EC7"   # primary accent  — headers, borders, highlights
C_YELL = "#F9F6C4"   # sidebar background (light yellow)
C_LBLU = "#89D4FF"   # main background  (light blue from palette)
C_BLUE = "#44ACFF"   # active accent    — chart lines, reset button
C_BG   = "#89D4FF"   # main background  (light blue)
C_SURF = "#FFFFFF"   # surface / card   (white cards on blue bg)
C_SIDE = "#F9F6C4"   # sidebar          (light yellow)
C_BORD = "#B8D4E8"   # subtle borders   (muted blue-tint)
C_TEXT = "#1A1A1A"   # primary text
C_MUTE = "#555555"   # muted / label text
C_GREN = "#52C41A"   # START button green
C_REDD = "#FF4D4F"   # STOP button red
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SafeRoute AI",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Base: light-blue main area ── */
.stApp {{ background-color: {C_BG}; color: {C_TEXT}; }}
.block-container {{
    background-color: {C_BG};
    color: {C_TEXT};
    padding-top: 2.5rem;   /* prevents title clipping */
}}

/* ── Sidebar: light yellow ── */
[data-testid="stSidebar"] {{
    background-color: {C_SIDE};
    border-right: 2px solid {C_PINK};
}}
/* All sidebar text → dark so it's readable on light yellow */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li {{
    color: {C_TEXT} !important;
}}

/* ── Headers ── */
h1, h2, h3 {{ color: {C_PINK} !important; }}

/* ── Metric cards (main area only) ── */
.block-container [data-testid="stMetric"] {{
    background-color: {C_SURF};
    border-radius: 8px;
    padding: 14px 16px;
    border-left: 3px solid {C_PINK};
}}
[data-testid="stMetricValue"] {{ color: {C_TEXT} !important; font-size: 1.6rem !important; }}
[data-testid="stMetricLabel"] {{ color: {C_MUTE} !important; font-size: 0.8rem !important; letter-spacing: 0.4px; }}
/* Sidebar metric cards on light yellow */
[data-testid="stSidebar"] [data-testid="stMetric"] {{
    background-color: #FFFFFF;
    border-radius: 6px;
    border-left: 3px solid {C_PINK};
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{ color: {C_TEXT} !important; }}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{ color: {C_MUTE} !important; }}

/* ── START button (1st column in sidebar controls) ── */
[data-testid="stSidebar"] [data-testid="column"]:nth-child(1) .stButton > button {{
    background-color: {C_GREN};
    color: #FFFFFF;
    border-color: {C_GREN};
    font-weight: 700;
    letter-spacing: 0.8px;
}}
[data-testid="stSidebar"] [data-testid="column"]:nth-child(1) .stButton > button:hover {{
    background-color: #389E0D;
    border-color: #389E0D;
}}

/* ── STOP button (2nd column in sidebar controls) ── */
[data-testid="stSidebar"] [data-testid="column"]:nth-child(2) .stButton > button {{
    background-color: {C_REDD};
    color: #FFFFFF;
    border-color: {C_REDD};
    font-weight: 700;
    letter-spacing: 0.8px;
}}
[data-testid="stSidebar"] [data-testid="column"]:nth-child(2) .stButton > button:hover {{
    background-color: #CF1322;
    border-color: #CF1322;
}}

/* ── RESET and main-area buttons ── */
.stButton > button {{
    background-color: {C_SURF};
    color: {C_TEXT};
    border: 1px solid {C_BLUE};
    border-radius: 6px;
    font-weight: 600;
    letter-spacing: 0.6px;
    transition: all 0.15s ease;
}}
.stButton > button:hover {{
    background-color: {C_BLUE};
    color: #FFFFFF;
    border-color: {C_BLUE};
}}

/* ── Input fields & selects ── */
input, textarea {{
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid {C_BORD} !important;
    border-radius: 6px !important;
}}
input::placeholder, textarea::placeholder {{ color: #000000 !important; opacity: 0.6; }}
[data-testid="stSelectbox"] > div > div {{
    background-color: #FFFFFF;
    color: #000000;
    border-color: {C_BORD};
}}

/* ── Divider ── */
hr {{ border-color: {C_BORD} !important; }}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background-color: {C_SURF};
    border: 1px solid {C_BORD};
    border-radius: 8px;
}}
[data-testid="stExpander"] summary {{
    color: {C_PINK} !important;
    font-weight: 600;
}}

/* ── Alert boxes (readable on light-blue bg) ── */
[data-testid="stAlertInfo"]    {{ background-color: #DDEFFF; border-left: 4px solid {C_BLUE}; color: #1A1A1A; }}
[data-testid="stAlertWarning"] {{ background-color: #FFFBDE; border-left: 4px solid #B8960C; color: #1A1A1A; }}
[data-testid="stAlertError"]   {{ background-color: #FFE8F2; border-left: 4px solid {C_PINK}; color: #1A1A1A; }}
[data-testid="stAlertSuccess"] {{ background-color: #F0FFE8; border-left: 4px solid {C_GREN}; color: #1A1A1A; }}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {{ background-color: {C_PINK}; }}

/* ── Main header ── */
.main-header {{
    font-size: 3rem;
    font-weight: 800;
    color: {C_PINK};
    text-align: center;
    letter-spacing: 2px;
    margin-top: 1rem;
    margin-bottom: 0.4rem;
    padding-top: 0.5rem;
    line-height: 1.4;
    overflow: visible;
    white-space: nowrap;
}}
.main-sub {{
    text-align: center;
    font-size: 1rem;
    color: {C_MUTE};
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}}

/* ── Feature cards ── */
.feat-card {{
    background-color: {C_SURF};
    padding: 1.2rem 1rem;
    border-radius: 8px;
    height: 100%;
}}
.feat-card b {{ font-size: 0.95rem; letter-spacing: 0.3px; }}
.feat-card p  {{ color: {C_MUTE}; font-size: 0.85rem; margin: 0.2rem 0; }}
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────────
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator    = Orchestrator()
    st.session_state.vehicle         = None
    st.session_state.sensor_history  = deque(maxlen=50)
    st.session_state.alert_history   = []
    st.session_state.risk_counts     = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    st.session_state.is_running      = False
    st.session_state.step_count      = 0
    st.session_state.last_sensor_data = None   # snapshot saved on STOP
    st.session_state.last_decisions   = None   # snapshot saved on STOP

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">◆  SafeRoute AI</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Multi-Agent Vehicle Safety Monitoring System</div>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h2 style='color:{C_PINK}; font-size:1.1rem; letter-spacing:1px;'>≡  CONTROL PANEL</h2>", unsafe_allow_html=True)

    st.markdown(f"<p style='color:{C_TEXT}; font-weight:600; margin-bottom:4px;'>◉  Vehicle Setup</p>", unsafe_allow_html=True)
    vehicle_id = st.text_input("Vehicle ID", value="TN-09-AB-1234", label_visibility="collapsed")
    simulation_mode = st.selectbox(
        "Simulation Mode",
        ["normal", "tire_failure", "engine_overheat"],
        help="Choose what to simulate",
    )

    st.markdown(f"<p style='color:{C_TEXT}; font-weight:600; margin:12px 0 4px;'>◉  Route Configuration</p>", unsafe_allow_html=True)
    road_name = st.selectbox("Road", ["NH-44", "NH-163", "SH-18", "ORR"], help="Select the road")
    time_of_day = st.selectbox("Time of Day", ["day", "night", "dawn", "dusk"])

    st.markdown(f"<p style='color:{C_TEXT}; font-weight:600; margin:12px 0 4px;'>◉  Controls</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("START", use_container_width=True):
            st.session_state.vehicle        = Vehicle(vehicle_id, simulation_mode)
            st.session_state.is_running     = True
            st.session_state.sensor_history = deque(maxlen=50)
            st.session_state.alert_history  = []
            st.session_state.risk_counts    = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            st.session_state.step_count     = 0
            st.success("Monitoring started!")
    with c2:
        if st.button("STOP", use_container_width=True):
            st.session_state.is_running = False
            st.warning("Monitoring stopped")

    if st.button("RESET", use_container_width=True):
        st.session_state.orchestrator   = Orchestrator()
        st.session_state.vehicle        = None
        st.session_state.sensor_history = deque(maxlen=50)
        st.session_state.alert_history  = []
        st.session_state.risk_counts    = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        st.session_state.is_running     = False
        st.session_state.step_count     = 0
        st.info("System reset")

    st.divider()
    st.markdown(f"<p style='color:{C_TEXT}; font-weight:600; margin-bottom:6px;'>◉  System Stats</p>", unsafe_allow_html=True)
    summary = st.session_state.orchestrator.get_alert_summary()
    st.metric("Total Alerts",    summary.get("total_alerts", 0))
    st.metric("Critical Alerts", summary.get("critical_alerts", 0))
    if "agent_stats" in summary:
        st.metric("ML Predictions", summary["agent_stats"]["tire_predictor"]["predictions_made"])
        st.metric("Emergencies",    summary["agent_stats"]["emergency_responder"]["total_emergencies"])

# ── Main Dashboard ─────────────────────────────────────────────────────────────
if st.session_state.vehicle and st.session_state.is_running:
    sensor_data = st.session_state.vehicle.get_sensor_data()
    st.session_state.sensor_history.append(sensor_data)
    st.session_state.step_count += 1

    route_info = {
        "road_name": road_name,
        "time_of_day": time_of_day,
        "location": {"lat": 17.3850, "lon": 78.4867},
    }

    decisions = st.session_state.orchestrator.analyze_sensor_data(sensor_data, route_info)
    # Track risk level every tick (not just when alerts fire)
    st.session_state.risk_counts[decisions["risk_level"]] += 1
    if decisions["alerts"]:
        st.session_state.alert_history.append({"timestamp": datetime.now(), "decisions": decisions})

    # Save latest snapshot so STOP can show it
    st.session_state.last_sensor_data = sensor_data
    st.session_state.last_decisions   = decisions

    # ── Metric Row ─────────────────────────────────────────────────────────────
    tire   = sensor_data["tires"]["front_left"]
    engine = sensor_data["engine"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sym = "●" if tire["status"] == "OK" else "▲" if tire["status"] == "WARNING" else "■"
        st.metric(f"{sym}  Tire Pressure", f"{tire['pressure_psi']} PSI", delta=tire["status"])
    with c2:
        sym = "●" if tire["temperature_c"] < 45 else "▲" if tire["temperature_c"] < 50 else "■"
        st.metric(f"{sym}  Tire Temperature", f"{tire['temperature_c']} °C")
    with c3:
        sym = "●" if engine["status"] == "OK" else "▲" if engine["status"] == "WARNING" else "■"
        st.metric(f"{sym}  Engine Temp", f"{engine['engine_temp_c']} °C", delta=engine["status"])
    with c4:
        sym = "●" if decisions["risk_level"] == "LOW" else "▲" if decisions["risk_level"] == "MEDIUM" else "■"
        st.metric(f"{sym}  Risk Level", decisions["risk_level"])

    st.divider()

    # ── Live Charts ────────────────────────────────────────────────────────────
    _chart_layout = dict(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color=C_TEXT, size=12),
        xaxis=dict(gridcolor="#E8E8E8", zerolinecolor="#E8E8E8", color=C_MUTE),
        yaxis=dict(gridcolor="#E8E8E8", zerolinecolor="#E8E8E8", color=C_MUTE),
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"<h3 style='color:{C_PINK}; font-size:1rem;'>◈  Tire Pressure Over Time</h3>", unsafe_allow_html=True)
        if len(st.session_state.sensor_history) > 1:
            steps     = list(range(len(st.session_state.sensor_history)))
            pressures = [d["tires"]["front_left"]["pressure_psi"] for d in st.session_state.sensor_history]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=steps, y=pressures, mode="lines+markers", name="Pressure",
                line=dict(color=C_PINK, width=2.5),
                marker=dict(size=6, color=C_PINK),
            ))
            fig.add_hline(y=30, line_dash="dash", line_color=C_BLUE,
                          annotation_text="WARNING", annotation_font_color=C_BLUE)
            fig.add_hline(y=28, line_dash="dash", line_color=C_PINK,
                          annotation_text="CRITICAL", annotation_font_color=C_PINK)
            fig.update_layout(**_chart_layout, showlegend=False,
                              yaxis_title="PSI", xaxis_title="Steps")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Collecting data — need at least 2 readings")

    with c2:
        st.markdown(f"<h3 style='color:{C_PINK}; font-size:1rem;'>◎  Temperature Trends</h3>", unsafe_allow_html=True)
        if len(st.session_state.sensor_history) > 1:
            steps      = list(range(len(st.session_state.sensor_history)))
            tire_temps = [d["tires"]["front_left"]["temperature_c"] for d in st.session_state.sensor_history]
            eng_temps  = [d["engine"]["engine_temp_c"] for d in st.session_state.sensor_history]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=steps, y=tire_temps, mode="lines+markers", name="Tire",
                                     line=dict(color=C_PINK, width=2)))
            fig.add_trace(go.Scatter(x=steps, y=eng_temps,  mode="lines+markers", name="Engine",
                                     line=dict(color=C_BLUE, width=2)))
            fig.update_layout(**_chart_layout, yaxis_title="°C", xaxis_title="Steps",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                          font=dict(color=C_TEXT)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Collecting data...")

    st.divider()

    # ── Distribution Charts ────────────────────────────────────────────────────
    if st.session_state.step_count > 0:
        st.markdown(f"<h3 style='color:{C_PINK};'>◆  Alert Distribution</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        type_counts: dict = {}
        for entry in st.session_state.alert_history:
            for alert in entry["decisions"].get("alerts", []):
                t = alert.get("type", "OTHER")
                type_counts[t] = type_counts.get(t, 0) + 1
        risk_counts = st.session_state.risk_counts

        _dist_layout = dict(
            paper_bgcolor=C_SURF,
            plot_bgcolor=C_SURF,
            font=dict(color=C_TEXT),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
        )

        with c1:
            if type_counts:
                fig = go.Figure(data=[go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.45,
                    marker=dict(colors=[C_PINK, C_BLUE, C_LBLU, C_YELL, "#C8A0D8"],
                                line=dict(color="#FFFFFF", width=2)),
                    textinfo="percent",
                    textposition="auto",          # outside when slice too small
                    automargin=True,              # prevents label clipping
                    textfont=dict(size=12, color="#1A1A1A"),  # always dark — readable on any slice
                )])
                fig.update_layout(**_dist_layout,
                                  title=dict(text="Alert Type Distribution", font=dict(color=C_TEXT)),
                                  legend=dict(font=dict(color=C_TEXT)))
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Grouped bars — each risk level is its own bar so High Risk (pink)
            # is always clearly visible regardless of count
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Low / Safe",  x=["Low / Safe"],  y=[risk_counts["LOW"]],
                marker_color=C_LBLU,
                text=[risk_counts["LOW"]], textposition="outside",
                textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            fig.add_trace(go.Bar(
                name="Medium Risk", x=["Medium Risk"], y=[risk_counts["MEDIUM"]],
                marker_color=C_BLUE,
                text=[risk_counts["MEDIUM"]], textposition="outside",
                textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            fig.add_trace(go.Bar(
                name="High Risk",   x=["High Risk"],   y=[risk_counts["HIGH"]],
                marker_color=C_PINK,
                text=[risk_counts["HIGH"]], textposition="outside",
                textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            _y_max = max(risk_counts["LOW"], risk_counts["MEDIUM"], risk_counts["HIGH"], 1) * 1.3
            _bar_layout = {**_dist_layout, "margin": dict(l=10, r=10, t=60, b=10)}
            fig.update_layout(**_bar_layout, barmode="group",
                              title=dict(text="Risk Level Progress", font=dict(color=C_TEXT)),
                              yaxis=dict(gridcolor="#E8E8E8", color=C_MUTE, title="Count",
                                         range=[0, _y_max]),
                              xaxis=dict(color=C_MUTE),
                              showlegend=False,
                              bargap=0.35)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f"<p style='color:{C_MUTE}; font-size:0.78rem; margin-top:-10px;'>"
                f"■ Counts every monitoring step by risk level — "
                f"High fires when tire &lt; 28 PSI or engine &gt; 110 °C</p>",
                unsafe_allow_html=True,
            )

        st.divider()

    # ── Agent Responses ────────────────────────────────────────────────────────
    if decisions.get("agent_responses"):
        st.markdown(f"<h3 style='color:{C_PINK};'>◐  Agent Analysis</h3>", unsafe_allow_html=True)

        if "route_analyzer" in decisions["agent_responses"]:
            route_data = decisions["agent_responses"]["route_analyzer"]
            with st.expander("▸  Route Analyzer", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Road",    route_data["route"]["road_type"])
                    st.metric("Weather", route_data["weather"]["condition"])
                with c2:
                    st.metric("Route Risk",    f"{route_data['risk_analysis']['risk_score']}/10")
                    st.metric("Risk Category", route_data["risk_analysis"]["risk_category"])
                with c3:
                    st.metric("Visibility",  f"{route_data['weather']['visibility_km']} km")
                    st.metric("Temperature", f"{route_data['weather']['temperature']} °C")
                st.info(route_data["recommendation"])
                if route_data.get("alternatives"):
                    st.write("**Alternative Routes:**")
                    for alt in route_data["alternatives"]["alternatives"]:
                        st.write(f"▸  {alt['road']}  —  Risk {alt['risk_score']}/10  (saves {alt['risk_reduction']} pts)")

        if "tire_predictor" in decisions["agent_responses"]:
            pred = decisions["agent_responses"]["tire_predictor"]
            ml   = pred["ml_prediction"]
            with st.expander("▸  ML Tire Predictor", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Failure Probability", f"{ml['failure_probability'] * 100:.1f}%")
                with c2:
                    st.metric("Will Fail", "YES" if ml["will_fail"] else "NO")
                with c3:
                    if ml["time_to_failure_hours"]:
                        st.metric("Time to Failure", f"~{ml['time_to_failure_hours']:.0f} hrs")
                st.progress(ml["failure_probability"])
                st.warning(f"**Recommendation:**  {ml['recommendation']}")
                st.info(pred["analysis"])

        if "emergency_responder" in decisions["agent_responses"]:
            emg = decisions["agent_responses"]["emergency_responder"]
            with st.expander("▸  Emergency Responder", expanded=True):
                st.error(f"**Emergency ID:**  {emg['emergency_id']}")
                st.error(f"**Type:**  {emg['type']}")
                st.write("**Actions Executed:**")
                for action in emg["actions_taken"]:
                    st.write(f"  ✓  **{action['action']}**  —  {action['target']}")
                    st.write(f"     _{action['message']}_")

    # ── Alerts ─────────────────────────────────────────────────────────────────
    if decisions["alerts"]:
        st.divider()
        st.markdown(f"<h3 style='color:{C_PINK};'>▲  Current Alerts</h3>", unsafe_allow_html=True)
        for alert in decisions["alerts"]:
            sev = alert.get("severity", "INFO")
            if sev == "CRITICAL":
                st.error(f"■  **CRITICAL**  —  {alert['message']}")
            elif sev == "WARNING":
                st.warning(f"▲  **WARNING**  —  {alert['message']}")
            else:
                st.info(f"◆  **INFO**  —  {alert['message']}")

    # ── Actions ────────────────────────────────────────────────────────────────
    if decisions["actions"]:
        st.markdown(f"<h3 style='color:{C_PINK};'>◇  Recommended Actions</h3>", unsafe_allow_html=True)
        for action in decisions["actions"]:
            st.markdown(
                f"<p style='color:{C_TEXT}; margin:4px 0; padding-left:8px; "
                f"border-left:2px solid {C_BLUE};'>▸  {action}</p>",
                unsafe_allow_html=True,
            )

    time.sleep(1)
    st.rerun()

elif (
    not st.session_state.is_running
    and st.session_state.last_sensor_data is not None
    and st.session_state.last_decisions is not None
):
    # ── Stopped — show last recorded snapshot ──────────────────────────────────
    sensor_data = st.session_state.last_sensor_data
    decisions   = st.session_state.last_decisions
    tire   = sensor_data["tires"]["front_left"]
    engine = sensor_data["engine"]

    st.warning("▲  Monitoring stopped  —  showing last recorded snapshot.  Click  **START**  to resume.")

    # Last metric values
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sym = "●" if tire["status"] == "OK" else "▲" if tire["status"] == "WARNING" else "■"
        st.metric(f"{sym}  Tire Pressure", f"{tire['pressure_psi']} PSI", delta=tire["status"])
    with c2:
        sym = "●" if tire["temperature_c"] < 45 else "▲" if tire["temperature_c"] < 50 else "■"
        st.metric(f"{sym}  Tire Temperature", f"{tire['temperature_c']} °C")
    with c3:
        sym = "●" if engine["status"] == "OK" else "▲" if engine["status"] == "WARNING" else "■"
        st.metric(f"{sym}  Engine Temp", f"{engine['engine_temp_c']} °C", delta=engine["status"])
    with c4:
        sym = "●" if decisions["risk_level"] == "LOW" else "▲" if decisions["risk_level"] == "MEDIUM" else "■"
        st.metric(f"{sym}  Risk Level", decisions["risk_level"])

    st.divider()

    # Pressure + temperature history charts (frozen)
    _chart_layout = dict(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(color=C_TEXT, size=12),
        xaxis=dict(gridcolor="#E8E8E8", zerolinecolor="#E8E8E8", color=C_MUTE),
        yaxis=dict(gridcolor="#E8E8E8", zerolinecolor="#E8E8E8", color=C_MUTE),
        margin=dict(l=10, r=10, t=30, b=10), height=300,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<h3 style='color:{C_PINK}; font-size:1rem;'>◈  Tire Pressure History</h3>", unsafe_allow_html=True)
        if len(st.session_state.sensor_history) > 1:
            steps     = list(range(len(st.session_state.sensor_history)))
            pressures = [d["tires"]["front_left"]["pressure_psi"] for d in st.session_state.sensor_history]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=steps, y=pressures, mode="lines+markers", name="Pressure",
                                     line=dict(color=C_PINK, width=2.5), marker=dict(size=6, color=C_PINK)))
            fig.add_hline(y=30, line_dash="dash", line_color=C_BLUE, annotation_text="WARNING", annotation_font_color=C_BLUE)
            fig.add_hline(y=28, line_dash="dash", line_color=C_PINK, annotation_text="CRITICAL", annotation_font_color=C_PINK)
            fig.update_layout(**_chart_layout, showlegend=False, yaxis_title="PSI", xaxis_title="Steps")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(f"<h3 style='color:{C_PINK}; font-size:1rem;'>◎  Temperature History</h3>", unsafe_allow_html=True)
        if len(st.session_state.sensor_history) > 1:
            steps      = list(range(len(st.session_state.sensor_history)))
            tire_temps = [d["tires"]["front_left"]["temperature_c"] for d in st.session_state.sensor_history]
            eng_temps  = [d["engine"]["engine_temp_c"] for d in st.session_state.sensor_history]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=steps, y=tire_temps, mode="lines+markers", name="Tire",  line=dict(color=C_PINK, width=2)))
            fig.add_trace(go.Scatter(x=steps, y=eng_temps,  mode="lines+markers", name="Engine", line=dict(color=C_BLUE, width=2)))
            fig.update_layout(**_chart_layout, yaxis_title="°C", xaxis_title="Steps",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color=C_TEXT)))
            st.plotly_chart(fig, use_container_width=True)

    # Distribution charts (frozen)
    if st.session_state.step_count > 0:
        st.divider()
        st.markdown(f"<h3 style='color:{C_PINK};'>◆  Alert Distribution</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        type_counts: dict = {}
        for entry in st.session_state.alert_history:
            for alert in entry["decisions"].get("alerts", []):
                t = alert.get("type", "OTHER")
                type_counts[t] = type_counts.get(t, 0) + 1
        risk_counts = st.session_state.risk_counts
        _dist_layout = dict(paper_bgcolor=C_SURF, plot_bgcolor=C_SURF, font=dict(color=C_TEXT),
                            height=320, margin=dict(l=10, r=10, t=40, b=10))
        with c1:
            if type_counts:
                fig = go.Figure(data=[go.Pie(
                    labels=list(type_counts.keys()), values=list(type_counts.values()), hole=0.45,
                    marker=dict(colors=[C_PINK, C_BLUE, C_LBLU, C_YELL, "#C8A0D8"],
                                line=dict(color="#FFFFFF", width=2)),
                    textinfo="percent", textposition="auto", automargin=True,
                    textfont=dict(size=12, color="#1A1A1A"),
                )])
                fig.update_layout(**_dist_layout, title=dict(text="Alert Type Distribution", font=dict(color=C_TEXT)),
                                  legend=dict(font=dict(color=C_TEXT)))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Low / Safe",  x=["Low / Safe"],  y=[risk_counts["LOW"]],
                marker_color=C_LBLU, text=[risk_counts["LOW"]],
                textposition="outside", textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            fig.add_trace(go.Bar(
                name="Medium Risk", x=["Medium Risk"], y=[risk_counts["MEDIUM"]],
                marker_color=C_BLUE, text=[risk_counts["MEDIUM"]],
                textposition="outside", textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            fig.add_trace(go.Bar(
                name="High Risk",   x=["High Risk"],   y=[risk_counts["HIGH"]],
                marker_color=C_PINK, text=[risk_counts["HIGH"]],
                textposition="outside", textfont=dict(color=C_TEXT, size=14, family="Arial Black"),
            ))
            _y_max = max(risk_counts["LOW"], risk_counts["MEDIUM"], risk_counts["HIGH"], 1) * 1.3
            _bar_layout = {**_dist_layout, "margin": dict(l=10, r=10, t=60, b=10)}
            fig.update_layout(**_bar_layout, barmode="group",
                              title=dict(text="Risk Level Progress", font=dict(color=C_TEXT)),
                              yaxis=dict(gridcolor="#E8E8E8", color=C_MUTE, title="Count",
                                         range=[0, _y_max]),
                              xaxis=dict(color=C_MUTE),
                              showlegend=False,
                              bargap=0.35)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f"<p style='color:{C_MUTE}; font-size:0.78rem;'>"
                f"■ High Risk (pink) fires on CRITICAL alerts — tire &lt; 28 PSI or engine &gt; 110 °C</p>",
                unsafe_allow_html=True)

    # Last alerts
    if decisions["alerts"]:
        st.divider()
        st.markdown(f"<h3 style='color:{C_PINK};'>▲  Last Alerts</h3>", unsafe_allow_html=True)
        for alert in decisions["alerts"]:
            sev = alert.get("severity", "INFO")
            if sev == "CRITICAL":
                st.error(f"■  **CRITICAL**  —  {alert['message']}")
            elif sev == "WARNING":
                st.warning(f"▲  **WARNING**  —  {alert['message']}")
            else:
                st.info(f"◆  **INFO**  —  {alert['message']}")

else:
    # ── Welcome Screen ─────────────────────────────────────────────────────────
    st.info("Select a simulation mode and click  **START**  in the sidebar to begin monitoring")

    st.markdown(f"<h3 style='color:{C_PINK};'>◆  Features</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="feat-card" style="border-left:3px solid {C_PINK};">
            <b style="color:{C_PINK};">◈  Real-Time Monitoring</b>
            <p>Tire pressure &amp; temperature</p>
            <p>Engine diagnostics</p>
            <p>Live data visualization</p>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="feat-card" style="border-left:3px solid {C_BLUE};">
            <b style="color:{C_BLUE};">◐  AI Agents</b>
            <p>ML failure prediction</p>
            <p>Route safety analysis</p>
            <p>Emergency protocols</p>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="feat-card" style="border-left:3px solid {C_LBLU};">
            <b style="color:{C_LBLU};">◎  Advanced Analytics</b>
            <p>Multi-agent coordination</p>
            <p>Risk assessment</p>
            <p>Alert distribution charts</p>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<h3 style='color:{C_PINK};'>◆  Example Scenario</h3>", unsafe_allow_html=True)
    for step in [
        "Select  **tire_failure**  mode and click  **START**",
        "Watch tire pressure  **drop gradually**  on the live chart",
        "See the  **ML Predictor**  calculate failure probability in real-time",
        "When pressure hits  **WARNING**  level — agents activate",
        "At  **CRITICAL**  level — Emergency protocol executes automatically",
    ]:
        st.markdown(
            f"<p style='color:{C_TEXT}; margin:6px 0; padding-left:10px; "
            f"border-left:2px solid {C_PINK};'>▸  {step}</p>",
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#555555; font-size:0.8rem; letter-spacing:0.5px;'>"
    "SafeRoute AI  —  Multi-Agent Vehicle Safety System  |  Built with Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
