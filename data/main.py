import streamlit as st
import pandas as pd

# مودلك
from model import load_data, get_metrics

# تشارت هدى
from risk_charts import build_caffeine_sleep_fig, build_risk_level_fig

# -------- إعداد الصفحة --------
st.set_page_config(page_title="Riyalyze Dashboard", layout="wide")

# -------- تحميل البيانات --------
df = load_data()

# -------- الهيدر (حق هدى) --------
st.markdown("## User Survey Results")

# -------- الميتريكس (حقك) --------
if df is not None:
    total, male, female = get_metrics(df)

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total", total)
    kpi2.metric("Male", male)
    kpi3.metric("Female", female)

else:
    st.error("No data found")

# -------- الشارتات (دمجكم سوا 🔥) --------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Risk level distribution")
    fig_risk = build_risk_level_fig()
    st.plotly_chart(fig_risk, use_container_width=True)

with col2:
    st.markdown("### Caffeine vs Sleep Trends")
    fig_trend = build_caffeine_sleep_fig()
    st.plotly_chart(fig_trend, use_container_width=True)

# -------- 
st.markdown("### Additional Insights")

col3, col4 = st.columns(2)

with col3:
    import plotly.express as px
    fig_gender = px.pie(df, names=df.columns[2])
    st.plotly_chart(fig_gender, use_container_width=True)

with col4:
    fig_cups = px.histogram(df, x=df.columns[3])
    st.plotly_chart(fig_cups, use_container_width=True)
