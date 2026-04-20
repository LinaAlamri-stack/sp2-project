import base64
from pathlib import Path

import streamlit as st

from risk_charts import build_caffeine_cups_fig, build_gender_fig

st.set_page_config(page_title="RiskLevelCaffeineSleep | Riyalyze", layout="wide")

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
    f"""
    <style>
        :root {{
            --bg: #0F123B;
            --text: #e8ecff;
            --muted: #9aa6d1;
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
            padding: 32px 6vw 48px !important;
            max-width: 100% !important;
        }}

        .page-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 14px;
        }}

        .logo-img {{
            width: 44px;
            height: 44px;
            object-fit: contain;
        }}

        .logo-fallback {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: linear-gradient(135deg, #c03bff 0%, #7b2bff 100%);
            display: grid;
            place-items: center;
            font-weight: 700;
        }}

        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin: 12px 0 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="page-title">
        {logo_html}
        <span>Riyalyze</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## User Survey Results")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Gender Distribution")
    fig_gender = build_gender_fig()
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.markdown("### Daily Cups Consumption")
    fig_cups = build_caffeine_cups_fig()
    st.plotly_chart(fig_cups, use_container_width=True)
