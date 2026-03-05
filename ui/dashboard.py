"""
SafeRoute AI - Interactive Dashboard
Real-time vehicle monitoring with multi-agent system
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our system
from simulation.sensors import Vehicle
from agents.orchestrator import Orchestrator

# Page config
st.set_page_config(
    page_title="SafeRoute AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF4B4B;
    }
    .alert-critical {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
    }
    .alert-ok {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()
    st.session_state.vehicle = None
    st.session_state.sensor_history = []
    st.session_state.alert_history = []
    st.session_state.is_running = False
    st.session_state.step_count = 0

# Header
st.markdown('<div class="main-header">🚗 SafeRoute AI</div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #666;">Multi-Agent Vehicle Safety Monitoring System</p>',
    unsafe_allow_html=True,
)

st.divider()

# Sidebar - Controls
with st.sidebar:
    st.header("⚙️ Control Panel")

    # Vehicle Configuration
    st.subheader("🚗 Vehicle Setup")
    vehicle_id = st.text_input("Vehicle ID", value="TN-09-AB-1234")

    simulation_mode = st.selectbox(
        "Simulation Mode",
        ["normal", "tire_failure", "engine_overheat"],
        help="Choose what to simulate",
    )

    # Route Configuration
    st.subheader("🛣️ Route Configuration")
    road_name = st.selectbox(
        "Road",
        ["NH-44", "NH-163", "SH-18", "ORR"],
        help="Select the road for route analysis",
    )

    time_of_day = st.selectbox("Time of Day", ["day", "night", "dawn", "dusk"])

    # Start/Stop Controls
    st.subheader("🎮 Controls")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🟢 Start", use_container_width=True):
            st.session_state.vehicle = Vehicle(vehicle_id, simulation_mode)
            st.session_state.is_running = True
            st.session_state.sensor_history = []
            st.session_state.alert_history = []
            st.session_state.step_count = 0
            st.success("Monitoring started!")

    with col2:
        if st.button("🔴 Stop", use_container_width=True):
            st.session_state.is_running = False
            st.warning("Monitoring stopped")

    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.orchestrator = Orchestrator()
        st.session_state.vehicle = None
        st.session_state.sensor_history = []
        st.session_state.alert_history = []
        st.session_state.is_running = False
        st.session_state.step_count = 0
        st.info("System reset")

    # System Info
    st.divider()
    st.subheader("📊 System Stats")

    summary = st.session_state.orchestrator.get_alert_summary()

    st.metric("Total Alerts", summary.get("total_alerts", 0))
    st.metric("Critical Alerts", summary.get("critical_alerts", 0))

    if "agent_stats" in summary:
        st.metric(
            "ML Predictions",
            summary["agent_stats"]["tire_predictor"]["predictions_made"],
        )
        st.metric(
            "Emergencies",
            summary["agent_stats"]["emergency_responder"]["total_emergencies"],
        )

# Main Dashboard
if st.session_state.vehicle and st.session_state.is_running:
    # Get sensor data
    sensor_data = st.session_state.vehicle.get_sensor_data()
    st.session_state.sensor_history.append(sensor_data)
    st.session_state.step_count += 1

    # Keep only last 50 readings
    if len(st.session_state.sensor_history) > 50:
        st.session_state.sensor_history.pop(0)

    # Prepare route info
    route_info = {
        "road_name": road_name,
        "time_of_day": time_of_day,
        "location": {"lat": 17.3850, "lon": 78.4867},
    }

    # Orchestrator analysis
    decisions = st.session_state.orchestrator.analyze_sensor_data(
        sensor_data, route_info
    )

    if decisions["alerts"]:
        st.session_state.alert_history.append(
            {"timestamp": datetime.now(), "decisions": decisions}
        )

    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    tire = sensor_data["tires"]["front_left"]
    engine = sensor_data["engine"]

    with col1:
        pressure_status = (
            "🟢"
            if tire["status"] == "OK"
            else "🟡"
            if tire["status"] == "WARNING"
            else "🔴"
        )
        st.metric(
            f"{pressure_status} Tire Pressure",
            f"{tire['pressure_psi']} PSI",
            delta=f"{tire['status']}",
        )

    with col2:
        temp_status = (
            "🟢"
            if tire["temperature_c"] < 45
            else "🟡"
            if tire["temperature_c"] < 50
            else "🔴"
        )
        st.metric(f"{temp_status} Tire Temperature", f"{tire['temperature_c']}°C")

    with col3:
        engine_status = (
            "🟢"
            if engine["status"] == "OK"
            else "🟡"
            if engine["status"] == "WARNING"
            else "🔴"
        )
        st.metric(
            f"{engine_status} Engine Temp",
            f"{engine['engine_temp_c']}°C",
            delta=f"{engine['status']}",
        )

    with col4:
        risk_color = (
            "🟢"
            if decisions["risk_level"] == "LOW"
            else "🟡"
            if decisions["risk_level"] == "MEDIUM"
            else "🔴"
        )
        st.metric(f"{risk_color} Risk Level", decisions["risk_level"])

    st.divider()

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Tire Pressure Over Time")

        if len(st.session_state.sensor_history) > 1:
            # Create pressure chart
            steps = list(range(len(st.session_state.sensor_history)))
            pressures = [
                data["tires"]["front_left"]["pressure_psi"]
                for data in st.session_state.sensor_history
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=pressures,
                    mode="lines+markers",
                    name="Pressure",
                    line=dict(color="#FF4B4B", width=3),
                    marker=dict(size=8),
                )
            )

            # Add threshold lines
            fig.add_hline(
                y=30,
                line_dash="dash",
                line_color="orange",
                annotation_text="WARNING (30 PSI)",
            )
            fig.add_hline(
                y=28,
                line_dash="dash",
                line_color="red",
                annotation_text="CRITICAL (28 PSI)",
            )

            fig.update_layout(
                xaxis_title="Time Steps",
                yaxis_title="Pressure (PSI)",
                height=300,
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Collecting data... (need at least 2 readings)")

    with col2:
        st.subheader("🌡️ Temperature Trends")

        if len(st.session_state.sensor_history) > 1:
            steps = list(range(len(st.session_state.sensor_history)))
            tire_temps = [
                data["tires"]["front_left"]["temperature_c"]
                for data in st.session_state.sensor_history
            ]
            engine_temps = [
                data["engine"]["engine_temp_c"]
                for data in st.session_state.sensor_history
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=tire_temps,
                    mode="lines+markers",
                    name="Tire Temp",
                    line=dict(color="#FF6B6B", width=2),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=engine_temps,
                    mode="lines+markers",
                    name="Engine Temp",
                    line=dict(color="#4ECDC4", width=2),
                )
            )

            fig.update_layout(
                xaxis_title="Time Steps",
                yaxis_title="Temperature (°C)",
                height=300,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Collecting data...")

    st.divider()

    # Agent Responses
    if decisions.get("agent_responses"):
        st.subheader("🤖 AI Agent Analysis")

        # Route Analyzer
        if "route_analyzer" in decisions["agent_responses"]:
            route_data = decisions["agent_responses"]["route_analyzer"]

            with st.expander("🛣️ Route Analyzer", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Road", route_data["route"]["road_type"])
                    st.metric("Weather", route_data["weather"]["condition"])

                with col2:
                    st.metric(
                        "Route Risk", f"{route_data['risk_analysis']['risk_score']}/10"
                    )
                    st.metric(
                        "Risk Category", route_data["risk_analysis"]["risk_category"]
                    )

                with col3:
                    st.metric(
                        "Visibility", f"{route_data['weather']['visibility_km']} km"
                    )
                    st.metric(
                        "Temperature", f"{route_data['weather']['temperature']}°C"
                    )

                st.info(f"💡 {route_data['recommendation']}")

                if route_data.get("alternatives"):
                    st.write("**Alternative Routes:**")
                    for alt in route_data["alternatives"]["alternatives"]:
                        st.write(
                            f"- {alt['road']}: Risk {alt['risk_score']}/10 (saves {alt['risk_reduction']} points)"
                        )

        # Tire Predictor
        if "tire_predictor" in decisions["agent_responses"]:
            pred = decisions["agent_responses"]["tire_predictor"]
            ml = pred["ml_prediction"]

            with st.expander("🔮 ML Tire Predictor", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Failure Probability", f"{ml['failure_probability'] * 100:.1f}%"
                    )

                with col2:
                    st.metric("Will Fail", "YES" if ml["will_fail"] else "NO")

                with col3:
                    if ml["time_to_failure_hours"]:
                        st.metric(
                            "Time to Failure", f"~{ml['time_to_failure_hours']:.0f} hrs"
                        )

                # Progress bar for probability
                st.progress(ml["failure_probability"])

                st.warning(f"**Recommendation:** {ml['recommendation']}")
                st.info(pred["analysis"])

        # Emergency Responder
        if "emergency_responder" in decisions["agent_responses"]:
            emg = decisions["agent_responses"]["emergency_responder"]

            with st.expander("🚨 Emergency Responder", expanded=True):
                st.error(f"**Emergency ID:** {emg['emergency_id']}")
                st.error(f"**Type:** {emg['type']}")

                st.write("**Actions Executed:**")
                for action in emg["actions_taken"]:
                    st.write(f"✓ **{action['action']}** → {action['target']}")
                    st.write(f"   _{action['message']}_")

    # Alerts
    if decisions["alerts"]:
        st.divider()
        st.subheader("⚠️ Current Alerts")

        for alert in decisions["alerts"]:
            severity = alert.get("severity", "INFO")

            if severity == "CRITICAL":
                st.error(f"🚨 **CRITICAL:** {alert['message']}")
            elif severity == "WARNING":
                st.warning(f"⚠️ **WARNING:** {alert['message']}")
            else:
                st.info(f"ℹ️ **INFO:** {alert['message']}")

    # Actions
    if decisions["actions"]:
        st.subheader("📋 Recommended Actions")
        for action in decisions["actions"]:
            st.write(f"- {action}")

    # Auto-refresh
    time.sleep(1)
    st.rerun()

else:
    # Welcome Screen
    st.info("👈 Click **Start** in the sidebar to begin monitoring")

    st.subheader("🎯 Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🔧 Real-Time Monitoring**
        - Tire pressure & temperature
        - Engine diagnostics
        - Live data visualization
        """)

    with col2:
        st.markdown("""
        **🤖 AI Agents**
        - ML failure prediction
        - Route safety analysis
        - Emergency protocols
        """)

    with col3:
        st.markdown("""
        **📊 Advanced Analytics**
        - Multi-agent coordination
        - Risk assessment
        - Automated responses
        """)

    st.divider()

    st.subheader("📈 Example Scenario")
    st.write("""
    1. **Start** monitoring with tire_failure mode
    2. Watch tire pressure **drop gradually**
    3. See **ML predictor** calculate failure probability
    4. When pressure hits **WARNING** level → Agents activate
    5. At **CRITICAL** level → Emergency protocol executes
    """)

# Footer
st.divider()
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>SafeRoute AI - Multi-Agent Vehicle Safety System | Built with ❤️ using Streamlit</p>
</div>
""",
    unsafe_allow_html=True,
)
