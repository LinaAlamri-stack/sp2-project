import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/survey_data.csv")

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="User Demographics Dashboard",  # عنوان الصفحة
    layout="wide",                            # العرض عريض
    initial_sidebar_state="expanded"          # السايدبار مفتوح
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0a1d37;
    color: white;
}

/* تصميم السايدبار */
section[data-testid="stSidebar"] {
    background: #020B24;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* تعديل الألوان والتنسيقات */
.card {
    background: #071A45;
    border-radius: 14px;
    padding: 16px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## User Demographics")

# =========================
# CALCULATE USER STATS
# =========================
# حساب عدد المستخدمين
total_users = df.shape[0]

# حساب عدد الذكور والإناث
gender_counts = df['gender'].value_counts()

# =========================
# TITLES
# =========================
st.markdown('<h1>User Demographics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<h3>Summary of User Information</h3>', unsafe_allow_html=True)

# عرض عدد المستخدمين
st.markdown(f"**Total number of users:** {total_users}")

# عرض عدد الذكور والإناث
st.markdown(f"**Number of Males:** {gender_counts.get('Male', 0)}")
st.markdown(f"**Number of Females:** {gender_counts.get('Female', 0)}")

# =========================
# NEW USER FEATURE
# =========================
# للتحقق إذا كان المستخدم الجديد
# هنا نعتبر أن المستخدم الجديد إذا كانت قيمة "user_id" لا توجد في البيانات

new_user_id = "new_user_id_example"  # هذا معرّف المستخدم الجديد الذي سيتم التحقق منه
new_user_check = new_user_id not in df['user_id'].values

if new_user_check:
    st.markdown(f"**New User Detected**: Yes, {new_user_id} is a new user!")

# =========================
# INTERACTIVE CHART
# =========================
# رسم شارت تفاعلي يوضح توزيع الذكور والإناث
fig = px.pie(
    names=gender_counts.index,
    values=gender_counts.values,
    title="Gender Distribution of Users",
    color=gender_counts.index,
    color_discrete_map={'Male': '#1f77b4', 'Female': '#ff7f0e'}
)

# عرض الشارت التفاعلي
st.plotly_chart(fig, use_container_width=True)
