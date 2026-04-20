import sqlite3
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


DB_PATH = Path(__file__).resolve().parent / "data" / "app.db"
SURVEY_CSV_PATH = Path(__file__).resolve().parent / "data" / "survey_data.csv"


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(color="#E8ECFF", size=16),
            )
        ],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def _read_sql(query: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn)
    except sqlite3.DatabaseError:
        return pd.DataFrame()


def _load_legacy_survey_df() -> pd.DataFrame:
    if not SURVEY_CSV_PATH.exists():
        return pd.DataFrame()

    lines = SURVEY_CSV_PATH.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    cleaned_lines = [
        line for line in lines if not line.startswith(("<<<<<<<", "=======", ">>>>>>>"))
    ]
    if not cleaned_lines:
        return pd.DataFrame()

    header_index = next(
        (i for i, line in enumerate(cleaned_lines) if line.startswith("Timestamp,")),
        None,
    )
    if header_index is None:
        return pd.DataFrame()

    csv_text = "\n".join(cleaned_lines[header_index:])
    df = pd.read_csv(StringIO(csv_text))
    df = df.dropna(how="all")
    if "Timestamp" in df.columns:
        df = df[df["Timestamp"].astype(str).str.lower() != "timestamp"]
    return df


def get_total_user_count() -> int:
    legacy_df = _load_legacy_survey_df()
    legacy_count = len(legacy_df.index) if not legacy_df.empty else 0

    db_df = _read_sql("SELECT COUNT(*) AS total FROM users")
    db_count = int(db_df.iloc[0]["total"]) if not db_df.empty else 0

    return legacy_count + db_count


def build_gender_fig() -> go.Figure:
    db_df = _read_sql(
        """
        SELECT gender
        FROM users
        WHERE gender IS NOT NULL AND TRIM(gender) != ''
        """
    )
    legacy_df = _load_legacy_survey_df()

    db_gender = (
        db_df["gender"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"female": "Female", "male": "Male"})
        .dropna()
        if not db_df.empty and "gender" in db_df.columns
        else pd.Series(dtype=str)
    )

    legacy_gender = (
        legacy_df["3. Gender"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"female": "Female", "male": "Male"})
        .dropna()
        if not legacy_df.empty and "3. Gender" in legacy_df.columns
        else pd.Series(dtype=str)
    )

    combined_gender = pd.concat([legacy_gender, db_gender], ignore_index=True)

    if combined_gender.empty:
        return _empty_figure("No gender data available yet")

    counts = combined_gender.value_counts().rename_axis("Gender").reset_index(name="Count")
    counts["Gender"] = pd.Categorical(counts["Gender"], categories=["Female", "Male"], ordered=True)
    counts = counts.sort_values("Gender")
    total = int(counts["Count"].sum())
    counts["Percent"] = (counts["Count"] / total * 100).round(1)
    counts["Label"] = counts.apply(
        lambda row: f"{int(row['Count'])} ({row['Percent']:.1f}%)",
        axis=1,
    )

    fig = px.bar(
        counts,
        x="Count",
        y="Gender",
        color="Gender",
        color_discrete_map={"Female": "#EC4899", "Male": "#3B82F6"},
        orientation="h",
        text="Label",
    )
    fig.update_traces(textposition="outside", textfont_size=14)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis_title="Users",
        yaxis_title="",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.10)", zeroline=False),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Users: %{x}<br>Percent: %{customdata[0]:.1f}%<extra></extra>",
        customdata=counts[["Percent"]].to_numpy(),
    )
    return fig


def build_caffeine_cups_fig() -> go.Figure:
    db_df = _read_sql(
        """
        SELECT caffeine_per_day
        FROM user_surveys
        WHERE caffeine_per_day IS NOT NULL
        """
    )
    legacy_df = _load_legacy_survey_df()

    db_labels = (
        db_df["caffeine_per_day"]
        .map({0: "0", 1: "1-2", 2: "1-2", 3: "3+"})
        .dropna()
        if not db_df.empty and "caffeine_per_day" in db_df.columns
        else pd.Series(dtype=str)
    )

    legacy_labels = (
        legacy_df["4. Number of caffeine drinks per day"]
        .astype(str)
        .str.strip()
        .replace(
            {
                "0": "0",
                "1-2": "1-2",
                "3-4": "3+",
                "more than 4": "3+",
                "5+": "3+",
            }
        )
        .dropna()
        if not legacy_df.empty and "4. Number of caffeine drinks per day" in legacy_df.columns
        else pd.Series(dtype=str)
    )

    labels = pd.concat([legacy_labels, db_labels], ignore_index=True)
    if labels.empty:
        return _empty_figure("No caffeine data available yet")

    order = ["0", "1-2", "3+"]
    counts = (
        labels.value_counts()
        .reindex(order, fill_value=0)
        .rename_axis("Cups")
        .reset_index(name="Users")
    )
    total = int(counts["Users"].sum())
    counts["Percent"] = (counts["Users"] / total * 100).round(1)
    counts["Label"] = counts.apply(
        lambda row: f"{int(row['Users'])} ({row['Percent']:.1f}%)",
        axis=1,
    )

    fig = px.bar(
        counts,
        x="Cups",
        y="Users",
        color="Cups",
        color_discrete_map={
            "0": "#94A3B8",
            "1-2": "#5EEAD4",
            "3+": "#EC4899",
        },
        template="plotly_dark",
        text="Label",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis_title="Cups Per Day",
        yaxis_title="Users",
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Users: %{y}<br>Percent: %{customdata[0]:.1f}%<extra></extra>",
        customdata=counts[["Percent"]].to_numpy(),
    )
    return fig


def build_risk_level_fig() -> go.Figure:
    risk_df = pd.DataFrame(
        {
            "Level": ["Low", "Moderate", "High"],
            "Percentage": [52, 32, 16],
        }
    )
    fig = px.bar(
        risk_df,
        x="Level",
        y="Percentage",
        color="Level",
        color_discrete_map={"Low": "#3B82F6", "Moderate": "#A855F7", "High": "#EC4899"},
        template="plotly_dark",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def build_caffeine_sleep_fig() -> go.Figure:
    months = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=[1.6, 1.8, 1.7, 1.9, 2.3, 2.4, 2.48],
            name="Caffeine",
            line=dict(color="#5EEAD4", width=3),
            mode="lines+markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=[7.2, 7.0, 6.5, 6.2, 5.9, 5.8, 5.4],
            name="Sleep",
            line=dict(color="#A855F7", width=3),
            mode="lines+markers",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig
