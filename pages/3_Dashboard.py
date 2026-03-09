import base64
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Dashboard | Riyalyze",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

params = st.query_params
tab = params.get("tab")
if isinstance(tab, list):
    tab = tab[0] if tab else None
tab = (tab or "dashboard").lower()
is_dashboard = tab == "dashboard"
is_profile = tab == "profile"

st.markdown(
    f"""
    <style>
        :root {{
            --bg: #0F123B;
            --accent: #A735D9;
            --text: #e8ecff;
            --muted: #9aa6d1;
        }}

        html, body, [class*="css"]  {{
            font-family: 'SF Pro Text', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text);
            font-weight: 500;
            background-color: var(--bg);
        }}

        a, a:hover, a:visited {{
            color: inherit;
            text-decoration: none !important;
        }}

        .stApp {{
            background-color: var(--bg);
            min-height: 100vh;
        }}

        header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] {{
            display: none !important;
        }}

        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}

        .dash {{
            min-height: 100vh;
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 24px;
            padding: 48px 60px;
        }}

        .content {{
            min-height: 80vh;
        }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: stretch;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 26px;
            letter-spacing: 0.6px;
        }}

        .logo-img {{
            width: 58px;
            height: 58px;
            object-fit: contain;
        }}

        .logo-fallback {{
            width: 58px;
            height: 58px;
            border-radius: 14px;
            background: linear-gradient(135deg, #c03bff 0%, #7b2bff 100%);
            display: grid;
            place-items: center;
            font-weight: 700;
        }}

        .divider {{
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin-top: 4px;
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
            border-radius: 22px;
            background: transparent;
            border: 1px solid transparent;
            box-shadow: none;
            backdrop-filter: none;
            cursor: pointer;
            transition: all 180ms ease;
            text-decoration: none;
        }}

        .nav-item.active {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(12px);
        }}

        .nav-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #351A62;
            display: grid;
            place-items: center;
            color: #fff;
            font-weight: 600;
        }}

        .nav-item.active .nav-icon {{
            background: #B628E2;
            color: #fff;
        }}

        .nav-label {{
            font-size: 18px;
            color: var(--text);
        }}

        @media (max-width: 980px) {{
            .dash {{
                grid-template-columns: 1fr;
            }}

            .sidebar {{
                order: -1;
            }}
        }}
    </style>

    <div class="dash">
        <aside class="sidebar">
            <div class="brand">
                {logo_html}
                <span>Riyalyze</span>
            </div>
            <div class="divider"></div>
            <div class="nav">
                <a class="nav-item {'active' if is_dashboard else ''}" href="?tab=dashboard">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 11.5L12 4L21 11.5V21H14.5V14.5H9.5V21H3V11.5Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Dashboard</div>
                </a>
                <a class="nav-item {'active' if is_profile else ''}" href="?tab=profile">
                    <div class="nav-icon secondary">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12ZM4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22H4Z" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="nav-label">Profile</div>
                </a>
            </div>
        </aside>
        <main class="content"></main>
    </div>
    """,
    unsafe_allow_html=True,
)
