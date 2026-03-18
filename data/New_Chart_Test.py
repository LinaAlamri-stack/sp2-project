import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Caffeine & Sleep Insights", layout="wide", initial_sidebar_state="collapsed")

# 2. Advanced Custom CSS for the "Modern/Neon" Dashboard look
st.markdown("""
    <style>
    /* Main Background - Deep Dark Navy */
    .main { background-color: #060914; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    
    /* Headings and Subheadings */
    h1 { color: #ffffff !important; font-weight: 700; }
    .stSubheader { color: #ffffff !important; font-weight: 600; }
    
    /* Custom Styling for Statistic Cards */
    .metric-card {
        background-color: #0d1225;
        border: 1px solid #1d2645;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,255,255,0.05);
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 38px;
        font-weight: bold;
        margin-top: 5px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Chart Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart) {
        background-color: #0d1225;
        border-radius: 15px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Dynamic Data Loading
@st.cache_data(ttl=10) # Auto-refresh every 10 seconds for new survey entries
def load_data():
    try:
        return pd.read_csv("data/survey_data.csv")
    except:
        return pd.read_csv("survey_data.csv")

df = load_data()

# 4. Dashboard Header
st.title("☕ Caffeine & Sleep Analytics")
st.markdown("Real-time monitoring of user habits and health correlations.")
st.markdown("---")

# 5. LIVE PARTICIPANT METRICS (English KPIs)
st.subheader("Live Participant Metrics")
col_a, col_b, col_c = st.columns(3)

if '3. Gender' in df.columns:
    total_users = len(df)
    males = len(df[df['3. Gender'] == 'Male'])
    females = len(df[df['3. Gender'] == 'Female'])

    with col_a:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Participants</div><div class="metric-value" style="color:#33CCFF;">{total_users}</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Male Participants</div><div class="metric-value" style="color:#FFFF66;">{males}</div></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Female Participants</div><div class="metric-value" style="color:#FF66FF;">{females}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. INTERACTIVE CHARTS (Row 1)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution")
    fig_gender = px.pie(df, names='3. Gender', hole=0.6, color_discrete_sequence=['#33CCFF', '#FFFF66'])
    fig_gender.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=10, b=10))
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Daily Cups Consumption")
    if '4. Number of cups per day' in df.columns:
        fig_cups = px.histogram(df, x='4. Number of cups per day', color='3. Gender', barmode='group', color_discrete_sequence=['#33CCFF', '#CC33FF'])
        fig_cups.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', xaxis_title="Cups Per Day", yaxis_title="Count")
        st.plotly_chart(fig_cups, use_container_width=True)

st.markdown("---")

# 7. INTERACTIVE CHARTS (Row 2)
col3, col4 = st.columns(2)

with col3:
    st.subheader("Intake Timing")
    if '6. Timing of last cup' in df.columns:
        fig_timing = px.bar(df, x='6. Timing of last cup', color_discrete_sequence=['#FF66FF'])
        fig_timing.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', xaxis_title="Time of Day", yaxis_title="Users")
        st.plotly_chart(fig_timing, use_container_width=True)

with col4:
    st.subheader("Sleep Quality Score")
    if '12. Sleep Quality' in df.columns:
        fig_sleep = px.histogram(df, x='12. Sleep Quality', color_discrete_sequence=['#33CCFF'])
        fig_sleep.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', xaxis_title="Quality Level", yaxis_title="Count")
        st.plotly_chart(fig_sleep, use_container_width=True)

# Auto-Refresh Hint
st.info("💡 Data refreshes automatically every 10 seconds as new users submit the survey.")
