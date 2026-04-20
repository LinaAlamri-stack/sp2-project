import base64
from pathlib import Path
from typing import Optional

import streamlit as st


st.set_page_config(
    page_title="Riyalyze | Dietary Habits Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

params = st.query_params
page = params.get("page")
if isinstance(page, list):
    page = page[0] if page else None
page = (page or "").strip().lower()
if page in {"login", "1_login"}:
    st.switch_page("pages/1_Login.py")
if page in {"signup", "sign-up", "2_signup"}:
    st.switch_page("pages/2_Signup.py")


PROJECT_DIR = Path(__file__).parent
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
            gap: 22px;
            animation: fadeUp 900ms ease-out both;
            animation-delay: 120ms;
        }}

        .right h1 {{
            font-size: clamp(30px, 4.2vw, 48px);
            font-weight: 600;
            margin: 0;
        }}

        .cta {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 320px;
            padding: 14px 28px;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #f8f2ff;
            text-decoration: none;
            font-weight: 500;
            box-shadow: 0 12px 30px rgba(167, 53, 217, 0.35);
            transition: transform 200ms ease, box-shadow 200ms ease;
            animation: fadeUp 900ms ease-out both;
        }}

        .cta .cta-text {{
            color: #ffffff;
            font-size: 18px;
        }}

        .cta .cta-action {{
            color: #101935;
            font-weight: 600;
            margin-left: 6px;
        }}


        .cta:nth-of-type(1) {{
            animation-delay: 220ms;
        }}

        .cta:nth-of-type(2) {{
            animation-delay: 320ms;
        }}

        .cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 18px 36px rgba(161, 66, 244, 0.45);
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

    <div class="hero">
        <div class="left">
            <div class="brand">
                {logo_html}
                <span>Riyalyze</span>
            </div>
            <div class="project-name">Dietary Habits DASHBOARD</div>
        </div>
        <div class="right">
            <h1>Nice to see you!</h1>
            <a class="cta" href="/?page=login"><span class="cta-text">Already have an account?</span><span class="cta-action">Log In</span></a>
            <a class="cta" href="/?page=signup"><span class="cta-text">New here?</span><span class="cta-action">Sign Up</span></a>
        </div>
    </div>
    <div class="footer">
        <span>© 2026, Made by Riyalyze Team</span>
        <a href="#">Github</a>
        <a href="#">License</a>
    </div>
    """,
    unsafe_allow_html=True,
)
