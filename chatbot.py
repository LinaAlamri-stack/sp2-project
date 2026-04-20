import streamlit as st

# ---------------------------
# Dummy User Data (اغيرها بعدين)
# ---------------------------
user_data = {
    "cluster": "B",
    "risk": "High",
    "caffeine": 5,  # cups/day
    "sleep": 5      # hours/day
}

# ---------------------------
# Rule-Based Logic
# ---------------------------
def generate_response(user_input, data):
    cluster = data["cluster"]
    risk = data["risk"]
    caffeine = data["caffeine"]
    sleep = data["sleep"]

    response = f"Based on your cluster ({cluster}) and current habits:\n\n"

    # Risk logic
    if risk == "High":
        response += "- You are currently in a HIGH risk category.\n"
        response += "- Immediate lifestyle adjustments are recommended.\n\n"
    elif risk == "Medium":
        response += "- You are in a MEDIUM risk category.\n"
        response += "- Small improvements can reduce your risk.\n\n"
    else:
        response += "- You are in a LOW risk category.\n"
        response += "- Maintain your current healthy habits.\n\n"

    # Caffeine logic
    if caffeine >= 4:
        response += f"- Your caffeine intake ({caffeine} cups/day) is high.\n"
        response += "- Try reducing it to 2 cups/day.\n\n"

    # Sleep logic
    if sleep < 6:
        response += f"- Your sleep ({sleep} hours/day) is below recommended levels.\n"
        response += "- Aim for 7–8 hours per night.\n\n"

    # Specific questions
    if "reduce risk" in user_input.lower():
        response += "👉 Focus on improving sleep and reducing caffeine first.\n"

    if "diet" in user_input.lower():
        response += "👉 Consider a balanced diet with less sugar and processed food.\n"

    if "sleep" in user_input.lower():
        response += "👉 Keep a consistent sleep schedule and avoid caffeine at night.\n"

    # Future prediction line
    response += "\nIf current habits continue, your 10-year projection indicates similar or higher risk."

    return response


# ---------------------------
# UI Design
# ---------------------------
st.set_page_config(page_title="Health Chatbot", layout="wide")

st.title("💬 Health Insights Chatbot")
st.caption("This chatbot provides personalized insights based on your data")

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! Ask me about your health insights"
    })

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------
# Quick Buttons
# ---------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("How to reduce risk?"):
        user_input = "reduce risk"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data)
        st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    if st.button("Best diet for me?"):
        user_input = "diet"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data)
        st.session_state.messages.append({"role": "assistant", "content": response})

with col3:
    if st.button("Improve sleep?"):
        user_input = "sleep"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Type your question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = generate_response(user_input, user_data)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()