import base64
from pathlib import Path

import streamlit as st

from database import init_db, save_user_survey, update_user_basic, update_user_metrics

st.set_page_config(
    page_title="Riyalyze Lifestyle Assessment",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

params = st.query_params
uid_param = params.get("uid")
if isinstance(uid_param, list):
    uid_param = uid_param[0] if uid_param else None
if "user_id" not in st.session_state and uid_param and str(uid_param).isdigit():
    st.session_state.user_id = int(uid_param)

if "user_id" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

PROJECT_DIR = Path(__file__).resolve().parents[1]
DESKTOP_RIYALYZE_DIR = Path.home() / "Desktop" / "Riyalyze"
ASSETS_DIR = PROJECT_DIR / "assets"


def _find_asset(names: list[str], directories: list[Path]) -> Path | None:
    for directory in directories:
        for base in names:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = directory / f"{base}{ext}"
                if candidate.exists():
                    return candidate
    return None


def _b64(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("utf-8")


SEARCH_DIRS = [DESKTOP_RIYALYZE_DIR, ASSETS_DIR, PROJECT_DIR]
LOGO_IMAGE = _find_asset(["logoR", "logo"], SEARCH_DIRS)
logo_b64 = _b64(LOGO_IMAGE)

logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' alt='Riyalyze logo' class='logo-img'/>"
    if logo_b64
    else "<div class='logo-fallback'>R</div>"
)

QUESTIONS = [
    {
        "key": "full_name",
        "question": "What is your full name?",
        "type": "text",
        "placeholder": "Sara Suliman",
    },
    {
        "key": "age",
        "question": "How old are you?",
        "type": "number",
        "placeholder": "23",
    },
    {
        "key": "gender",
        "question": "What is your gender?",
        "options": ["Female", "Male"],
    },
    {
        "key": "weight",
        "question": "What is your weight (kg)?",
        "type": "float",
        "placeholder": "58",
    },
    {
        "key": "height",
        "question": "What is your height (cm)?",
        "type": "float",
        "placeholder": "160",
    },
    {
        "key": "sleep_hours",
        "question": "How many hours do you sleep per night?",
        "options": [str(i) for i in range(0, 13)],
    },
    {
        "key": "sleep_quality",
        "question": "How would you rate your sleep quality?",
        "options": ["Poor", "Average", "Good", "Excellent"],
    },
    {
        "key": "fast_food_per_week",
        "question": "How many times do you eat fast food per week?",
        "options": ["0", "1-2", "3-4", "5+"],
    },
    {
        "key": "caffeine_per_day",
        "question": "How many caffeinated drinks do you consume per day?",
        "options": ["0", "1", "2", "3+"],
    },
    {
        "key": "caffeine_after_8pm",
        "question": "Do you consume caffeine after 8 PM?",
        "options": ["Yes", "No"],
    },
    {
        "key": "eat_after_10pm",
        "question": "Do you usually eat after 10 PM?",
        "options": ["Yes", "No"],
    },
    {
        "key": "physical_activity_days",
        "question": "How many days per week do you do physical activity?",
        "options": [str(i) for i in range(0, 8)],
    },
    {
        "key": "screen_hours",
        "question": "How many hours do you spend on screens daily?",
        "options": [str(i) for i in range(0, 17)],
    },
    {
        "key": "low_energy_frequency",
        "question": "How often do you feel low energy during the day?",
        "options": ["Rarely", "Sometimes", "Often", "Always"],
    },
]

TOTAL = len(QUESTIONS)

if "survey_step" not in st.session_state:
    st.session_state.survey_step = 0
if "survey_answers" not in st.session_state:
    st.session_state.survey_answers = {}

if "step" in params:
    try:
        st.session_state.survey_step = max(
            0, min(int(params.get("step", 0)), TOTAL - 1)
        )
    except ValueError:
        st.session_state.survey_step = 0
    params.pop("step", None)

step = st.session_state.survey_step
question = QUESTIONS[step]

st.markdown(
    f"""
    <style>
        :root {{
            --bg: #0F123B;
            --accent: #A735D9;
            --text: #e8ecff;
            --muted: #9aa6d1;
            --option-bg: #d8dce3;
            --option-text: #0e1838;
        }}

        html, body, [class*="css"]  {{
            font-family: 'SF Pro Text', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: var(--bg);
            color: var(--text);
        }}

        .stApp {{
            background-color: var(--bg);
        }}

        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .block-container {{
            padding: 24px 6vw 40px !important;
            max-width: 100% !important;
        }}

        .top-bar {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            margin-bottom: 0;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 22px;
            font-weight: 600;
            letter-spacing: 0.4px;
        }}

        .logo-img {{
            width: 46px;
            height: 46px;
            object-fit: contain;
        }}

        .logo-fallback {{
            width: 46px;
            height: 46px;
            border-radius: 12px;
            background: linear-gradient(135deg, #c03bff 0%, #7b2bff 100%);
            display: grid;
            place-items: center;
            font-weight: 700;
        }}

        .back-btn {{
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.2);
            display: grid;
            place-items: center;
            color: #fff;
            font-size: 20px;
            background: rgba(255,255,255,0.05);
            text-decoration: none !important;
        }}

        .progress-wrap {{
            display: flex;
            justify-content: center;
            margin: 10px 0 30px;
        }}

        .progress {{
            display: flex;
            gap: 16px;
            padding: 16px 30px;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            min-width: min(620px, 88vw);
            justify-content: center;
        }}

        .step {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-size: 14px;
            color: #cdd4ff;
            background: transparent;
            border: 1px solid transparent;
        }}

        .step.active {{
            color: #fff;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.4);
        }}

        .question {{
            font-size: 30px;
            font-weight: 700;
            margin-top: 0;
            text-align: center;
            max-width: min(620px, 88vw);
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 10px;
        }}

        div[data-testid="stButton"] {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }}

        div[data-testid="stButton"] button {{
            width: min(620px, 88vw);
            margin-left: auto;
            margin-right: auto;
            border-radius: 999px;
            padding: 16px 22px;
            background: var(--option-bg);
            color: var(--option-text);
            font-weight: 600;
            font-size: 15px;
            border: none;
            text-align: center;
            margin-top: 0;
        }}

        div[data-testid="stButton"] button:hover {{
            filter: brightness(0.97);
        }}

        button[kind="primary"] {{
            width: min(360px, 70vw) !important;
            background: var(--accent) !important;
            color: white !important;
            font-weight: 600;
            margin: 0 auto;
            display: block;
        }}

        .bottom-brand {{
            margin-top: 36px;
            display: flex;
            justify-content: center;
        }}

        @media (max-width: 720px) {{
            .question {{
                font-size: 24px;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

progress_html = "".join(
    f"<div class='step {'active' if i == step else ''}'>{i + 1}</div>"
    for i in range(TOTAL)
)

st.markdown(
    f"""
    <div class="top-bar">
        {f"<a class='back-btn' href='?step={step-1}'>←</a>" if step > 0 else ""}
    </div>
    <div class="progress-wrap">
        <div class="progress">{progress_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, center_col, right_col = st.columns([1, 2, 1], gap="large")
with center_col:
    st.markdown("<div class='center-col'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='question'>{question['question']}</div>",
        unsafe_allow_html=True,
    )
    if question.get("type") == "text":
        name_val = st.text_input(
            "",
            key=f"ans_{question['key']}",
            placeholder=question.get("placeholder", ""),
        )
        if st.button("Continue"):
            if not name_val.strip():
                st.error("Please enter your name.")
            else:
                st.session_state.survey_answers[question["key"]] = name_val.strip()
                if step < TOTAL - 1:
                    st.session_state.survey_step = step + 1
                    st.rerun()
    elif question.get("type") == "number":
        age_val = st.text_input(
            "",
            key=f"ans_{question['key']}",
            placeholder=question.get("placeholder", ""),
        )
        if st.button("Continue"):
            if not age_val.isdigit():
                st.error("Please enter a valid age.")
            else:
                age_int = int(age_val)
                st.session_state.survey_answers[question["key"]] = age_int
                if step < TOTAL - 1:
                    st.session_state.survey_step = step + 1
                    st.rerun()
    elif question.get("type") == "float":
        float_val = st.text_input(
            "",
            key=f"ans_{question['key']}",
            placeholder=question.get("placeholder", ""),
        )
        if st.button("Continue"):
            try:
                float_num = float(float_val)
            except ValueError:
                st.error("Please enter a valid number.")
            else:
                if float_num <= 0:
                    st.error("Please enter a valid number.")
                else:
                    st.session_state.survey_answers[question["key"]] = float_num
                    if step < TOTAL - 1:
                        st.session_state.survey_step = step + 1
                        st.rerun()
    else:
        for idx, option in enumerate(question["options"]):
            if st.button(option, key=f"opt_{step}_{idx}"):
                st.session_state.survey_answers[question["key"]] = option
                if step < TOTAL - 1:
                    st.session_state.survey_step = step + 1
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="bottom-brand">
        <div class="brand">{logo_html}<span>Riyalyze</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if step == TOTAL - 1:
    with center_col:
        submitted = st.button("Submit", type="primary")
        if submitted:
            answers = st.session_state.survey_answers
            if len(answers) != TOTAL:
                st.error("Please answer all questions before submitting.")
            else:
                sleep_quality_map = {"Poor": 0, "Average": 1, "Good": 2, "Excellent": 3}
                fast_food_map = {"0": 0, "1-2": 1, "3-4": 2, "5+": 3}
                caffeine_per_day_map = {"0": 0, "1": 1, "2": 2, "3+": 3}
                yes_no_map = {"Yes": 1, "No": 0}
                low_energy_map = {"Rarely": 0, "Sometimes": 1, "Often": 2, "Always": 3}

                user_input = {
                    "full_name": answers.get("full_name"),
                    "age": answers.get("age"),
                    "caffeine_per_day": caffeine_per_day_map[answers["caffeine_per_day"]],
                    "fast_food_per_week": fast_food_map[answers["fast_food_per_week"]],
                    "sleep_hours": int(answers["sleep_hours"]),
                    "physical_activity_days": int(answers["physical_activity_days"]),
                    "screen_hours": int(answers["screen_hours"]),
                    "sleep_quality": sleep_quality_map[answers["sleep_quality"]],
                    "eat_after_10pm": yes_no_map[answers["eat_after_10pm"]],
                    "caffeine_after_8pm": yes_no_map[answers["caffeine_after_8pm"]],
                    "low_energy_frequency": low_energy_map[answers["low_energy_frequency"]],
                }

                risk_score = (
                    user_input["caffeine_per_day"] * 4
                    + user_input["fast_food_per_week"] * 3
                    + user_input["screen_hours"] * 3
                    + max(0, 8 - user_input["sleep_hours"]) * 4
                    + (5 - user_input["sleep_quality"]) * 5
                    + user_input["eat_after_10pm"] * 8
                    + user_input["caffeine_after_8pm"] * 8
                    + (user_input["low_energy_frequency"] - 1) * 4
                    - user_input["physical_activity_days"] * 3
                )
                risk_score = max(0, min(int(round(risk_score)), 100))

                if risk_score <= 30:
                    risk_level = "low"
                    projection_title = "Low Future Risk"
                    projection_status = "Stable"
                elif risk_score >= 60:
                    risk_level = "high"
                    projection_title = "High Future Risk"
                    projection_status = "High Concern"
                else:
                    risk_level = "moderate"
                    projection_title = "Moderate Future Risk"
                    projection_status = "Needs Improvement"

                user_input.update(
                    {
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "projection_title": projection_title,
                        "projection_status": projection_status,
                        "projection_cluster": "Lifestyle Cluster",
                    }
                )

                update_user_basic(
                    st.session_state["user_id"],
                    answers.get("full_name", "User"),
                    answers.get("age"),
                )
                update_user_metrics(
                    st.session_state["user_id"],
                    gender=answers.get("gender"),
                    weight=answers.get("weight"),
                    height=answers.get("height"),
                )
                save_user_survey(st.session_state["user_id"], user_input)
                st.success("Assessment submitted successfully!")
                st.switch_page("pages/3_Dashboard.py")

st.markdown("</div>", unsafe_allow_html=True)
