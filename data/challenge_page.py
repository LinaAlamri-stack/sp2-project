import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Riyalyze", layout="wide")

# =========================
# CSS 
# =========================
st.markdown("""
<style>

body {
    background-color: #0F172A;
}

.main {
    background-color: #0F172A;
}

/* Titles */
.title {
    font-size: 40px;
    font-weight: 800;
    color: white;
        text-align: center;

}

.subtitle {
    color: #94A3B8;
    margin-bottom: 25px;
        text-align: center;

}

/* Cards */
.card {
        text-align: center;
    background: linear-gradient(145deg, #1E293B, #0F172A);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

/* Glow Card */
.glow {
    border: 1px solid rgba(79,139,249,0.3);
    box-shadow: 0 0 20px rgba(79,139,249,0.2);
}

.block-container {
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4F8BF9, #9333EA);
    color: white;
    border-radius: 12px;
    height: 45px;
    font-weight: 600;
    border: none;
}

.center {
    text-align: center;
}

/* Chat bubble */
.chat {
    background-color: #1E293B;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">Riyalyze Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered lifestyle insights + challenge system</div>', unsafe_allow_html=True)

# =========================
# TOP GRID
# =========================
col1, col2 = st.columns(2)

# =========================
# LEFT - PREDICTION
# =========================
with col1:
    
    st.subheader("Your AI Prediction")

    st.markdown("### 🔥 Moderate Risk")
    st.write("Your lifestyle shows patterns that need improvement.")

    st.write("**Main Issues:**")
    st.write("- High screen time")
    st.write("- Low activity")
    st.write("- Late caffeine intake")

    
    

# =========================
# RIGHT - QUICK STATS
# =========================
with col2:
    st.subheader("Quick Stats")

    st.metric("Caffeine Intake", "1.0 Cups/day")
    st.metric("Screen Time", "9 hrs")
    st.metric("Sleep", "5 hrs")


# =========================
# SECOND ROW
# =========================
col3, col4 = st.columns([1,1], gap="small")# =========================
# CHALLENGE
# =========================
with col3:
    st.subheader("🔥 Live Challenge")

    st.write("Goal: Reduce Screen Time")

    st.progress(0.7)
    st.write("You vs another user")

    st.write("🏆 Current Leader: You")

    st.button("View Challenge")


# =========================
# CHATBOT
# =========================
with col4:
    st.subheader("🤖 AI Health Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Ask me about your lifestyle 🚀"}
        ]

    for msg in st.session_state.messages:
        st.markdown(f'<div class="chat"><b>{msg["role"]}:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Ask something...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # ردود ذكية بسيطة
        if "sleep" in user_input.lower():
            reply = "Try sleeping earlier and avoid screens before bed."
        elif "screen" in user_input.lower():
            reply = "Reduce screen time by setting daily limits."
        elif "caffeine" in user_input.lower():
            reply = "Avoid caffeine after 8 PM for better sleep."
        else:
            reply = "Focus on balance: sleep, diet, and activity."

        st.session_state.messages.append({"role": "assistant", "content": reply})


