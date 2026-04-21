import streamlit as st
from database import get_user_by_id, get_user_survey, init_db

# ---------------------------
# Initialize
# ---------------------------
st.set_page_config(page_title="Health Coach", layout="wide")
init_db()

# Get user from session
user_id = st.session_state.get("user_id")
if not user_id:
    st.warning("Please log in first.")
    st.stop()

# ---------------------------
# Load Real User Data from DB
# ---------------------------
user = get_user_by_id(user_id)
survey = get_user_survey(user_id)

if not survey:
    st.warning("Please complete your health assessment first.")
    st.stop()

user_data = {
    "name": user.get("name", "there") if user else "there",
    "age": survey.get("age"),
    "cluster": survey.get("projection_cluster", "Unknown"),
    "risk_level": survey.get("risk_level", "moderate"),
    "risk_score": survey.get("risk_score", 50),
    "caffeine": survey.get("caffeine_per_day", 0),
    "sleep": survey.get("sleep_hours", 7),
    "sleep_quality": survey.get("sleep_quality", 2),
    "fast_food": survey.get("fast_food_per_week", 0),
    "activity": survey.get("physical_activity_days", 0),
    "screen": survey.get("screen_hours", 0),
    "eat_late": survey.get("eat_after_10pm", 0),
    "caffeine_late": survey.get("caffeine_after_8pm", 0),
    "low_energy": survey.get("low_energy_frequency", 0),
}

# ---------------------------
# Coaching Logic Engine
# ---------------------------
def get_personalized_insights(data):
    """Generate insights based on user's specific data"""
    insights = []
    
    # Sleep analysis
    if data["sleep"] < 6:
        insights.append({
            "type": "warning",
            "area": "sleep",
            "message": f"You're getting only {data['sleep']} hours of sleep. This significantly impacts your energy and health.",
            "tip": "Try setting a consistent bedtime alarm 8 hours before you need to wake up."
        })
    elif data["sleep"] < 7:
        insights.append({
            "type": "caution",
            "area": "sleep",
            "message": f"Your {data['sleep']} hours of sleep is slightly below optimal.",
            "tip": "Adding just 30-60 minutes could improve your daily energy."
        })
    
    # Caffeine analysis
    if data["caffeine"] >= 3:
        insights.append({
            "type": "warning",
            "area": "caffeine",
            "message": f"High caffeine intake ({data['caffeine']}+ cups/day) can affect sleep quality and increase anxiety.",
            "tip": "Try reducing by one cup per week to avoid withdrawal symptoms."
        })
    
    if data["caffeine_late"]:
        insights.append({
            "type": "warning",
            "area": "caffeine",
            "message": "Caffeine after 8 PM disrupts your sleep cycle even if you fall asleep.",
            "tip": "Switch to decaf or herbal tea after 6 PM."
        })
    
    # Late eating
    if data["eat_late"]:
        insights.append({
            "type": "caution",
            "area": "diet",
            "message": "Eating after 10 PM affects digestion and sleep quality.",
            "tip": "Try having your last meal at least 3 hours before bedtime."
        })
    
    # Fast food
    if data["fast_food"] >= 2:
        insights.append({
            "type": "caution",
            "area": "diet",
            "message": f"Eating fast food {data['fast_food']}+ times per week increases health risks.",
            "tip": "Try meal prepping on weekends to have healthy alternatives ready."
        })
    
    # Physical activity
    if data["activity"] < 3:
        insights.append({
            "type": "caution",
            "area": "activity",
            "message": f"Only {data['activity']} days of activity per week is below recommendations.",
            "tip": "Start with short 15-minute walks. Consistency matters more than intensity."
        })
    
    # Screen time
    if data["screen"] >= 8:
        insights.append({
            "type": "warning",
            "area": "screen",
            "message": f"{data['screen']} hours of screen time daily can strain your eyes and affect sleep.",
            "tip": "Use the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds."
        })
    
    return insights

def get_priority_actions(data):
    """Get top 3 most impactful changes for this user"""
    actions = []
    
    # Prioritize based on impact
    if data["risk_level"] == "high":
        if data["sleep"] < 6:
            actions.append("🛏️ Increase sleep to at least 7 hours - this is your #1 priority")
        if data["caffeine_late"]:
            actions.append("☕ Stop caffeine after 6 PM immediately")
        if data["activity"] < 2:
            actions.append("🚶 Add at least 2 days of 30-minute walks")
    elif data["risk_level"] == "moderate":
        if data["sleep"] < 7:
            actions.append("🛏️ Add 30-60 minutes to your sleep")
        if data["caffeine"] >= 3:
            actions.append("☕ Reduce caffeine by 1 cup per day")
        if data["fast_food"] >= 2:
            actions.append("🥗 Replace one fast food meal with home-cooked food")
    else:
        actions.append("✨ Maintain your current healthy habits")
        actions.append("📊 Consider tracking your progress weekly")
    
    return actions[:3]

def generate_response(user_input, data, chat_history):
    """Generate contextual, non-repetitive responses"""
    user_input_lower = user_input.lower()
    name = data["name"].split()[0] if data["name"] else "there"
    
    # Track what we've already discussed
    discussed_topics = set()
    for msg in chat_history:
        if msg["role"] == "assistant":
            content_lower = msg["content"].lower()
            if "sleep" in content_lower:
                discussed_topics.add("sleep")
            if "caffeine" in content_lower or "coffee" in content_lower:
                discussed_topics.add("caffeine")
            if "diet" in content_lower or "food" in content_lower:
                discussed_topics.add("diet")
            if "exercise" in content_lower or "activity" in content_lower:
                discussed_topics.add("activity")
            if "risk" in content_lower:
                discussed_topics.add("risk")
    
    # Greetings
    greetings = ["hi", "hello", "hey", "مرحبا", "هلا", "السلام"]
    if any(g in user_input_lower for g in greetings):
        risk_emoji = "🟢" if data["risk_level"] == "low" else "🟡" if data["risk_level"] == "moderate" else "🔴"
        return f"""Hey {name}! 👋

I've looked at your health profile. Here's what I see:

{risk_emoji} **Risk Level:** {data['risk_level'].title()} (Score: {data['risk_score']}/100)
☕ **Caffeine:** {data['caffeine']} cups/day
🛏️ **Sleep:** {data['sleep']} hours/night
🏃 **Activity:** {data['activity']} days/week

What would you like to focus on today?"""

    # Risk questions
    if any(word in user_input_lower for word in ["risk", "score", "level", "خطر", "مستوى"]):
        if data["risk_level"] == "high":
            priority_actions = get_priority_actions(data)
            return f"""Your risk score is **{data['risk_score']}/100** which puts you in the **high risk** category.

**Your Top Priority Actions:**
{chr(10).join(f"• {action}" for action in priority_actions)}

The good news? Small consistent changes can significantly lower your risk within weeks. Which area feels most doable to start with?"""
        elif data["risk_level"] == "moderate":
            return f"""Your risk score is **{data['risk_score']}/100** - moderate range.

You're not in the danger zone, but there's room for improvement. Based on your data, focusing on {"sleep" if data["sleep"] < 7 else "caffeine reduction" if data["caffeine"] >= 3 else "physical activity"} would give you the best results.

Want specific tips for that area?"""
        else:
            return f"""Your risk score is **{data['risk_score']}/100** - you're doing great! 🎉

Keep up your current habits. Your {data['sleep']} hours of sleep and {data['activity']} days of activity are serving you well.

Any specific area you want to optimize further?"""

    # Sleep questions
    if any(word in user_input_lower for word in ["sleep", "نوم", "tired", "تعب", "energy", "طاقة"]):
        if "sleep" in discussed_topics:
            # Give different advice since we discussed sleep before
            return f"""Since we talked about sleep before, here's something else that might help:

{"• Your caffeine after 8 PM is definitely disrupting deep sleep cycles. Even if you fall asleep, the quality suffers." if data["caffeine_late"] else ""}
{"• Late night eating affects sleep quality too. Try finishing meals by 8 PM." if data["eat_late"] else ""}
{"• High screen time (" + str(data['screen']) + " hours) before bed suppresses melatonin production." if data["screen"] >= 6 else ""}

Have you tried any of the previous suggestions?"""
        else:
            if data["sleep"] < 6:
                return f"""With only **{data['sleep']} hours** of sleep, your body isn't getting enough recovery time.

**Why this matters for you:**
• Your {data["low_energy"]}-level fatigue is directly connected to this
• It's harder to maintain healthy eating habits when tired
• Exercise feels harder than it should

**Start here:**
1. Set a phone alarm for 10:30 PM to start winding down
2. No screens 30 minutes before bed
3. Keep your room cool (18-20°C)

What's currently keeping you up late?"""
            elif data["sleep"] < 7:
                return f"""You're getting {data['sleep']} hours - close but not quite optimal.

Adding just 30-45 minutes could noticeably improve your energy. Your sleep quality rating of {data['sleep_quality']}/3 suggests the sleep you're getting isn't fully restorative either.

{"Cutting caffeine after 6 PM would help with quality." if data["caffeine_late"] else "A consistent bedtime would help your body optimize its sleep cycles."}

What time do you usually go to bed?"""
            else:
                return f"""Your {data['sleep']} hours of sleep is in a good range! 

{"However, your sleep quality could improve. The late caffeine and eating habits might be affecting how restorative your sleep is." if data["caffeine_late"] or data["eat_late"] else "And with good sleep quality, you're set in this area."}

Is there something specific about your sleep that concerns you?"""

    # Caffeine questions
    if any(word in user_input_lower for word in ["caffeine", "coffee", "قهوة", "كافيين", "tea", "شاي"]):
        if data["caffeine"] >= 3:
            return f"""You're at **{data['caffeine']}+ cups** daily, which is on the higher side.

**What this means for your body:**
• Increased cortisol (stress hormone)
• Disrupted sleep even if you feel tired
• Caffeine tolerance means you need more for the same effect

**Practical reduction plan:**
Week 1: Replace one cup with decaf
Week 2: Replace another with green tea (less caffeine)
Week 3: Aim for 2 cups max before 2 PM

{"🚨 And definitely cut the evening caffeine - that's affecting your sleep quality significantly." if data["caffeine_late"] else ""}

Which cup would be easiest to replace first?"""
        elif data["caffeine"] >= 2:
            return f"""Your {data['caffeine']} cups is moderate. {"The main issue is the timing - caffeine after 8 PM stays in your system for hours." if data["caffeine_late"] else "That's a reasonable amount if it's consumed before early afternoon."}

Want tips on timing your caffeine for better energy throughout the day?"""
        else:
            return f"""Your caffeine intake ({data['caffeine']} cup/day) is actually quite good! This isn't a concern area for you.

Should we focus on something that would have more impact on your health?"""

    # Diet questions
    if any(word in user_input_lower for word in ["diet", "food", "eat", "أكل", "طعام", "غذاء", "fast food"]):
        if data["fast_food"] >= 2 or data["eat_late"]:
            issues = []
            if data["fast_food"] >= 2:
                issues.append(f"• Fast food {data['fast_food']}+ times/week adds excess sodium, sugar, and unhealthy fats")
            if data["eat_late"]:
                issues.append("• Eating after 10 PM disrupts your digestion and sleep")
            
            return f"""Based on your profile, here's what stands out:

{chr(10).join(issues)}

**Simple swaps that work:**
{"• Meal prep on Sunday - even just having cooked rice and grilled chicken ready helps" if data["fast_food"] >= 2 else ""}
{"• If you must eat late, keep it light - yogurt, fruit, or a small portion" if data["eat_late"] else ""}
• Keep healthy snacks accessible so fast food isn't the default

What's usually driving the fast food choices - time, convenience, or cravings?"""
        else:
            return f"""Your eating habits look reasonable based on your data. 

{"The late-night eating is something to watch though." if data["eat_late"] else "Not much to fix here!"}

Any specific dietary goals you're working toward?"""

    # Exercise/Activity questions
    if any(word in user_input_lower for word in ["exercise", "activity", "workout", "رياضة", "تمارين", "active", "walk", "مشي"]):
        if data["activity"] < 2:
            return f"""With only **{data['activity']} days** of activity, this is a key area for improvement.

**Why this matters especially for you:**
• Physical activity directly reduces your risk score
• It improves sleep quality (which you need)
• Even light activity helps manage stress and energy

**Realistic starting point:**
Don't aim for gym workouts. Start with:
1. 15-minute walk after lunch or dinner
2. Take stairs instead of elevator
3. Stand and stretch every hour if you work at a desk

What type of movement do you actually enjoy (or used to enjoy)?"""
        elif data["activity"] < 4:
            return f"""You're at {data['activity']} days of activity - not bad, but there's room to grow.

**To level up:**
• Add one more active day - it doesn't have to be intense
• Try to make one session slightly longer
• Mix in different activities to stay interested

What's your current activity usually look like?"""
        else:
            return f"""**{data['activity']} days of activity is excellent!** 💪

You're above average here. This is helping keep your risk score lower than it would otherwise be.

Keep it up and make sure you're also getting adequate recovery and sleep to support this activity level."""

    # Screen time questions
    if any(word in user_input_lower for word in ["screen", "phone", "جوال", "شاشة", "computer"]):
        if data["screen"] >= 8:
            return f"""**{data['screen']} hours** of screen time is quite high.

**Effects you might be experiencing:**
• Eye strain and headaches
• Disrupted sleep (blue light suppresses melatonin)
• Less time for physical activity

**Practical reductions:**
• Enable night mode after 8 PM
• Take a 5-minute break every hour
• No screens in the bedroom
• Try audiobooks/podcasts instead of videos when possible

Which part of your day has the most screen time?"""
        else:
            return f"""Your screen time ({data['screen']} hours) is within a reasonable range.

Just make sure to take regular breaks and avoid screens close to bedtime. The 20-20-20 rule helps: every 20 minutes, look at something 20 feet away for 20 seconds.

Anything specific about screen habits you want to discuss?"""

    # Cluster questions
    if any(word in user_input_lower for word in ["cluster", "group", "category", "مجموعة"]):
        return f"""You're in **{data['cluster']}**.

This groups you with users who have similar lifestyle patterns. It helps us understand common challenges and what interventions work best for people like you.

Your specific data within this cluster:
• Caffeine: {data['caffeine']} cups/day
• Sleep: {data['sleep']} hours
• Screen time: {data['screen']} hours

Want to know what typically helps people in your cluster improve their scores?"""

    # Progress/Improvement questions
    if any(word in user_input_lower for word in ["improve", "better", "تحسين", "أحسن", "change", "تغيير", "help"]):
        priority_actions = get_priority_actions(data)
        insights = get_personalized_insights(data)
        
        warning_count = len([i for i in insights if i["type"] == "warning"])
        
        return f"""Based on your complete profile, here's your personalized action plan:

**Your Top 3 Priorities:**
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(priority_actions))}

**Quick Wins (can start today):**
{"• Set a bedtime alarm for 10:30 PM" if data["sleep"] < 7 else ""}
{"• Replace afternoon coffee with water or herbal tea" if data["caffeine"] >= 2 else ""}
{"• Take a 10-minute walk after one meal" if data["activity"] < 3 else ""}

You have {warning_count} areas that need attention. Focus on one thing at a time - trying to change everything at once usually doesn't stick.

Which priority feels most achievable for you to start with?"""

    # Default response - be helpful without repeating
    recent_topics = list(discussed_topics)[-3:] if discussed_topics else []
    
    suggestions = []
    if "sleep" not in recent_topics and data["sleep"] < 7:
        suggestions.append("sleep improvement")
    if "caffeine" not in recent_topics and data["caffeine"] >= 2:
        suggestions.append("caffeine management")
    if "diet" not in recent_topics and (data["fast_food"] >= 2 or data["eat_late"]):
        suggestions.append("eating habits")
    if "activity" not in recent_topics and data["activity"] < 3:
        suggestions.append("physical activity")
    
    if suggestions:
        return f"""I'm here to help with your health journey, {name}.

Based on your profile, we could discuss:
{chr(10).join(f"• {s.title()}" for s in suggestions[:3])}

Or ask me anything specific about your health data. I can explain your risk score, suggest improvements, or give tips for any area you're curious about."""
    else:
        return f"""I'm your health coach, {name}. You can ask me about:

• Your risk score and what affects it
• Sleep optimization
• Managing caffeine intake
• Diet and eating habits
• Physical activity recommendations
• Your cluster group and what it means

What would you like to explore?"""


# ---------------------------
# UI Design
# ---------------------------
st.title("💬 Your Personal Health Coach")
st.caption(f"Personalized insights for {user_data['name']} • Risk Level: {user_data['risk_level'].title()}")

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message with user context
if len(st.session_state.messages) == 0:
    risk_emoji = "🟢" if user_data["risk_level"] == "low" else "🟡" if user_data["risk_level"] == "moderate" else "🔴"
    welcome = f"""Hi {user_data['name'].split()[0] if user_data['name'] else 'there'}! 👋

I'm your personal health coach. I've reviewed your health assessment and I'm ready to help.

{risk_emoji} Your current risk level is **{user_data['risk_level']}** with a score of **{user_data['risk_score']}/100**.

What would you like to work on today? You can ask me about:
• How to reduce your risk score
• Sleep improvement strategies
• Managing caffeine intake
• Diet recommendations
• Building an activity routine

Or just say hi and tell me what's on your mind!"""
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome
    })

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Quick Action Buttons
# ---------------------------
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 My Risk Score", use_container_width=True):
        user_input = "What's my risk score and how can I improve it?"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    if st.button("🛏️ Sleep Help", use_container_width=True):
        user_input = "How can I improve my sleep?"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col3:
    if st.button("☕ Caffeine Tips", use_container_width=True):
        user_input = "Tell me about my caffeine intake"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col4:
    if st.button("🎯 Action Plan", use_container_width=True):
        user_input = "What should I improve first?"
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_response(user_input, user_data, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ---------------------------
# Chat Input
# ---------------------------
user_input = st.chat_input("Ask me anything about your health...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = generate_response(user_input, user_data, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ---------------------------
# Sidebar with User Stats
# ---------------------------
with st.sidebar:
    st.markdown("### 📋 Your Profile")
    st.markdown(f"**Name:** {user_data['name']}")
    st.markdown(f"**Cluster:** {user_data['cluster']}")
    
    st.markdown("---")
    st.markdown("### 📊 Current Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk Score", f"{user_data['risk_score']}/100")
        st.metric("Sleep", f"{user_data['sleep']}h")
        st.metric("Activity", f"{user_data['activity']} days")
    with col2:
        st.metric("Risk Level", user_data['risk_level'].title())
        st.metric("Caffeine", f"{user_data['caffeine']} cups")
        st.metric("Screen", f"{user_data['screen']}h")
    
    st.markdown("---")
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
