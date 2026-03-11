import base64
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Dashboard | Riyalyze",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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


def get_projection_content(level: str):
    if level == "low":
        return {
            "title": "Low Future Risk",
            "status": "Stable",
            "cluster": "Balanced Lifestyle",
            "message": "If you maintain your current habits, your projected lifestyle risk remains low over the next 10 years.",
            "recommendation": "Maintain your current sleep routine and continue your balanced habits.",
            "badge": "#39D98A",
            "image": body_green_b64,
        }
    elif level == "high":
        return {
            "title": "High Future Risk",
            "status": "High Concern",
            "cluster": "High Caffeine / Late Habits",
            "message": "If your current habits remain unchanged, your projected lifestyle pattern may move toward a higher long-term risk state.",
            "recommendation": "Reduce caffeine after 8 PM, lower screen exposure at night, and increase weekly physical activity.",
            "badge": "#FF4D6D",
            "image": body_red_b64,
        }
    else:
        return {
            "title": "Moderate Future Risk",
            "status": "Needs Improvement",
            "cluster": "High Screen Time Lifestyle",
            "message": "If your current habits remain unchanged, your projected lifestyle risk may gradually increase over time.",
            "recommendation": "Improve sleep consistency, reduce late-night eating, and lower screen exposure before bed.",
            "badge": "#4DA8FF",
            "image": body_blue_b64,
        }


projection = get_projection_content(risk_level)

projection_img_html = (
    f"<img src='data:image/png;base64,{projection['image']}' class='projection-body-img' alt='Projection body' />"
    if projection["image"]
    else "<div class='projection-body-fallback'>Body Image</div>"
)

dashboard_href = f"?tab=dashboard&risk={risk_level}"
profile_href = f"?tab=profile&risk={risk_level}"



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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #e8ecff;
    }}

    body {{
        min-height: 100vh;
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
        padding: 38px 46px 34px;
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
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px;
        padding: 18px 16px;
        box-shadow: inset 0 0 16px rgba(255,255,255,0.03);
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
        padding-top: 2px;
        display: flex;
        flex-direction: column;
        gap: 18px;
        min-width: 0;
    }}

    .dashboard-header {{
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 6px;
    }}

    .dashboard-title {{
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin: 0;
    }}

    .dashboard-subtitle {{
        font-size: 14px;
        color: #9aa6d1;
        margin: 0;
    }}

    .placeholder {{
        min-height: 720px;
        border-radius: 26px;
        border: 1px dashed rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.02);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #7f89b8;
        font-size: 16px;
        text-align: center;
        padding: 20px;
        width: 100%;
    }}

    @media (max-width: 1200px) {{
        .dash {{
            grid-template-columns: 300px 1fr;
            gap: 22px;
            padding: 30px 28px;
        }}
    }}

    @media (max-width: 980px) {{
        .dash {{
            grid-template-columns: 1fr;
            padding: 24px 18px;
        }}

        .main-area {{
            padding-top: 0;
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
                <a class="nav-item {'active' if is_dashboard else ''}" href="{dashboard_href}" target="_top">
                    <div class="nav-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 11.5L12 4L21 11.5V21H14.5V14.5H9.5V21H3V11.5Z" fill="white"/>
                        </svg>
                    </div>
                    <div class="nav-label">Dashboard</div>
                </a>

                <a class="nav-item {'active' if is_profile else ''}" href="{profile_href}" target="_top">
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
                    {projection['title']}
                </div>

                <div class="projection-mini">
                    <div class="mini-box">
                        <div class="mini-label">Projected Condition</div>
                        <div class="mini-value">{projection['status']}</div>
                    </div>

                    <div class="mini-box">
                        <div class="mini-label">Current Pattern</div>
                        <div class="mini-value">{projection['cluster']}</div>
                    </div>
                </div>
            </div>
        </aside>

        <section class="main-area">
            <div class="dashboard-header">
                <h1 class="dashboard-title">{'Dashboard' if is_dashboard else 'Profile'}</h1>
                <p class="dashboard-subtitle">
                    {'Your health behavior dashboard overview' if is_dashboard else 'User profile overview'}
                </p>
            </div>

            
        </section>
    </div>
</body>
</html>
"""

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp, .main {
    background-color: #0F123B !important;
}

header, footer {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

iframe {
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

components.html(html, height=980, scrolling=False)