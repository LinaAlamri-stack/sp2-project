import base64
from pathlib import Path
import streamlit as st
from database import update_password

st.set_page_config(
    page_title="Reset Password | Riyalyze",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DESKTOP_RIYALYZE_DIR = Path.home() / "Desktop" / "Riyalyze"
ASSETS_DIR = PROJECT_DIR / "assets"


def _find_asset(names, directories):
    for directory in directories:
        for base in names:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = directory / f"{base}{ext}"
                if candidate.exists():
                    return candidate
    return None


def _b64(path):
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
    f"<img src='data:image/png;base64,{logo_b64}' class='logo-img'>"
    if logo_b64
    else "<div class='logo-fallback'>R</div>"
)

st.markdown(
    f"""
<style>
:root {{
    --bg:#0F123B;
    --accent:#A735D9;
    --text:#e8ecff;
    --muted:#9aa6d1;
}}

html, body, [class*="css"] {{
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', sans-serif;
}}

.stApp {{
    {hero_css}
    background-color: var(--bg);
    background-size: 58% auto;
    background-position: left 6% center;
    background-repeat: no-repeat;
    min-height:100vh;
}}

header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {{
    display:none !important;
}}

.block-container {{
    padding:0 !important;
    max-width:100% !important;
}}

div[data-testid="stHorizontalBlock"] {{
    min-height:100vh;
    align-items:center;
    padding:80px 10vw;
    
}}
div[data-testid="stTextInput"] label {{
    color: white !important;
    font-weight: 500;
}}
.left {{
    display:flex;
    flex-direction:column;
    gap:24px;
}}

.brand {{
    display:flex;
    align-items:center;
    gap:12px;
    font-size:26px;
    color:white !important;
    animation: logoEntrance 1s ease-out;
}}

.logo-img {{
    width:54px;
    height:54px;
}}

.logo-fallback {{
    width:54px;
    height:54px;
    border-radius:14px;
    background:linear-gradient(135deg,#c03bff,#7b2bff);
    display:grid;
    place-items:center;
    font-weight:700;
}}

.project-name {{
    font-size:32px;
    letter-spacing:0.14em;
    text-transform:uppercase;
}}

.hero-title {{
    font-size:48px;
    font-weight:700;
}}

.form-note {{
    color:var(--muted);
    margin-bottom:10px;
}}

div[data-testid="stTextInput"] {{
    width:min(480px,80vw);
    margin-bottom:12px;
}}

div[data-testid="stTextInput"] input {{
    background:rgba(16,25,53,.7);
    border:1px solid rgba(167,53,217,.25);
    border-radius:16px;
    padding:16px;
    color:white;
}}

div.stButton > button {{
    width:min(520px,82vw);
    padding:16px 28px;
    border:none;
    border-radius:16px;
    background:linear-gradient(135deg,#A735D9,#B63FE8);
    color:white;
    font-size:16px;
    font-weight:600;
    box-shadow:0 12px 30px rgba(167,53,217,.35);
    margin-top:8px;
}}

div.stButton > button:hover {{
    filter:brightness(1.05);
}}

.auth-link-wrap {{
    width:min(480px,80vw);
    text-align:right;
    margin-top:12px;
}}

.auth-link,
.auth-link:visited,
.auth-link:active,
.auth-link:focus {{
    color:#A735D9;
    text-decoration:none !important;
    border-bottom:none !important;
    box-shadow:none !important;
    font-weight:600;
    font-size:14px;
}}

.auth-link:hover {{
    color:#A735D9;
    text-decoration:none !important;
    border-bottom:none !important;
    box-shadow:none !important;
}}

.footer {{
    position:fixed;
    bottom:24px;
    right:10vw;
    color:var(--muted);
    font-size:13px;
    display:flex;
    gap:24px;
}}
@keyframes logoEntrance {{
    0% {{
        opacity:0;
        transform: translateY(25px);
    }}

    100% {{
        opacity:1;
        transform: translateY(0);
    }}
}}
</style>
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
    <div class="project-name">Dietary Habits Dashboard</div>
</div>
""",
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        '<h1 class="hero-title">Reset Password</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="form-note">Enter your email and create a new password.</p>',
        unsafe_allow_html=True
    )

    email = st.text_input("Email")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Reset Password"):
        if not email or not new_password or not confirm_password:
            st.warning("Please fill all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            updated = update_password(email, new_password)
            if updated:
                st.success("Password updated successfully.")
            else:
                st.error("Email not found.")

    st.markdown(
        """
        <div class="auth-link-wrap">
            <a href="/Login" target="_self" class="auth-link">Back to Log In</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="footer">
    <span>© 2026, Made by Riyalyze Team</span>
</div>
""",
    unsafe_allow_html=True,
)
