import sqlite3
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Riyalyze | Challenge Match",
    layout="wide"
)
from database import DB_PATH, init_db

# ==========================================
# PAGE CONFIG
# ==========================================
params = st.query_params
uid_param = params.get("uid")

if isinstance(uid_param, list):
    uid_param = uid_param[0] if uid_param else None

if "user_id" not in st.session_state and uid_param and str(uid_param).isdigit():
    st.session_state["user_id"] = int(uid_param)
    


# ==========================================
# INIT DB
# ==========================================

init_db()

components.html(
    """
    <script>
        const scrollTopNow = () => {
            window.parent.scrollTo(0, 0);
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
        };
        scrollTopNow();
        setTimeout(scrollTopNow, 50);
        setTimeout(scrollTopNow, 200);
    </script>
    """,
    height=0,
)

# ==========================================
# HELPERS
# ==========================================
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_users_with_surveys() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.gender,
                u.weight,
                u.height,
                s.full_name,
                s.age,
                s.caffeine_per_day,
                s.fast_food_per_week,
                s.sleep_hours,
                s.physical_activity_days,
                s.screen_hours,
                s.sleep_quality,
                s.eat_after_10pm,
                s.caffeine_after_8pm,
                s.low_energy_frequency,
                s.risk_score,
                s.risk_level,
                s.projection_title,
                s.projection_status,
                s.projection_cluster,
                s.updated_at
            FROM users u
            LEFT JOIN user_surveys s
                ON u.id = s.user_id
            ORDER BY u.id
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_user_with_survey(user_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
                u.id,
                u.name,
                u.email,
                u.gender,
                u.weight,
                u.height,
                s.full_name,
                s.age,
                s.caffeine_per_day,
                s.fast_food_per_week,
                s.sleep_hours,
                s.physical_activity_days,
                s.screen_hours,
                s.sleep_quality,
                s.eat_after_10pm,
                s.caffeine_after_8pm,
                s.low_energy_frequency,
                s.risk_score,
                s.risk_level,
                s.projection_title,
                s.projection_status,
                s.projection_cluster,
                s.updated_at
            FROM users u
            LEFT JOIN user_surveys s
                ON u.id = s.user_id
            WHERE u.id = ?
            """,
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def compute_health_score(user: dict) -> int:
    score = 100

    sleep_hours = user.get("sleep_hours") or 0
    physical_days = user.get("physical_activity_days") or 0
    screen_hours = user.get("screen_hours") or 0
    caffeine_per_day = user.get("caffeine_per_day") or 0
    fast_food_per_week = user.get("fast_food_per_week") or 0
    eat_after_10pm = user.get("eat_after_10pm") or 0
    caffeine_after_8pm = user.get("caffeine_after_8pm") or 0

    if sleep_hours < 6:
        score -= 20
    elif sleep_hours < 7:
        score -= 10

    if physical_days < 2:
        score -= 15
    elif physical_days < 4:
        score -= 8

    if screen_hours > 8:
        score -= 15
    elif screen_hours > 6:
        score -= 8

    if caffeine_per_day >= 3:
        score -= 10
    elif caffeine_per_day == 2:
        score -= 5

    if fast_food_per_week >= 5:
        score -= 12
    elif fast_food_per_week >= 3:
        score -= 6

    if eat_after_10pm == 1:
        score -= 8

    if caffeine_after_8pm == 1:
        score -= 8

    return max(0, min(100, score))


def choose_goal(user: dict) -> str:
    sleep_hours = user.get("sleep_hours") or 0
    screen_hours = user.get("screen_hours") or 0
    physical_days = user.get("physical_activity_days") or 0
    caffeine_per_day = user.get("caffeine_per_day") or 0
    risk_level = (user.get("risk_level") or "").strip().lower()
    cluster = (user.get("projection_cluster") or "").strip()

    if screen_hours >= 8:
        return "Reduce Screen Time"
    if sleep_hours < 6:
        return "Improve Sleep"
    if physical_days < 2:
        return "Increase Physical Activity"
    if caffeine_per_day >= 3:
        return "Reduce Caffeine Intake"
    if cluster:
        return f"Compete within {cluster}"
    if risk_level == "high":
        return "Improve Lifestyle Risk"
    return "Maintain Healthy Lifestyle"


def find_match(current_user: dict, users: list[dict]) -> Optional[dict]:
    current_id = current_user["id"]
    current_goal = choose_goal(current_user)
    current_cluster = (current_user.get("projection_cluster") or "").strip().lower()
    current_risk = (current_user.get("risk_level") or "").strip().lower()
    current_score = compute_health_score(current_user)

    same_goal = [
        u for u in users
        if u["id"] != current_id and choose_goal(u) == current_goal
    ]
    if same_goal:
        same_goal.sort(key=lambda x: abs(compute_health_score(x) - current_score))
        return same_goal[0]

    same_cluster = [
        u for u in users
        if u["id"] != current_id
        and (u.get("projection_cluster") or "").strip().lower() == current_cluster
        and current_cluster != ""
    ]
    if same_cluster:
        same_cluster.sort(key=lambda x: abs(compute_health_score(x) - current_score))
        return same_cluster[0]

    same_risk = [
        u for u in users
        if u["id"] != current_id
        and (u.get("risk_level") or "").strip().lower() == current_risk
        and current_risk != ""
    ]
    if same_risk:
        same_risk.sort(key=lambda x: abs(compute_health_score(x) - current_score))
        return same_risk[0]

    others = [u for u in users if u["id"] != current_id]
    if others:
        others.sort(key=lambda x: abs(compute_health_score(x) - current_score))
        return others[0]

    return None


def metric_tag(label: str, value: str) -> str:
    return f"""
    <div class="metric-pill">
        <span class="metric-label">{label}</span>
        <span class="metric-value">{value}</span>
    </div>
    """


def progress_bar_html(value: int) -> str:
    safe_value = max(0, min(100, value))
    return f"""
    <div class="progress-wrap">
        <div class="progress-fill" style="width:{safe_value}%;"></div>
    </div>
    """


# ==========================================
# STYLE
# ==========================================
st.markdown("""
<style>
    header, footer,
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stToolbar"] {
        display: none !important;
    }

    .stApp {
        background: radial-gradient(circle at top left, #17124a 0%, #081033 42%, #03081f 100%);
        color: #f4f6ff;
    }

    .block-container {
        padding-top: 0.9rem !important;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    .back-wrap {
        margin-top: 0;
        margin-bottom: 1.25rem;
    }

    .back-wrap div[data-testid="stButton"] {
        width: auto;
        margin: 0;
    }

    .back-wrap div[data-testid="stButton"] > button {
        width: auto;
        min-width: 0;
        padding: 10px 18px;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        color: #f4f6ff;
        box-shadow: none;
        margin-top: 0;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(19, 24, 59, 0.98), rgba(11, 15, 38, 0.98));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 20px 22px;
        min-height: 145px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.20);
    }

    [data-testid="stMetricLabel"] {
        color: #aeb7de;
        font-size: 14px;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
    }

    .hero-card {
        background: linear-gradient(145deg, rgba(18, 24, 58, 0.97), rgba(8, 12, 32, 0.97));
        border: 1px solid rgba(125, 105, 255, 0.20);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.28);
        margin-bottom: 20px;
    }

    .section-card {
        background: linear-gradient(145deg, rgba(16, 21, 50, 0.98), rgba(9, 12, 30, 0.98));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 26px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.22);
        min-height: 100%;
    }

    .title {
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 10px;
        color: #ffffff;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 18px;
        color: #b4bcdf;
        margin-bottom: 0;
        line-height: 1.6;
    }

    .card-title {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .card-subtitle {
        font-size: 14px;
        color: #99a4d1;
        margin-bottom: 18px;
        line-height: 1.6;
    }

    .player-name {
        font-size: 28px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 10px;
        line-height: 1.2;
        word-break: break-word;
    }

    .goal-badge {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 999px;
        background: linear-gradient(90deg, #8b5cf6, #ec4899);
        color: white;
        font-size: 13px;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(200, 90, 255, 0.18);
    }

    .metric-pill {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 12px 15px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #c1c9ea;
        font-size: 14px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 15px;
        font-weight: 800;
        text-align: right;
    }

    .score-box {
        background: linear-gradient(145deg, rgba(75, 96, 255, 0.20), rgba(216, 67, 255, 0.14));
        border: 1px solid rgba(125, 105, 255, 0.30);
        border-radius: 20px;
        padding: 20px;
        margin-top: 18px;
        margin-bottom: 14px;
        text-align: center;
    }

    .score-number {
        font-size: 42px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 8px;
    }

    .score-text {
        color: #b4bcdf;
        font-size: 14px;
        font-weight: 600;
    }

    .progress-wrap {
        width: 100%;
        height: 16px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 6px;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.18);
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #7c3aed 0%, #c026d3 55%, #ec4899 100%);
        box-shadow: 0 0 18px rgba(192, 38, 211, 0.35);
    }

    .vs-box {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100%;
        font-size: 38px;
        font-weight: 900;
        color: #e6ddff;
        padding-top: 30px;
    }

    .winner-box {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.16), rgba(59, 130, 246, 0.16));
        border: 1px solid rgba(91, 211, 165, 0.30);
        border-radius: 20px;
        padding: 18px;
        color: #f8fffb;
        font-size: 18px;
        font-weight: 800;
        margin-top: 12px;
    }

    .hint-box {
        background: rgba(255,255,255,0.04);
        border-left: 4px solid #8b5cf6;
        padding: 14px 16px;
        border-radius: 14px;
        color: #d6dcf8;
        margin-top: 14px;
        line-height: 1.7;
    }

    .stButton > button {
        width: 100%;
        border-radius: 16px;
        border: none;
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        color: white;
        font-weight: 800;
        height: 48px;
        margin-top: 10px;
    }

    div[data-testid="column"] {
        align-self: stretch;
    }

    @media (max-width: 900px) {
        .title {
            font-size: 38px;
        }

        .player-name {
            font-size: 24px;
        }

        [data-testid="stMetric"] {
            min-height: 120px;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="back-wrap">', unsafe_allow_html=True)
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/3_Dashboard.py")
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# LOAD USERS
# ==========================================
all_users = get_all_users_with_surveys()

st.markdown('<div class="title">🔥 Challenge Match</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Match users with similar goals and let them compete to improve their lifestyle habits.</div>',
    unsafe_allow_html=True
)

if not all_users:
    st.warning("No users with survey data were found yet.")
    st.stop()

# ==========================================
# CURRENT USER
if "user_id" not in st.session_state:
    st.error("Please login first.")
    st.stop()

current_user = get_user_with_survey(st.session_state["user_id"])

if not current_user:
    st.error("No user data found for the logged-in user.")
    st.stop()
# ==========================================

matched_user = find_match(current_user, all_users)
goal = choose_goal(current_user)
current_score = compute_health_score(current_user)
match_score = compute_health_score(matched_user) if matched_user else 0

# ==========================================
# TOP SUMMARY
# ==========================================
summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric(
        "Selected User",
        current_user.get("full_name") or current_user.get("name") or "User"
    )

with summary_col2:
    st.metric("Challenge Goal", goal)

with summary_col3:
    st.metric(
        "Matched User",
        (matched_user.get("full_name") or matched_user.get("name") or "No Match")
        if matched_user else "No Match"
    )

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

# ==========================================
# PLAYER CARDS
# ==========================================
col1, col_mid, col2 = st.columns([1.15, 0.35, 1.15])

with col1:
    st.markdown('<div class="card-title">Your Profile</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="player-name">{current_user.get("full_name") or current_user.get("name") or "User"}</div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="goal-badge">{goal}</div>', unsafe_allow_html=True)

    st.markdown(metric_tag("Risk Level", str(current_user.get("risk_level") or "N/A").title()), unsafe_allow_html=True)
    st.markdown(metric_tag("Cluster", str(current_user.get("projection_cluster") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Sleep Hours", str(current_user.get("sleep_hours") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Screen Hours", str(current_user.get("screen_hours") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Activity Days", str(current_user.get("physical_activity_days") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Caffeine / Day", str(current_user.get("caffeine_per_day") or "N/A")), unsafe_allow_html=True)

    st.markdown(f'''
    <div class="score-box">
        <div class="score-number">{current_score}</div>
        <div class="score-text">Health Score</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(progress_bar_html(current_score), unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="vs-box">VS ⚔️</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card-title">Matched User</div>', unsafe_allow_html=True)

    if matched_user:
        st.markdown(
            f'<div class="player-name">{matched_user.get("full_name") or matched_user.get("name") or "User"}</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="goal-badge">{goal}</div>', unsafe_allow_html=True)

        st.markdown(metric_tag("Risk Level", str(matched_user.get("risk_level") or "N/A").title()), unsafe_allow_html=True)
        st.markdown(metric_tag("Cluster", str(matched_user.get("projection_cluster") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Sleep Hours", str(matched_user.get("sleep_hours") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Screen Hours", str(matched_user.get("screen_hours") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Activity Days", str(matched_user.get("physical_activity_days") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Caffeine / Day", str(matched_user.get("caffeine_per_day") or "N/A")), unsafe_allow_html=True)

        st.markdown(f'''
        <div class="score-box">
            <div class="score-number">{match_score}</div>
            <div class="score-text">Health Score</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown(progress_bar_html(match_score), unsafe_allow_html=True)
    else:
        st.info("No suitable match found yet.")



# ==========================================
# WINNER + DETAILS
# ==========================================

    st.markdown('<div class="card-title">🏆 Challenge Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Live comparison based on current health score.</div>', unsafe_allow_html=True)

    if matched_user:
        if current_score > match_score:
            winner_text = f'Winner so far: {current_user.get("full_name") or current_user.get("name")} 🏆'
        elif match_score > current_score:
            winner_text = f'Winner so far: {matched_user.get("full_name") or matched_user.get("name")} 🏆'
        else:
            winner_text = "It is currently a tie 🤝"

        st.markdown(f'<div class="winner-box">{winner_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="winner-box">Waiting for another user to join the challenge.</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hint-box">
            <b>Challenge rule:</b> The user with the healthier lifestyle score leads the challenge.
        </div>
        """,
        unsafe_allow_html=True
    )



    st.markdown('<div class="card-title">📌 Challenge Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Automatically generated based on the current user profile.</div>', unsafe_allow_html=True)

    st.write(f"**Goal:** {goal}")
    st.write(f"**Projection Title:** {current_user.get('projection_title') or 'N/A'}")
    st.write(f"**Projection Status:** {current_user.get('projection_status') or 'N/A'}")
    st.write(f"**Lifestyle Cluster:** {current_user.get('projection_cluster') or 'N/A'}")
    st.write(f"**Current Risk Level:** {str(current_user.get('risk_level') or 'N/A').title()}")

    st.markdown("---")
    st.write("**Suggested challenge objective:**")

    if goal == "Reduce Screen Time":
        st.write("- Keep daily screen time below 6 hours.")
    elif goal == "Improve Sleep":
        st.write("- Reach at least 7 hours of sleep consistently.")
    elif goal == "Increase Physical Activity":
        st.write("- Complete physical activity at least 4 days per week.")
    elif goal == "Reduce Caffeine Intake":
        st.write("- Limit caffeine intake and avoid it late at night.")
    else:
        st.write("- Maintain a balanced and healthy lifestyle pattern.")

tips = []

if goal == "Reduce Screen Time":
    tips = [
        "Try a 1-hour no-phone time before sleep 📵",
        "Replace screen time with a short walk 🚶‍♀️",
        "Use app limits to control usage ⏳"
    ]
elif goal == "Improve Sleep":
    tips = [
        "Sleep at the same time every day 🌙",
        "Avoid caffeine after 8 PM ☕",
        "Keep your room dark and quiet 💤"
    ]
elif goal == "Increase Physical Activity":
    tips = [
        "Start with just 10 minutes a day 💪",
        "Walk instead of short drives 🚶",
        "Find an activity you enjoy 🎯"
    ]
elif goal == "Reduce Caffeine Intake":
    tips = [
        "Switch one coffee to water 💧",
        "Avoid caffeine late in the day 🌙",
        "Track your daily intake 📊"
    ]
else:
    tips = [
        "Small changes lead to big results 🌱",
        "Stay consistent, not perfect ✨",
        "Your future self will thank you 💖"
    ]

st.markdown("### ✨ Stay Motivated")
st.markdown("Small daily habits make a big difference.")

for tip in tips:
    st.markdown(f"- {tip}")

st.info("Keep going — you're doing better than you think 🚀")
