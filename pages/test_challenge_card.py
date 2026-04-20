import streamlit.components.v1 as components

html = """
<style>
.main-card {
    width: 100%;
    max-width: 620px;
    box-sizing: border-box;
    background: linear-gradient(145deg, #2f3cff, #1a237e);
    border-radius: 28px;
    padding: 28px;
    color: white;
    font-family: Arial;
    }


.user-card {
    background: rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;
}

.progress-wrap {
    width: 100%;
    height: 12px;
    background: #1a1f60;
    border-radius: 999px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    background: #c04cff;
}

.vs {
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}

.btn {
    display:block;
    margin-top:15px;
    padding:12px;
    text-align:center;
    background:#8b5cf6;
    color:white;
    border-radius:10px;
    text-decoration:none;
    font-weight:bold;
}

.link-btn {
    display: block;
    width: 100%;
    box-sizing: border-box;
    margin-top: 10px;
    padding: 14px 24px;
    border-radius: 16px;
    background: linear-gradient(90deg, #8b5cf6, #ec4899);
    color: white;
    text-decoration: none;
    font-weight: 700;
    text-align: center;
}
</style>

<div class="main-card">
    <h2>🔥 Challenge Match</h2>
    <p>Live progress between two users</p>

    <div class="user-card">Huda</div>
    <div class="progress-wrap">
        <div class="progress-fill" style="width:72%"></div>
    </div>
    <p>72% completed</p>

    <div class="vs">VS ⚔️</div>

    <div class="user-card">Sara</div>
    <div class="progress-wrap">
        <div class="progress-fill" style="width:58%"></div>
    </div>
    <p>58% completed</p>
if st.button("Start Challenge 🚀"):
    st.switch_page("pages/2_Challenge_Match.py")
"""

components.html(html, height=520)