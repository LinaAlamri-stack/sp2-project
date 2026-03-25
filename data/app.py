import streamlit as st
from model import load_data, get_metrics
from view import setup_page, render_header, render_metrics, render_charts, render_footer

@st.cache_data(ttl=10)
def get_data():
    return load_data()

def main():
    setup_page()

    df = get_data()
    if df is None:
        st.error("No data found")
        return

    render_header()

    total, male, female = get_metrics(df)
    render_metrics(total, male, female)

    render_charts(df)

    render_footer()


if __name__ == "__main__":
    main()
