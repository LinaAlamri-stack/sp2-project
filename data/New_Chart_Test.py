import pandas as pd
import plotly.express as px
import streamlit as st
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Health Habits Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. تصميم CSS المخصص (نفس التصميم الأصلي)
st.markdown("""
    <style>
    .main { background-color: #060914; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #ffffff !important; }
    .stSubheader { color: #ffffff !important; font-weight: 600; }
    [data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart),
    div[data-testid="stMetricValue"] {
        background-color: #0d1225;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,255,255,0.03);
        margin-bottom: 20px;
    }
    div[data-testid="metric-container"] { background-color: transparent !important; border: none !important; }
    div[data-testid="stMetricLabel"] { color: #a0a0a0 !important; font-size: 16px; }
    div[data-testid="stMetricValue"] { color: #33CCFF !important; font-size: 32px; }
    </style>
    """, unsafe_allow_html=True)

# 3. تحميل البيانات
@st.cache_data(ttl=10)
def load_data():
    paths = ["data/survey_data.csv", "survey_data.csv", "../data/survey_data.csv"]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

df = load_data()

# 4. العنوان الرئيسي
st.title("User Habits & Health Analytics")
st.markdown("Caffeine Consumption & Sleep Analysis")
st.markdown("---")

# 5. --- إصلاح المؤشرات العلوية (المطلوب الأساسي) ---
st.subheader("Live Participant Metrics")

total_users = len(df)
# نستخدم iloc للوصول لثالث عمود (Gender) بغض النظر عن اسمه الطويل
male_count = len(df[df.iloc[:, 2] == 'Male']) 
female_count = len(df[df.iloc[:, 2] == 'Female'])

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Total Participants", value=total_users)
kpi2.metric(label="Male Participants", value=male_count)
kpi3.metric(label="Female Participants", value=female_count)

st.markdown("<br>", unsafe_allow_html=True)

# 6. --- الحفاظ على التشارتس الستة الأصلية (ROW 1 & ROW 2) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution (Original)")
    # نفس الدائرة الأصلية بالأزرق والأصفر
    fig_gender = px.pie(df, names=df.columns[2], hole=0.5, color_discrete_sequence=['#33CCFF', '#FFFF66'])
    fig_gender.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Daily Cups Consumption (Histogram)")
    # نفس الهستوجرام الأصلي
    fig_cups = px.histogram(df, x=df.columns[3], color=df.columns[2], barmode='group', color_discrete_sequence=['#33CCFF', '#CC33FF'])
    fig_cups.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_cups, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Caffeine Intake Timing")
    # نفس التشارت الأصلي
    fig_timing = px.bar(df, x=df.columns[5], color_discrete_sequence=['#FF66FF'])
    fig_timing.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_timing, use_container_width=True)

with col4:
    st.subheader("Sleep Quality Score Distribution")
    # نفس التشارت الأصلي
    fig_sleep = px.histogram(df, x=df.columns[11], color_discrete_sequence=['#33CCFF'])
    fig_sleep.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_sleep, use_container_width=True)

# 7. --- الحفاظ على التشارتس الجديدة (ROW 3) ---
st.markdown("---")
st.subheader("Deep Dive: Age & Status")
col5, col6 = st.columns(2)

with col5:
    st.subheader("Age Group Distribution")
    fig_age = px.bar(df, x=df.columns[1], color_discrete_sequence=['#CC33FF'])
    fig_age.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_age, use_container_width=True)

with col6:
    st.subheader("Drink Type Preferences")
    fig_drink = px.pie(df, names=df.columns[4], hole=0.5)
    fig_drink.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    st.plotly_chart(fig_drink, use_container_width=True)
# Auto-Refresh Hint
st.info("💡 Data refreshes automatically every 10 seconds as new users submit the survey.")
