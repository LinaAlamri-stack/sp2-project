import base64
from datetime import date, datetime
from pathlib import Path

import streamlit as st

from database import get_user_by_id, init_db, update_user_profile


st.set_page_config(
    page_title="Profile | Riyalyze",
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
LOGO_IMAGE = _find_asset(["logoR", "logo"], SEARCH_DIRS)
logo_b64 = _b64(LOGO_IMAGE)

logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' alt='Riyalyze logo' class='logo-img'/>"
    if logo_b64
    else "<div class='logo-fallback'>R</div>"
)

st.markdown(
    """
    <style>
        :root {
            --bg: #0F123B;
            --accent: #A735D9;
            --text: #e8ecff;
            --muted: #9aa6d1;
            --field-bg: #0E1838;
            --field-text: #6E7488;
            --field-label: #92ADC9;
        }

        html, body, [class*="css"]  {
            font-family: 'SF Pro Text', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text);
            font-weight: 500;
            background-color: var(--bg);
        }

        a, a:hover, a:visited {
            color: inherit;
            text-decoration: none !important;
        }

        .stApp {
            background-color: var(--bg);
            min-height: 100vh;
        }

        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {
            display: none !important;
        }

        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        .dash {
            min-height: 100vh;
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 24px;
            padding: 48px 60px;
        }

        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: stretch;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 26px;
            letter-spacing: 0.6px;
        }

        .logo-img {
            width: 58px;
            height: 58px;
            object-fit: contain;
        }

        .logo-fallback {
            width: 58px;
            height: 58px;
            border-radius: 14px;
            background: linear-gradient(135deg, #c03bff 0%, #7b2bff 100%);
            display: grid;
            place-items: center;
            font-weight: 700;
        }

        .divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin-top: 4px;
        }

        .nav {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 14px 18px;
            border-radius: 22px;
            background: transparent;
            border: 1px solid transparent;
            box-shadow: none;
            backdrop-filter: none;
            cursor: pointer;
            transition: all 180ms ease;
            text-decoration: none;
        }

        .nav-item.active {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(12px);
        }

        .nav-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #351A62;
            display: grid;
            place-items: center;
            color: #fff;
            font-weight: 600;
        }

        .nav-item.active .nav-icon {
            background: #B628E2;
            color: #fff;
        }

        .nav-label {
            font-size: 18px;
            color: var(--text);
        }

        .content {
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 40px;
        }

        .profile-panel {
            width: min(560px, 70vw);
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .profile-head {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 8px;
        }

        .avatar {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #B628E2, #6E4CFF);
            display: grid;
            place-items: center;
            color: #fff;
            font-weight: 700;
        }

        .profile-name {
            font-size: 20px;
            color: #dbe6ff;
        }

        .profile-email {
            font-size: 14px;
            color: #92ADC9;
        }

        .field {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .field label {
            color: var(--field-label);
            font-size: 14px;
        }

        .field-box {
            background: var(--field-bg);
            color: var(--field-text);
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .section-sep {
            height: 14px;
        }

        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stDateInput"] {
            width: min(560px, 70vw);
            margin-bottom: 10px;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stDateInput"] label {
            color: var(--field-label);
            font-size: 14px;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stDateInput"] input {
            width: 100%;
            background: var(--field-bg);
            color: var(--field-text) !important;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            padding: 14px 16px;
            font-size: 15px;
        }

        div.stButton > button {
            min-width: min(560px, 70vw);
            padding: 14px 20px;
            border-radius: 14px;
            border: none;
            background: linear-gradient(135deg, #A735D9, #A735D9);
            color: #f8f2ff;
            font-weight: 500;
            font-size: 15px;
            box-shadow: 0 12px 30px rgba(167, 53, 217, 0.35);
            cursor: pointer;
            transition: transform 200ms ease, box-shadow 200ms ease, filter 200ms ease;
        }

        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 36px rgba(167, 53, 217, 0.45);
            filter: brightness(1.05);
        }

        @media (max-width: 980px) {
            .dash {
                grid-template-columns: 1fr;
            }

            .sidebar {
                order: -1;
            }

            .content {
                justify-content: flex-start;
                padding-top: 0;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

user_id = st.session_state.get("user_id")
user = get_user_by_id(user_id) if user_id else None

left_col, right_col = st.columns([0.32, 0.68], gap="large")
with left_col:
    st.markdown(
        f"""
        <div class="sidebar">
            <div class="brand">
                {logo_html}
                <span>Riyalyze</span>
            </div>
            <div class="divider"></div>
            <div class="nav">
                <a class="nav-item" href="/Dashboard">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 11.5L12 4L21 11.5V21H14.5V14.5H9.5V21H3V11.5Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Dashboard</div>
                </a>
                <a class="nav-item active" href="/Profile">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12ZM4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22H4Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Profile</div>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown('<div class="content">', unsafe_allow_html=True)
    st.markdown('<div class="profile-panel">', unsafe_allow_html=True)

    if not user:
        st.warning("Please log in to view your profile.")
    else:
        name = user.get("name") or ""
        email = user.get("email") or ""
        gender = user.get("gender") or "Female"
        weight = user.get("weight") or 0.0
        height = user.get("height") or 0.0
        birth_date = user.get("birth_date")
        parsed_birth = None
        if birth_date:
            try:
                parsed_birth = datetime.fromisoformat(birth_date).date()
            except ValueError:
                parsed_birth = None

        st.markdown(
            f"""
            <div class="profile-head">
                <div class="avatar">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12ZM4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22H4Z" fill="white"/>
                    </svg>
                </div>
                <div>
                    <div class="profile-name">{name}</div>
                    <div class="profile-email">{email}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("profile_form"):
            name_input = st.text_input("Full Name", value=name)
            gender_input = st.selectbox("Gender", ["Male", "Female"], index=0 if gender == "Male" else 1)
            birth_input = st.date_input("Birth Of Date", value=parsed_birth or date(2002, 11, 11))
            weight_input = st.number_input("Weight (kg)", min_value=0.0, step=0.1, value=float(weight))
            height_input = st.number_input("Height (cm)", min_value=0.0, step=0.1, value=float(height))

            submitted = st.form_submit_button("Save Changes")
            if submitted:
                update_user_profile(
                    user_id,
                    name_input,
                    gender_input,
                    weight_input,
                    height_input,
                    birth_input.isoformat() if birth_input else None,
                )
                st.success("Profile updated.")

        # Separator
        st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

        if parsed_birth:
            today = date.today()
            age = today.year - parsed_birth.year - (
                (today.month, today.day) < (parsed_birth.month, parsed_birth.day)
            )
        else:
            age = "-"

        st.markdown(
            f"""
            <div class="field">
                <label>Age</label>
                <div class="field-box">{age}</div>
            </div>
            <div class="field">
                <label>Email</label>
                <div class="field-box">{email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div></div>", unsafe_allow_html=True)
