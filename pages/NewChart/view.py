import streamlit as st
import plotly.express as px
import plotly.io as pio

def setup_page():
    st.set_page_config(
        page_title="Health Habits Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
    <style>
    .main { background-color: #060914; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.title("User Habits & Health Analytics")
    st.markdown("Caffeine Consumption & Sleep Analysis")
    st.markdown("---")


def render_metrics(total, male, female):
    st.subheader("Live Participant Metrics")

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Total Participants", value=total)
    kpi2.metric(label="Male Participants", value=male)
    kpi3.metric(label="Female Participants", value=female)


def render_charts(df):
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gender = px.pie(df, names=df.columns[2])
        #st.plotly_chart(fig_gender, use_container_width=True)
        chart1 = pio.to_html(fig_gender, full_html=False, include_plotlyjs="cdn")

    with col2:
        fig_cups = px.histogram(df, x=df.columns[3])
        #st.plotly_chart(fig_cups, use_container_width=True)
        chart2 = pio.to_html(fig_cups, full_html=False, include_plotlyjs="cdn")
    return (chart1,chart2)


def render_footer():
    st.info("💡 Data refreshes automatically every 10 seconds.")
