# نستورد المكتبات اللي نحتاجها
# streamlit لعرض الداشبورد
# pandas للتعامل مع البيانات
# plotly لرسم الجراف التفاعلي
# math لحساب المسافات الرياضية
import streamlit as st
import pandas as pd
import plotly.express as px
import math


# =========================
# LOAD DATA
# =========================
# ملف نتائج الكلستر   
# هذا الملف فيه كل المستخدمين + رقم الكلستر لكل واحد
cluster_data = pd.read_csv("data/clustering_results.csv")


# =========================
# PAGE CONFIG
# =========================
# إعدادات الصفحة في Streamlit
st.set_page_config(
    page_title="Riyalyze Dashboard",  # اسم الصفحة
    layout="wide",                    # العرض عريض
    initial_sidebar_state="expanded"  # السايدبار مفتوح
)


# =========================
# CUSTOM CSS
# =========================
# هذا CSS لتصميم الداشبورد
# يغير الألوان والخلفية والبطاقات
st.markdown("""
<style>
.stApp{
    background-color:#020F2F;
    color:white;
}

/* اخفاء الهيدر الافتراضي */
header[data-testid="stHeader"]{
    background:transparent;
}

/* تصميم السايدبار */
section[data-testid="stSidebar"]{
    background:#020B24;
    border-right:1px solid rgba(255,255,255,0.05);
}

/* لون النص في السايدبار */
section[data-testid="stSidebar"] *{
    color:white !important;
}

/* تصميم العناوين */
.main-title{
    font-size:34px;
    font-weight:700;
}

.sub-title{
    font-size:14px;
    color:#9EB1E0;
    margin-bottom:20px;
}

/* تصميم الكروت */
.card{
    background:#071A45;
    border:1px solid rgba(255,255,255,0.05);
    border-radius:14px;
    padding:14px 16px;
}

/* عنوان الأقسام */
.section-title{
    font-size:20px;
    font-weight:600;
    margin-top:30px;
    margin-bottom:10px;
}

/* بوكس نتيجة الكلستر */
.chart-box{
    background:#071A45;
    border:1px solid rgba(255,255,255,0.05);
    border-radius:16px;
    min-height:120px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#DCE7FF;
    font-size:20px;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
# هذا السايدبار اللي على اليسار
st.sidebar.markdown("## Riyalyze")
st.sidebar.radio("", ["🏠 Dashboard"])


# =========================
# USER DATA (TEMP VALUES)
# =========================
# هذه بيانات مستخدم افتراضية
# بيانات راح تجي من الاستبيان أو قاعدة البيانات

user_caffeine = 2
user_sleep = 7
user_fast_food = 2
user_activity = 3
user_screen = 6
user_sleep_quality = 3
user_eat_late = 0
user_caffeine_late = 0
user_low_energy = 3


# نجمع بيانات المستخدم في dictionary
# عشان نستخدمها لاحقًا في حساب الكلستر
user_row = {
    "caffeine_per_day": user_caffeine,
    "fast_food_per_week": user_fast_food,
    "sleep_hours": user_sleep,
    "physical_activity_days": user_activity,
    "screen_hours": user_screen,
    "sleep_quality": user_sleep_quality,
    "eat_after_10pm": user_eat_late,
    "caffeine_after_8pm": user_caffeine_late,
    "low_energy_frequency": user_low_energy
}


# =========================
# TITLES
# =========================
# عنوان الداشبورد
st.markdown('<div class="main-title">Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your Lifestyle Summary</div>', unsafe_allow_html=True)


# =========================
# SIMPLE RISK SCORE
# =========================
# هنا نحسب risk score بسيط بناءً على العادات
risk_score = (
    user_caffeine * 4
    + user_fast_food * 3
    + user_screen * 3
    + max(0, 8 - user_sleep) * 4
    + (5 - user_sleep_quality) * 5
    + user_eat_late * 8
    + user_caffeine_late * 8
    + (user_low_energy - 1) * 4
    - user_activity * 3
)

# نضمن أن السكور بين 0 و 100
risk_score = max(0, min(round(risk_score), 100))


# =========================
# KPI CARDS
# =========================
# هنا نعرض معلومات المستخدم في كروت

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
    ☕ Your Caffeine Intake
    <br><b>{user_caffeine}</b> Cups/day
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
    🌙 Your Sleep Hours
    <br><b>{user_sleep}</b> Hours/Night
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
    🍟 Fast Food / Week
    <br><b>{user_fast_food}</b> Times
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
    📉 Risk Score
    <br><b>{risk_score}</b>
    </div>
    """, unsafe_allow_html=True)


# =========================
# CLUSTER LABELS
# =========================
# أسماء الكلسترات
cluster_names = {
    0: "Cluster A",
    1: "Cluster B",
    2: "Cluster C"
}


# =========================
# PREDICT USER CLUSTER
# =========================
# هنا نحسب أقرب كلستر للمستخدم

feature_cols = [
    "caffeine_per_day",
    "fast_food_per_week",
    "sleep_hours",
    "physical_activity_days",
    "screen_hours",
    "sleep_quality",
    "eat_after_10pm",
    "caffeine_after_8pm",
    "low_energy_frequency"
]

# نحسب مركز كل كلستر
cluster_centers = cluster_data.groupby("cluster")[feature_cols].mean()

# نحسب المتوسط والانحراف المعياري
feature_means = cluster_data[feature_cols].mean()
feature_stds = cluster_data[feature_cols].std().replace(0, 1)

#  standardization لبيانات المستخدم
user_scaled = {
    col: (user_row[col] - feature_means[col]) / feature_stds[col]
    for col in feature_cols
}

centers_scaled = (cluster_centers - feature_means) / feature_stds

# نحسب المسافة بين المستخدم وكل كلستر
distances = {}

for cluster_id in centers_scaled.index:

    distance = 0

    for col in feature_cols:
        distance += (user_scaled[col] - centers_scaled.loc[cluster_id, col]) ** 2

    distances[cluster_id] = math.sqrt(distance)

# نختار أقرب كلستر
user_cluster = min(distances, key=distances.get)

user_cluster_name = cluster_names.get(user_cluster, f"Cluster {user_cluster}")


# =========================
# CLUSTER AREA
# =========================
st.markdown('<div class="section-title">Cluster Comparison Chart</div>', unsafe_allow_html=True)

# نحسب متوسطات الكلسترات وعدد المستخدمين في كل كلستر
cluster_summary = (
    cluster_data.groupby("cluster")
    .agg(
        caffeine_per_day=("caffeine_per_day", "mean"),
        screen_hours=("screen_hours", "mean"),
        user_count=("cluster", "size")
    )
    .reset_index()
)

cluster_summary["cluster_name"] = cluster_summary["cluster"].map(cluster_names)

# النص اللي يظهر فوق كل فقاعة
cluster_summary["label"] = (
    cluster_summary["cluster_name"]
    + "<br>Users: "
    + cluster_summary["user_count"].astype(str)
)

# رسم الفقاعات
fig = px.scatter(
    cluster_summary,
    x="caffeine_per_day",
    y="screen_hours",
    size="user_count",
    color="cluster_name",
    text="label",
    size_max=70,
    color_discrete_map={
        "Cluster A": "#d94db5",  # وردي
        "Cluster B": "#2bb9e8",  # أزرق
        "Cluster C": "#8b5cf6"   # بنفسجي
    },
    hover_data={
        "caffeine_per_day": ":.2f",
        "screen_hours": ":.2f",
        "user_count": True,
        "cluster_name": False
    }
)

# نقطة المستخدم
fig.add_scatter(
    x=[user_caffeine],
    y=[user_screen],
    mode="markers+text",
    text=["You"],
    textposition="bottom center",
    marker=dict(
        size=16,
        color="#FFD166",
        symbol="diamond",
        line=dict(color="white", width=2)
    ),
    name="You"
)

# تنسيق شكل الفقاعات
fig.update_traces(
    textposition="top center",
    marker=dict(
        line=dict(color="white", width=2),
        opacity=0.9
    ),
    selector=dict(mode="markers")
)

# تنسيق الخلفية والمحاور
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1742",
    plot_bgcolor="#0f1f5c",
    font=dict(color="white", size=16),
    xaxis=dict(
        title="Average Caffeine Intake (cups/day)",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.12)",
        zeroline=False
    ),
    yaxis=dict(
        title="Average Screen Hours",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.12)",
        zeroline=False
    ),
    legend_title="",
    margin=dict(l=20, r=20, t=20, b=20),
    height=600
)

st.plotly_chart(fig, use_container_width=True)