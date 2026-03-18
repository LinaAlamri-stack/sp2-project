import pandas as pd
import plotly.express as px
import streamlit as st
import time

# 1. Page Configuration (Keep Sidebar Collapsed)
st.set_page_config(page_title="Health Habits Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Advanced Custom CSS for "Modern/Neon" Cards and Styling
st.markdown("""
    <style>
    /* Main Background - Deep Dark Navy */
    .main { background-color: #060914; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    
    /* Headings */
    h1 { color: #ffffff !important; }
    .stSubheader { color: #ffffff !important; font-weight: 600; }
    
    /* Chart and Statistic Card Styling (The "Card" look) */
    [data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart),
    div[data-testid="stMetricValue"] {
        background-color: #0d1225;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,255,255,0.03); /* Soft Neon Glow */
        margin-bottom: 20px;
    }
    
    /* Small Adjustments to Metrics (KPIs) */
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stMetricLabel"] { color: #a0a0a0 !important; font-size: 16px; }
    div[data-testid="stMetricValue"] { color: #33CCFF !important; font-size: 32px; } /* Neon Blue for Total */

    /* Sub-colors for Male/Female in Stats */
    div.male-stat [data-testid="stMetricValue"] { color: #FFFF66 !important; } /* Neon Yellow for Male */
    div.female-stat [data-testid="stMetricValue"] { color: #33CCFF !important; } /* Neon Blue for Female */
    </style>
    """, unsafe_allow_html=True)

# 3. Dynamic Data Loading Function (with Caching & Try/Except)
@st.cache_data(ttl=60) # Caches for 1 minute, forcing re-load if a user submits survey
def load_data():
    try: return pd.read_csv("data/survey_data.csv")
    except: return pd.read_csv("survey_data.csv")

# Initialize and Load
df = load_data()

# 4. Dashboard Title and Subtitle
st.title("User Habits & Health Dashboard")
st.markdown("Caffeine Consumption & Sleep Analysis")
st.markdown("---")

# --- FIRST ROW (PIE + HISTOGRAM) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution")
    if '3. Gender' in df.columns:
        # Pie with Neon Blue and Yellow
        fig_gender = px.pie(df, names='3. Gender', hole=0.5, color_discrete_sequence=['#33CCFF', '#FFFF66'])
        fig_gender.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0', margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Daily Caffeine Consumption")
    if '4. Number of cups per day' in df.columns:
        # Grouped Histogram with Neon Blue & Purple
        fig_cups = px.histogram(df, x='4. Number of cups per day', color='3. Gender', barmode='group', color_discrete_sequence=['#33CCFF', '#CC33FF'])
        fig_cups.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig_cups, use_container_width=True)

st.markdown("---")

# --- SECOND ROW (BAR + HISTOGRAM) ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Caffeine Intake Timing")
    if '6. Timing of last cup' in df.columns:
        # Neon Pink Bar
        fig_timing = px.bar(df, x='6. Timing of last cup', color_discrete_sequence=['#FF66FF'])
        fig_timing.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig_timing, use_container_width=True)

with col4:
    st.subheader("Sleep Quality Distribution")
    if '12. Sleep Quality' in df.columns:
        # Neon Blue Histogram
        fig_sleep = px.histogram(df, x='12. Sleep Quality', color_discrete_sequence=['#33CCFF'])
        fig_sleep.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig_sleep, use_container_width=True)

st.markdown("---")

# --- THIRD ROW: LIVE/DYNAMIC KEY STATS (NEW ADDITION) ---
st.subheader("Live Participant Metrics")

# 5. Dynamic Calculations (Numbers that change)
if '3. Gender' in df.columns:
    total_users = len(df)
    
    # Calculate Males and Females
    # (Assuming gender is coded as 'Male' and 'Female', adjust if it's 'ذكر' / 'أنثى')
    male_count = len(df[df['3. Gender'] == 'Male']) 
    female_count = len(df[df['3. Gender'] == 'Female'])

    # 6. Create Dynamic Metric Cards
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.metric(label="Total Participants", value=total_users)

    with kpi2:
        # Div with class to apply specific Neon Yellow color
        st.markdown('<div class="male-stat">', unsafe_allow_html=True)
        st.metric(label="Total Males", value=male_count)
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi3:
        # Div with class to apply specific Neon Blue color
        st.markdown('<div class="female-stat">', unsafe_allow_html=True)
        st.metric(label="Total Females", value=female_count)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("Cannot calculate dynamic metrics. '3. Gender' column missing.")

# Optional: Button to manually trigger a data refresh
if st.button("Refresh LIVE Data Now"):
    st.rerun()

)

# عرض الشارت التفاعلي
st.plotly_chart(fig, use_container_width=True)
