import base64
from pathlib import Path
from typing import Optional
import math

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

from database import get_user_by_id, get_user_survey, init_db, update_user_projection
from risk_charts import build_caffeine_sleep_fig, build_risk_level_fig

st.set_page_config(
    page_title="Dashboard | Riyalyze",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

PROJECT_DIR = Path(__file__).resolve().parents[1]
DESKTOP_RIYALYZE_DIR = Path.home() / "Desktop" / "Riyalyze"
ASSETS_DIR = PROJECT_DIR / "assets"


def _find_asset(names: list[str], directories: list[Path]) -> Optional[Path]:
    for directory in directories:
        for base in names:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = directory / f"{base}{ext}"
                if candidate.exists():
                    return candidate
    return None


def _b64(path: Optional[Path]) -> Optional[str]:
    if not path or not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("utf-8")


SEARCH_DIRS = [DESKTOP_RIYALYZE_DIR, ASSETS_DIR, PROJECT_DIR]

LOGO_IMAGE = _find_asset(["logoR", "logo"], SEARCH_DIRS)
BODY_GREEN = _find_asset(["body_green", "green_body", "projection_green"], SEARCH_DIRS)
BODY_BLUE = _find_asset(["body_blue", "blue_body", "projection_blue"], SEARCH_DIRS)
BODY_RED = _find_asset(["body_red", "red_body", "projection_red"], SEARCH_DIRS)

logo_b64 = _b64(LOGO_IMAGE)
body_green_b64 = _b64(BODY_GREEN)
body_blue_b64 = _b64(BODY_BLUE)
body_red_b64 = _b64(BODY_RED)

logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' alt='Riyalyze logo' class='logo-img'/>"
    if logo_b64
    else "<div class='logo-fallback'>R</div>"
)

params = st.query_params
uid_param = params.get("uid")
if isinstance(uid_param, list):
    uid_param = uid_param[0] if uid_param else None
if "user_id" not in st.session_state and uid_param and str(uid_param).isdigit():
    st.session_state.user_id = int(uid_param)

tab = params.get("tab")
if isinstance(tab, list):
    tab = tab[0] if tab else None
tab = (tab or "dashboard").lower()

risk_level = params.get("risk")
if isinstance(risk_level, list):
    risk_level = risk_level[0] if risk_level else None
risk_level = (risk_level or "moderate").lower()

is_dashboard = tab == "dashboard"
is_profile = tab == "profile"

user_id = st.session_state.get("user_id")
if user_id and not uid_param:
    params["uid"] = str(user_id)
user = get_user_by_id(user_id) if user_id else None
survey = get_user_survey(user_id) if user_id else None


def get_projection_content(level: str, cluster_text: str):
    if level == "low":
        return {
            "title": "Low Future Risk",
            "status": "Stable",
            "cluster": cluster_text,
            "message": "If you maintain your current habits, your projected lifestyle risk remains low over the next 10 years.",
            "recommendation": "Maintain your current sleep routine and continue your balanced habits.",
            "badge": "#39D98A",
            "image": body_green_b64,
        }
    elif level == "high":
        return {
            "title": "High Future Risk",
            "status": "High Concern",
            "cluster": cluster_text,
            "message": "If your current habits remain unchanged, your projected lifestyle pattern may move toward a higher long-term risk state.",
            "recommendation": "Reduce caffeine after 8 PM, lower screen exposure at night, and increase weekly physical activity.",
            "badge": "#FF4D6D",
            "image": body_red_b64,
        }
    else:
        return {
            "title": "Moderate Future Risk",
            "status": "Needs Improvement",
            "cluster": cluster_text,
            "message": "If your current habits remain unchanged, your projected lifestyle risk may gradually increase over time.",
            "recommendation": "Improve sleep consistency, reduce late-night eating, and lower screen exposure before bed.",
            "badge": "#081028",
            "image": body_blue_b64,
        }


# =========================
# USER DATA (PREFER DB, FALLBACK SESSION)
# =========================
user_caffeine = float((survey or {}).get("caffeine_per_day", st.session_state.get("caffeine_per_day", 2)))
user_sleep = float((survey or {}).get("sleep_hours", st.session_state.get("sleep_hours", 7)))
user_fast_food = float((survey or {}).get("fast_food_per_week", st.session_state.get("fast_food_per_week", 2)))
user_activity = float((survey or {}).get("physical_activity_days", st.session_state.get("physical_activity_days", 3)))
user_screen = float((survey or {}).get("screen_hours", st.session_state.get("screen_hours", 6)))
user_sleep_quality = float((survey or {}).get("sleep_quality", st.session_state.get("sleep_quality", 3)))
user_eat_late = float((survey or {}).get("eat_after_10pm", st.session_state.get("eat_after_10pm", 0)))
user_caffeine_late = float((survey or {}).get("caffeine_after_8pm", st.session_state.get("caffeine_after_8pm", 0)))
user_low_energy = float((survey or {}).get("low_energy_frequency", st.session_state.get("low_energy_frequency", 3)))

saved_risk_score = (survey or {}).get("risk_score")
if saved_risk_score is not None:
    risk_score = int(saved_risk_score)
else:
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
    risk_score = max(0, min(round(risk_score), 100))

saved_risk_level = (survey or {}).get("risk_level")
if saved_risk_level:
    final_risk_level = str(saved_risk_level).lower()
else:
    if risk_score <= 30:
        final_risk_level = "low"
    elif risk_score >= 60:
        final_risk_level = "high"
    else:
        final_risk_level = "moderate"

# =========================
# KPI DATA
# =========================
kpis = [
    {
        "label": "Your Caffeine Intake",
        "value": f"{user_caffeine:.1f}",
        "unit": "Cups/day",
        "icon": "☕",
        "pill_class": "green-pill",
    },
    {
        "label": "Your Sleep Hours",
        "value": f"{user_sleep:.1f}",
        "unit": "Hours/Night",
        "icon": "🌙",
        "pill_class": "blue-pill",
    },
    {
        "label": "Your Fast Food / Week",
        "value": f"{user_fast_food:.1f}",
        "unit": "Times/Week",
        "icon": "🍟",
        "pill_class": "yellow-pill",
    },
    {
        "label": "Your Risk Score",
        "value": str(risk_score),
        "unit": "Score",
        "icon": "✉️",
        "pill_class": "pink-pill",
    },
]

kpi_html = "".join(
    f"""
    <div class="kpi-card">
        <div class="kpi-header-row">
            <div class="kpi-title-wrap">
                <div class="kpi-mini-icon">{item['icon']}</div>
                <div class="kpi-title">{item['label']}</div>
            </div>
            <div class="kpi-dots">•••</div>
        </div>
        <div class="kpi-bottom-row">
            <div class="kpi-number">{item['value']}</div>
            <div class="kpi-pill {item['pill_class']}">{item['unit']}</div>
        </div>
    </div>
    """
    for item in kpis
)

user_name = (user or {}).get("name") or ""
survey_name = (survey or {}).get("full_name")
profile_name = (
    user_name
    if user_name and user_name.strip().lower() != "user"
    else (survey_name or user_name or "User")
)
profile_email = (user or {}).get("email") or "Not available"
profile_age = (user or {}).get("age") if (user or {}).get("age") is not None else (survey or {}).get("age")
profile_gender = (user or {}).get("gender") or "-"
profile_weight = (user or {}).get("weight")
profile_height = (user or {}).get("height")

def _fmt_value(value):
    return "-" if value is None or value == "" else str(value)

profile_html = f"""
<div class="profile-panel">
    <div class="profile-head">
        <div class="avatar">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12ZM4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22H4Z" fill="white"/>
            </svg>
        </div>
        <div>
            <div class="profile-name">{profile_name}</div>
            <div class="profile-email">{profile_email}</div>
        </div>
    </div>

    <div class="field">
        <label>Full Name</label>
        <div class="field-box">{profile_name}</div>
    </div>
    <div class="field">
        <label>Age</label>
        <div class="field-box">{_fmt_value(profile_age)}</div>
    </div>
    <div class="field">
        <label>Gender</label>
        <div class="field-box">{profile_gender}</div>
    </div>
    <div class="field">
        <label>Weight (kg)</label>
        <div class="field-box">{_fmt_value(profile_weight)}</div>
    </div>
    <div class="field">
        <label>Height (cm)</label>
        <div class="field-box">{_fmt_value(profile_height)}</div>
    </div>
</div>
"""

# =========================
# CLUSTER CHART DATA
# =========================
cluster_file = PROJECT_DIR / "data" / "clustering_results.csv"
cluster_html = ""
cluster_name_for_projection = (survey or {}).get("projection_cluster") or "Lifestyle Cluster"

if cluster_file.exists():
    cluster_data = pd.read_csv(cluster_file)

    feature_cols = [
        "caffeine_per_day",
        "fast_food_per_week",
        "sleep_hours",
        "physical_activity_days",
        "screen_hours",
        "sleep_quality",
        "eat_after_10pm",
        "caffeine_after_8pm",
        "low_energy_frequency",
    ]

    user_row = {
        "caffeine_per_day": user_caffeine,
        "fast_food_per_week": user_fast_food,
        "sleep_hours": user_sleep,
        "physical_activity_days": user_activity,
        "screen_hours": user_screen,
        "sleep_quality": user_sleep_quality,
        "eat_after_10pm": user_eat_late,
        "caffeine_after_8pm": user_caffeine_late,
        "low_energy_frequency": user_low_energy,
    }

    cluster_names = {
        0: "Cluster A",
        1: "Cluster B",
        2: "Cluster C",
    }

    cluster_centers = cluster_data.groupby("cluster")[feature_cols].mean()
    feature_means = cluster_data[feature_cols].mean()
    feature_stds = cluster_data[feature_cols].std().replace(0, 1)

    user_scaled = {
        col: (user_row[col] - feature_means[col]) / feature_stds[col]
        for col in feature_cols
    }

    centers_scaled = (cluster_centers - feature_means) / feature_stds

    distances = {}
    for cluster_id in centers_scaled.index:
        distance = 0
        for col in feature_cols:
            distance += (user_scaled[col] - centers_scaled.loc[cluster_id, col]) ** 2
        distances[cluster_id] = math.sqrt(distance)

    user_cluster = min(distances, key=distances.get)
    user_cluster_name = cluster_names.get(user_cluster, f"Cluster {user_cluster}")
    cluster_name_for_projection = user_cluster_name
    if user_id:
        update_user_projection(
            user_id,
            projection_cluster=cluster_name_for_projection,
            risk_score=risk_score,
            risk_level=final_risk_level,
        )

    cluster_summary = (
        cluster_data.groupby("cluster")
        .agg(
            caffeine_per_day=("caffeine_per_day", "mean"),
            screen_hours=("screen_hours", "mean"),
            user_count=("cluster", "size"),
        )
        .reset_index()
    )

    cluster_summary["cluster_name"] = cluster_summary["cluster"].map(cluster_names)
    cluster_summary["label"] = (
        cluster_summary["cluster_name"]
        + "<br>Users: "
        + cluster_summary["user_count"].astype(str)
    )

    fig = px.scatter(
        cluster_summary,
        x="caffeine_per_day",
        y="screen_hours",
        size="user_count",
        color="cluster_name",
        text="label",
        size_max=55,
        color_discrete_map={
            "Cluster A": "#d94db5",
            "Cluster B": "#2bb9e8",
            "Cluster C": "#8b5cf6",
        },
        hover_data={
            "caffeine_per_day": ":.2f",
            "screen_hours": ":.2f",
            "user_count": True,
            "cluster_name": False,
        },
    )

    fig.update_traces(
        textposition="middle center",
        marker=dict(
            line=dict(color="white", width=2),
            opacity=0.9,
        ),
        selector=dict(mode="markers"),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#151a55",
        plot_bgcolor="#151a55",
        font=dict(color="white", size=14),
        xaxis=dict(
            title="Average Caffeine Intake (cups/day)",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
        ),
        yaxis=dict(
            title="Average Screen Hours",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
        ),
        legend_title="",
        margin=dict(l=20, r=20, t=10, b=20),
        height=420,
    )

    chart_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")

    cluster_html = f"""
    <div class="cluster-wrap">
        <div class="cluster-title-row">
            <div class="cluster-main-title">Cluster Comparison Chart</div>
            <div class="cluster-user-group">You belong to: {user_cluster_name}</div>
        </div>
        <div class="cluster-chart-box">
            {chart_html}
        </div>
    </div>
    """
else:
    cluster_html = """
    <div class="cluster-wrap">
        <div class="cluster-title-row">
            <div class="cluster-main-title">Cluster Comparison Chart</div>
        </div>
        <div class="cluster-empty-state">
            clustering_results.csv not found inside the data folder.
        </div>
    </div>
    """

fig_risk = build_risk_level_fig()
fig_trend = build_caffeine_sleep_fig()

risk_html = pio.to_html(fig_risk, full_html=False, include_plotlyjs=False)
trend_html = pio.to_html(fig_trend, full_html=False, include_plotlyjs=False)

charts_html = f"""
<div class="survey-charts">
    <div class="chart-card">
        <div class="chart-title">Risk level distribution</div>
        <div class="chart-box">
            {risk_html}
        </div>
    </div>
    <div class="chart-card">
        <div class="chart-title">Caffeine vs Sleep Trends</div>
        <div class="chart-box">
            {trend_html}
        </div>
    </div>
</div>
"""

projection = get_projection_content(final_risk_level, cluster_name_for_projection)
projection_title = (survey or {}).get("projection_title") or projection["title"]
projection_status = (survey or {}).get("projection_status") or projection["status"]
projection_cluster = (survey or {}).get("projection_cluster") or projection["cluster"]

if user_id and (survey is not None):
    update_user_projection(
        user_id,
        risk_score=risk_score,
        risk_level=final_risk_level,
        projection_title=projection_title,
        projection_status=projection_status,
        projection_cluster=projection_cluster,
    )

projection_img_html = (
    f"<img src='data:image/png;base64,{projection['image']}' class='projection-body-img' alt='Projection body' />"
    if projection["image"]
    else "<div class='projection-body-fallback'>Body Image</div>"
)

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{
        box-sizing: border-box;
    }}

    html, body {{
        margin: 0;
        padding: 0;
        background: #0F123B;
        font-family: 'SF Pro Text', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #e8ecff;
        min-height: 100vh;
    }}

    body {{
        overflow-x: hidden;
    }}

    a {{
        color: inherit;
        text-decoration: none;
    }}

    .dash {{
        min-height: 100vh;
        display: grid;
        grid-template-columns: 320px 1fr;
        gap: 28px;
        padding: 42px 52px;
        background: #0F123B;
        align-items: start;
    }}

    .sidebar {{
        display: flex;
        flex-direction: column;
        gap: 24px;
    }}

    .brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 24px;
        letter-spacing: 0.4px;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    .logo-img {{
        width: 54px;
        height: 54px;
        object-fit: contain;
    }}

    .logo-fallback {{
        width: 54px;
        height: 54px;
        border-radius: 14px;
        background: linear-gradient(135deg, #c03bff 0%, #7b2bff 100%);
        display: grid;
        place-items: center;
        font-weight: 700;
    }}

    .divider {{
        height: 1px;
        background: rgba(255, 255, 255, 0.18);
        margin-top: 2px;
        margin-bottom: 8px;
    }}

    .nav {{
        display: flex;
        flex-direction: column;
        gap: 18px;
    }}

    .nav-item {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 14px 18px;
        border-radius: 24px;
        border: 1px solid transparent;
        transition: all 180ms ease;
    }}

    .nav-item.active {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.22);
        box-shadow: inset 0 0 18px rgba(255, 255, 255, 0.05);
    }}

    .nav-icon {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #351A62;
        display: grid;
        place-items: center;
        color: #fff;
        flex-shrink: 0;
    }}

    .nav-item.active .nav-icon {{
        background: #B628E2;
    }}

    .nav-label {{
        font-size: 16px;
        font-weight: 600;
    }}

    .projection-card {{
        width: 100%;
        max-width: 100%;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px;
        padding: 18px 16px;
        box-shadow: inset 0 0 16px rgba(255,255,255,0.03);
        margin-top: 6px;
    }}

    .projection-title {{
        font-size: 16px;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }}

    .projection-subtitle {{
        font-size: 11px;
        line-height: 1.4;
        color: #9aa6d1;
        margin-bottom: 12px;
    }}

    .projection-body-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 210px;
        margin: 8px 0 10px;
    }}

    .projection-body-img {{
        width: 100%;
        max-width: 120px;
        height: auto;
        object-fit: contain;
    }}

    .projection-body-fallback {{
        width: 110px;
        height: 170px;
        border-radius: 18px;
        background: rgba(255,255,255,0.06);
        display: grid;
        place-items: center;
        color: #9aa6d1;
        border: 1px dashed rgba(255,255,255,0.18);
        font-size: 12px;
    }}

    .risk-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: white;
        margin: 0 auto 12px;
        width: fit-content;
    }}

    .projection-mini {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}

    .mini-box {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px;
    }}

    .mini-label {{
        font-size: 10px;
        color: #9aa6d1;
        margin-bottom: 6px;
    }}

    .mini-value {{
        font-size: 13px;
        font-weight: 700;
        color: white;
        line-height: 1.35;
    }}

    .main-area {{
        padding-top: 36px;
        display: flex;
        flex-direction: column;
        gap: 18px;
    }}

    .main-area.profile-mode {{
        align-items: stretch;
    }}

    .profile-center {{
        display: flex;
        justify-content: center;
        width: 100%;
    }}

    .dashboard-header {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    .dashboard-title {{
        font-size: 28px;
        font-weight: 700;
        color: white;
    }}

    .dashboard-subtitle {{
        font-size: 14px;
        color: #9aa6d1;
    }}

    .profile-panel {{
        width: min(560px, 70vw);
        display: flex;
        flex-direction: column;
        gap: 18px;
        margin-top: 10px;
    }}

    .profile-head {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }}

    .avatar {{
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #B628E2, #6E4CFF);
        display: grid;
        place-items: center;
        color: #fff;
        font-weight: 700;
    }}

    .profile-name {{
        font-size: 20px;
        color: #dbe6ff;
    }}

    .profile-email {{
        font-size: 14px;
        color: #92ADC9;
    }}

    .field {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}

    .field label {{
        color: #92ADC9;
        font-size: 14px;
    }}

    .field-box {{
        background: #0E1838;
        color: #6E7488;
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin-top: 8px;
        margin-bottom: 18px;
    }}

    .kpi-card {{
        background: rgba(22, 33, 94, 0.92);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 14px 16px;
        min-height: 128px;
        box-shadow: inset 0 0 18px rgba(255,255,255,0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .kpi-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
    }}

    .kpi-title-wrap {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        min-width: 0;
    }}

    .kpi-mini-icon {{
        font-size: 14px;
        line-height: 1;
        flex-shrink: 0;
    }}

    .kpi-title {{
        font-size: 11px;
        color: #eef3ff;
        font-weight: 600;
        line-height: 1.2;
        white-space: nowrap;
        overflow: visible;
    }}

    .kpi-dots {{
        font-size: 13px;
        color: rgba(255,255,255,0.75);
        letter-spacing: 1px;
        flex-shrink: 0;
        margin-top: 1px;
    }}

    .kpi-bottom-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }}

    .kpi-number {{
        font-size: 18px;
        font-weight: 800;
        color: white;
        line-height: 1;
    }}

    .kpi-pill {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        line-height: 1;
    }}

    .green-pill {{
        background: #35c98b;
    }}

    .blue-pill {{
        background: #2f8fff;
    }}

    .yellow-pill {{
        background: #cfae59;
        color: #fff8e7;
    }}

    .pink-pill {{
        background: #8b6aa8;
    }}

    .cluster-wrap {{
        width: 100%;
        min-height: 520px;
        border-radius: 26px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.02);
        padding: 18px 18px 12px;
        overflow: hidden;
    }}

    .cluster-title-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }}

    .cluster-main-title {{
        font-size: 20px;
        font-weight: 700;
        color: white;
    }}

    .cluster-user-group {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: white;
        background: rgba(182, 40, 226, 0.22);
        border: 1px solid rgba(255,255,255,0.10);
    }}

    .cluster-chart-box {{
        width: 100%;
        height: 450px;
        border-radius: 20px;
        overflow: hidden;
        background: #151a55;
    }}

    .cluster-empty-state {{
        width: 100%;
        min-height: 420px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9aa6d1;
        font-size: 15px;
        text-align: center;
        padding: 20px;
    }}

    .survey-charts {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
        margin-top: 18px;
    }}

    .chart-card {{
        background: rgba(22, 33, 94, 0.92);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 16px;
        box-shadow: inset 0 0 18px rgba(255,255,255,0.03);
        min-height: 320px;
    }}

    .chart-title {{
        font-size: 16px;
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
    }}

    .chart-box {{
        width: 100%;
        height: 100%;
    }}

    @media (max-width: 1200px) {{
        .kpi-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}

    @media (max-width: 980px) {{
        .dash {{
            grid-template-columns: 1fr;
            padding: 28px 20px;
        }}

        .main-area {{
            padding-top: 0;
        }}

        .cluster-chart-box {{
            height: 420px;
        }}

        .survey-charts {{
            grid-template-columns: 1fr;
        }}
    }}

    @media (max-width: 640px) {{
        .kpi-grid {{
            grid-template-columns: 1fr;
        }}

        .kpi-title {{
            white-space: normal;
        }}

        .cluster-title-row {{
            align-items: flex-start;
        }}
    }}
</style>
</head>
<body>
    <div class="dash">
        <aside class="sidebar">
            <div class="brand">
                {logo_html}
                <span>Riyalyze</span>
            </div>

            <div class="divider"></div>

            <div class="nav">
                <a class="nav-item {'active' if is_dashboard else ''}" href="/Dashboard?tab=dashboard&risk={risk_level}&uid={user_id or ''}" target="_top">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 11.5L12 4L21 11.5V21H14.5V14.5H9.5V21H3V11.5Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Dashboard</div>
                </a>

                <a class="nav-item {'active' if is_profile else ''}" href="/Dashboard?tab=profile&risk={risk_level}&uid={user_id or ''}" target="_top">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12ZM4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22H4Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Profile</div>
                </a>
            </div>

            <div class="projection-card">
                <div class="projection-title">10-Year Projection</div>
                <div class="projection-subtitle">
                    Visual lifestyle projection based on current risk level
                </div>

                <div class="projection-body-wrap">
                    {projection_img_html}
                </div>

                <div class="risk-badge" style="background:{projection['badge']}">
                    {projection_title}
                </div>

                <div class="projection-mini">
                    <div class="mini-box">
                        <div class="mini-label">Projected Condition</div>
                        <div class="mini-value">{projection_status}</div>
                    </div>

                    <div class="mini-box">
                        <div class="mini-label">Current Pattern</div>
                        <div class="mini-value">{projection_cluster}</div>
                    </div>
                </div>
            </div>
        </aside>

        <main class="main-area {'profile-mode' if is_profile else ''}">
            <div class="dashboard-header">
                <div class="dashboard-title">
                    {"Dashboard" if is_dashboard else "Profile"}
                </div>
                <div class="dashboard-subtitle">
                    {"Your analytics overview will appear here." if is_dashboard else "Your personal information will appear here."}
                </div>
            </div>

            {"<div class='kpi-grid'>" + kpi_html + "</div>" + cluster_html + charts_html if is_dashboard else "<div class='profile-center'>" + profile_html + "</div>"}
        </main>
    </div>
</body>
</html>
"""

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0F123B !important;
}

.stApp {
    background-color: #0F123B !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0F123B !important;
}

.main {
    background-color: #0F123B !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

components.html(html, height=1650, scrolling=False)
