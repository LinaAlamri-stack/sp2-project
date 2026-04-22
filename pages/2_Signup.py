import base64
from pathlib import Path

import streamlit as st

from database import create_user, init_db


st.set_page_config(
    page_title="Sign Up | Riyalyze",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

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

HERO_IMAGE = _find_asset(["backgraound", "background"], SEARCH_DIRS)
LOGO_IMAGE = _find_asset(["logoR", "logo"], SEARCH_DIRS)

hero_b64 = _b64(HERO_IMAGE)
logo_b64 = _b64(LOGO_IMAGE)

hero_css = (
    f"background-image: url('data:image/png;base64,{hero_b64}');"
    if hero_b64
    else "background-image: none;"
)

logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' alt='Riyalyze logo' class='logo-img'/>"
    if logo_b64
    else "<div class='logo-fallback'>R</div>"
)

if "signup_step" not in st.session_state:
    st.session_state.signup_step = "email"

st.markdown(
    f"""
    <style>
        :root {{
            --bg: #0F123B;
            --bg-2: #090D2E;
            --accent: #A735D9;
            --accent-2: #A735D9;
            --text: #e8ecff;
            --muted: #9aa6d1;
        }}

        html, body, [class*="css"]  {{
            font-family: 'SF Pro Text', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text);
            font-weight: 500;
            background-color: #0F123B;
        }}

        a, a:hover, a:visited {{
            text-decoration: none !important;
        }}

        .stApp {{
            {hero_css}
            background-color: #0F123B;
            background-size: 58% auto;
            background-position: left 6% center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            min-height: 100vh;
        }}

        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        .hero {{
            min-height: 100vh;
            display: grid;
            grid-template-columns: minmax(320px, 1.2fr) minmax(320px, 1fr);
            gap: 24px;
            align-items: center;
            padding: 80px 10vw 60px;
        }}

        .left {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: flex-start;
            animation: fadeUp 900ms ease-out both;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 26px;
            letter-spacing: 0.8px;
            color: var(--text);
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

        .project-name {{
            font-size: clamp(22px, 3vw, 32px);
            letter-spacing: 0.16em;
            text-transform: uppercase;
            white-space: nowrap;
        }}

        .right {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 18px;
            animation: fadeUp 900ms ease-out both;
            animation-delay: 120ms;
        }}

        .hero-title {{
            font-size: clamp(30px, 4.2vw, 48px);
            font-weight: 600;
            margin: 0 0 6px;
        }}

        .form-note {{
            color: var(--muted);
            margin: 0 0 6px;
        }}

        div[data-testid="stHorizontalBlock"] {{
            align-items: center;
            min-height: 100vh;
            padding: 80px 10vw 60px;
            gap: 24px;
        }}

        div[data-testid="column"]:first-of-type {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        div[data-testid="column"]:nth-of-type(2) {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            gap: 16px;
        }}

        div[data-testid="column"]:nth-of-type(2) > div {{
            width: 100%;
        }}

        div[data-testid="stTextInput"] {{
            width: min(480px, 80vw);
            margin-bottom: 12px;
        }}

        div[data-testid="stTextInput"] label {{
            font-size: 14px;
            color: #d6dcff;
            letter-spacing: 0.04em;
        }}

        div[data-testid="stTextInput"] input {{
            width: 100%;
            background: rgba(16, 25, 53, 0.7);
            border: 1px solid rgba(167, 53, 217, 0.25);
            border-radius: 16px;
            padding: 16px 18px;
            color: var(--text);
            font-size: 15px;
            outline: none;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        }}

        div[data-testid="stTextInput"] input::placeholder {{
            color: rgba(232, 236, 255, 0.45);
        }}

        div.stButton > button {{
            width: min(520px, 82vw);
            padding: 16px 28px;
            border-radius: 16px;
            border: none;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #f8f2ff;
            font-weight: 500;
            font-size: 16px;
            box-shadow: 0 12px 30px rgba(167, 53, 217, 0.35);
            cursor: pointer;
            transition: transform 200ms ease, box-shadow 200ms ease, filter 200ms ease;
        }}

        div.stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 18px 36px rgba(167, 53, 217, 0.45);
            filter: brightness(1.05);
        }}

        .footer {{
            position: fixed;
            bottom: 24px;
            right: 10vw;
            color: var(--muted);
            font-size: 13px;
            letter-spacing: 0.08em;
            display: flex;
            gap: 24px;
        }}

        .footer a {{
            color: var(--muted);
            text-decoration: none;
        }}

        @keyframes fadeUp {{
            0% {{ opacity: 0; transform: translateY(16px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 980px) {{
            .hero {{
                grid-template-columns: 1fr;
                padding: 70px 8vw 80px;
                text-align: center;
            }}

            .right {{
                align-items: center;
            }}

            .footer {{
                position: static;
                margin-top: 32px;
                justify-content: center;
            }}
        }}
    </style>

    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.2, 1], gap="large")
with left_col:
    st.markdown(
        f"""
        <div class="left">
            <div class="brand">
                {logo_html}
                <span>Riyalyze</span>
            </div>
            <div class="project-name">Dietary Habits DASHBOARD</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
    """
    <div style="margin-bottom:10px;">
        <a href="/"
        target="_self"
        style="
            color:white;
            text-decoration:none;
            font-size:24px;
            font-weight:bold;
        ">
            ←
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
    st.markdown('<h1 class="hero-title">Nice to see you!</h1>', unsafe_allow_html=True)
    if st.session_state.signup_step == "email":
        st.markdown(
            '<p class="form-note">Enter your Email to Sign Up</p>',
            unsafe_allow_html=True,
        )
        email = st.text_input("Email", placeholder="Sara@example.com")
        if st.button("Continue", key="signup_continue"):
            if not email or "@" not in email:
                st.warning("Please enter a valid email.")
            else:
                st.session_state.signup_step = "password"
                st.session_state.signup_email = email
                st.rerun()
    else:
        st.markdown('<p class="form-note">Create your password</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up", key="signup_submit"):
            email = st.session_state.get("signup_email", "")
            if not password or len(password) < 6:
                st.warning("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                name_guess = email.split("@")[0].replace(".", " ").title() if email else "User"
                user_id = create_user(name_guess, email, password)

                if user_id is None:
                 st.error("Email already exists. Please use another email.")
                else:
                 st.session_state.user_id = user_id
                 st.session_state.user_email = email

                st.success("Account created successfully.")
                st.switch_page("pages/5_survey.py")
with right_col:
 st.markdown(
    """
    <div class="footer">
        <span>© 2026, Made by Riyalyze Team</span>
        <a href="/">Github</a>
        <a href="/">License</a>
    </div>
    """,
    unsafe_allow_html=True,
)
