import sqlite3
from typing import Optional

import streamlit as st

from database import DB_PATH, init_db

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Riyalyze | Challenge Match",
    layout="wide"
)

# ==========================================
# INIT DB
# ==========================================
init_db()

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
            JOIN user_surveys s
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
            JOIN user_surveys s
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
    current_cluster = (current_user.get("projection_cluster") or "").strip().lower()
    current_risk = (current_user.get("risk_level") or "").strip().lower()

    # 1) Prefer same cluster
    same_cluster = [
        u for u in users
        if u["id"] != current_id
        and (u.get("projection_cluster") or "").strip().lower() == current_cluster
        and current_cluster != ""
    ]
    if same_cluster:
        same_cluster.sort(key=lambda x: abs(compute_health_score(x) - compute_health_score(current_user)))
        return same_cluster[0]

    # 2) Then same risk level
    same_risk = [
        u for u in users
        if u["id"] != current_id
        and (u.get("risk_level") or "").strip().lower() == current_risk
        and current_risk != ""
    ]
    if same_risk:
        same_risk.sort(key=lambda x: abs(compute_health_score(x) - compute_health_score(current_user)))
        return same_risk[0]

    # 3) Then nearest score
    others = [u for u in users if u["id"] != current_id]
    if others:
        others.sort(key=lambda x: abs(compute_health_score(x) - compute_health_score(current_user)))
        return others[0]

    return None


def metric_tag(label: str, value: str) -> str:
    return f"""
    <div class="metric-pill">
        <span class="metric-label">{label}</span>
        <span class="metric-value">{value}</span>
    </div>
    """


# ==========================================
# STYLE
# ==========================================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, #1b1453 0%, #0b1028 38%, #070b1b 100%);
        color: #f3f4ff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    .hero-card {
        background: linear-gradient(145deg, rgba(21, 28, 63, 0.96), rgba(9, 13, 39, 0.96));
        border: 1px solid rgba(135, 109, 255, 0.25);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.30);
        margin-bottom: 22px;
    }

    .section-card {
        background: linear-gradient(145deg, rgba(18, 24, 56, 0.96), rgba(10, 14, 33, 0.96));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.24);
        height: 100%;
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 6px;
        color: #ffffff;
    }

    .subtitle {
        font-size: 17px;
        color: #aab2d6;
        margin-bottom: 0;
    }

    .card-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .card-subtitle {
        font-size: 14px;
        color: #9ea7d3;
        margin-bottom: 18px;
    }

    .player-name {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .goal-badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        color: white;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .metric-pill {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #bfc7ea;
        font-size: 14px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 15px;
        font-weight: 700;
    }

    .score-box {
        background: linear-gradient(145deg, rgba(77, 101, 255, 0.18), rgba(190, 60, 255, 0.14));
        border: 1px solid rgba(125, 105, 255, 0.28);
        border-radius: 18px;
        padding: 18px;
        margin-top: 16px;
        margin-bottom: 18px;
        text-align: center;
    }

    .score-number {
        font-size: 40px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 6px;
    }

    .score-text {
        color: #aab2d6;
        font-size: 14px;
    }

    .vs-box {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 240px;
        font-size: 34px;
        font-weight: 900;
        color: #d8ccff;
    }

    .winner-box {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.16), rgba(59, 130, 246, 0.16));
        border: 1px solid rgba(91, 211, 165, 0.30);
        border-radius: 18px;
        padding: 18px;
        color: #f8fffb;
        font-size: 18px;
        font-weight: 700;
        margin-top: 10px;
    }

    .hint-box {
        background: rgba(255,255,255,0.04);
        border-left: 4px solid #8b5cf6;
        padding: 14px 16px;
        border-radius: 12px;
        color: #d4daf8;
        margin-top: 12px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 14px;
        border-radius: 16px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        background: linear-gradient(90deg, #7c3aed, #ec4899);
        color: white;
        font-weight: 700;
        height: 46px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD USERS
# ==========================================
all_users = get_all_users_with_surveys()

st.markdown('<div class="hero-card">', unsafe_allow_html=True)
st.markdown('<div class="title">🔥 Challenge Match</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Match users with similar goals and let them compete to improve their lifestyle habits.</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

if not all_users:
    st.warning("No users with survey data were found yet. Make sure at least one user has completed the survey.")
    st.stop()

# ==========================================
# USER SELECTOR
# ==========================================
user_options = {
    f'{u["id"]} - {u.get("full_name") or u.get("name") or u.get("email")}': u["id"]
    for u in all_users
}

selected_label = st.selectbox(
    "Choose a user to generate a challenge match",
    options=list(user_options.keys())
)

selected_user_id = user_options[selected_label]
current_user = get_user_with_survey(selected_user_id)

if not current_user:
    st.error("Selected user was not found.")
    st.stop()

matched_user = find_match(current_user, all_users)
goal = choose_goal(current_user)

current_score = compute_health_score(current_user)
match_score = compute_health_score(matched_user) if matched_user else 0

current_progress = current_score / 100
match_progress = match_score / 100 if matched_user else 0

# ==========================================
# TOP SUMMARY
# ==========================================
summary_col1, summary_col2, summary_col3 = st.columns(3)
with summary_col1:
    st.metric("Selected User", current_user.get("full_name") or current_user.get("name") or "User")
with summary_col2:
    st.metric("Challenge Goal", goal)
with summary_col3:
    st.metric("Matched User", matched_user.get("full_name") or matched_user.get("name") if matched_user else "No Match")

# ==========================================
# PLAYER CARDS
# ==========================================
col1, col_mid, col2 = st.columns([1.2, 0.4, 1.2])

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="player-name">{}</div>'.format(current_user.get("full_name") or current_user.get("name") or "User"), unsafe_allow_html=True)
    st.markdown(f'<div class="goal-badge">{goal}</div>', unsafe_allow_html=True)

    st.markdown(metric_tag("Risk Level", str(current_user.get("risk_level") or "N/A").title()), unsafe_allow_html=True)
    st.markdown(metric_tag("Cluster", str(current_user.get("projection_cluster") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Sleep Hours", str(current_user.get("sleep_hours") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Screen Hours", str(current_user.get("screen_hours") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Activity Days", str(current_user.get("physical_activity_days") or "N/A")), unsafe_allow_html=True)
    st.markdown(metric_tag("Caffeine / Day", str(current_user.get("caffeine_per_day") or "N/A")), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
        <div class="score-number">{current_score}</div>
        <div class="score-text">Health Score</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(current_progress)
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="vs-box">VS ⚔️</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Matched User</div>', unsafe_allow_html=True)

    if matched_user:
        st.markdown(
            '<div class="player-name">{}</div>'.format(
                matched_user.get("full_name") or matched_user.get("name") or "User"
            ),
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="goal-badge">{goal}</div>', unsafe_allow_html=True)

        st.markdown(metric_tag("Risk Level", str(matched_user.get("risk_level") or "N/A").title()), unsafe_allow_html=True)
        st.markdown(metric_tag("Cluster", str(matched_user.get("projection_cluster") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Sleep Hours", str(matched_user.get("sleep_hours") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Screen Hours", str(matched_user.get("screen_hours") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Activity Days", str(matched_user.get("physical_activity_days") or "N/A")), unsafe_allow_html=True)
        st.markdown(metric_tag("Caffeine / Day", str(matched_user.get("caffeine_per_day") or "N/A")), unsafe_allow_html=True)

        st.markdown(f"""
        <div class="score-box">
            <div class="score-number">{match_score}</div>
            <div class="score-text">Health Score</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(match_progress)
    else:
        st.info("No suitable match found yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# WINNER + DETAILS
# ==========================================
bottom1, bottom2 = st.columns([1.2, 1])

with bottom1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        Future versions can use daily check-ins, streaks, and live progress updates.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Start Challenge 🚀"):
        st.success("Challenge started successfully! You can now use this page as your challenge overview.")
    st.markdown('</div>', unsafe_allow_html=True)

with bottom2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📌 Challenge Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Automatically generated based on the selected user profile.</div>', unsafe_allow_html=True)

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
    st.markdown('</div>', unsafe_allow_html=True)