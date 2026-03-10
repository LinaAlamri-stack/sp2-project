import streamlit as st  # استيراد مكتبة Streamlit لبناء واجهة الويب

# =========================
# PAGE CONFIG
# =========================
# إعدادات الصفحة الأساسية مثل عنوان الصفحة وشكل العرض
st.set_page_config(
    page_title="Riyalyze Lifestyle Assessment",  # اسم الصفحة في التبويب
    layout="centered"  # يجعل المحتوى في وسط الصفحة
)

# =========================
# CUSTOM CSS
# =========================
# هنا نضيف CSS لتنسيق الصفحة (الألوان، الخطوط، المسافات)
st.markdown("""
<style>

/* تنسيق عنوان Riyalyze */
.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

/* تنسيق عنوان Lifestyle Assessment */
.sub-title {
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #4F8BF9;
}

/* وصف الاستبيان */
.description {
    text-align: center;
    font-size: 16px;
    color: #666666;
    margin-bottom: 8px;
}

/* ملاحظة الوقت المتوقع */
.time-note {
    text-align: center;
    font-size: 14px;
    color: #888888;
    margin-bottom: 30px;
}

/* تصميم صندوق الفورم */
div[data-testid="stForm"] {
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #E5E7EB;
    background-color: #FFFFFF;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}

/* تنسيق زر الإرسال */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    border-radius: 12px;
    height: 45px;
    font-size: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
# عرض عنوان المشروع
st.markdown('<div class="main-title">Riyalyze</div>', unsafe_allow_html=True)

# عرض عنوان الاستبيان
st.markdown('<div class="sub-title">Lifestyle Assessment</div>', unsafe_allow_html=True)

# وصف قصير يشرح الهدف من الاستبيان
st.markdown(
    '<div class="description">Answer a few questions to help us analyze your lifestyle habits and generate your personalized dashboard.</div>',
    unsafe_allow_html=True
)

# ملاحظة أن الاستبيان سريع
st.markdown('<div class="time-note">Estimated time: less than 1 minute</div>', unsafe_allow_html=True)

# =========================
# FORM
# =========================
# إنشاء فورم يحتوي كل الأسئلة
with st.form("lifestyle_assessment_form"):

    # سؤال عدد ساعات النوم
    q1_sleep_hours = st.selectbox(
        "1. How many hours do you sleep per night?",
        options=list(range(0, 13)),  # الخيارات من 0 إلى 12
        index=None,
        placeholder="Select an option"
    )

    # سؤال جودة النوم
    q2_sleep_quality = st.selectbox(
        "2. How would you rate your sleep quality?",
        options=["Poor", "Average", "Good", "Excellent"],
        index=None,
        placeholder="Select an option"
    )

    # سؤال الوجبات السريعة
    q3_fast_food = st.selectbox(
        "3. How many times do you eat fast food per week?",
        options=["0", "1-2", "3-4", "5+"],
        index=None,
        placeholder="Select an option"
    )

    # سؤال استهلاك الكافيين يومياً
    q4_caffeine_per_day = st.selectbox(
        "4. How many caffeinated drinks do you consume per day?",
        options=["0", "1", "2", "3+"],
        index=None,
        placeholder="Select an option"
    )

    # سؤال الكافيين بعد 8 مساء
    q5_caffeine_after_8pm = st.selectbox(
        "5. Do you consume caffeine after 8 PM?",
        options=["Yes", "No"],
        index=None,
        placeholder="Select an option"
    )

    # سؤال الأكل بعد 10 مساء
    q6_eat_after_10pm = st.selectbox(
        "6. Do you usually eat after 10 PM?",
        options=["Yes", "No"],
        index=None,
        placeholder="Select an option"
    )

    # سؤال عدد أيام النشاط البدني
    q7_physical_activity_days = st.selectbox(
        "7. How many days per week do you do physical activity?",
        options=list(range(0, 8)),  # من 0 إلى 7 أيام
        index=None,
        placeholder="Select an option"
    )

    # سؤال ساعات الشاشة
    q8_screen_hours = st.selectbox(
        "8. How many hours do you spend on screens daily?",
        options=list(range(0, 17)),  # من 0 إلى 16 ساعة
        index=None,
        placeholder="Select an option"
    )

    # سؤال انخفاض الطاقة
    q9_low_energy = st.selectbox(
        "9. How often do you feel low energy during the day?",
        options=["Rarely", "Sometimes", "Often", "Always"],
        index=None,
        placeholder="Select an option"
    )

    # زر إرسال الفورم
    submitted = st.form_submit_button("Submit Assessment")

# =========================
# ENCODING + OUTPUT
# =========================
# إذا المستخدم ضغط Submit
if submitted:

    # نجمع كل الإجابات في قائمة
    questions = [
        q1_sleep_hours,
        q2_sleep_quality,
        q3_fast_food,
        q4_caffeine_per_day,
        q5_caffeine_after_8pm,
        q6_eat_after_10pm,
        q7_physical_activity_days,
        q8_screen_hours,
        q9_low_energy
    ]

    # التحقق إذا فيه سؤال ما تجاوب
    if any(answer is None for answer in questions):
        st.error("Please answer all questions before submitting.")

    else:

        # تحويل جودة النوم من نص إلى رقم
        sleep_quality_map = {
            "Poor": 0,
            "Average": 1,
            "Good": 2,
            "Excellent": 3
        }

        # تحويل عدد الوجبات السريعة
        fast_food_map = {
            "0": 0,
            "1-2": 1,
            "3-4": 2,
            "5+": 3
        }

        # تحويل استهلاك الكافيين
        caffeine_per_day_map = {
            "0": 0,
            "1": 1,
            "2": 2,
            "3+": 3
        }

        # تحويل نعم / لا إلى أرقام
        yes_no_map = {
            "Yes": 1,
            "No": 0
        }

        # تحويل مستوى الطاقة
        low_energy_map = {
            "Rarely": 0,
            "Sometimes": 1,
            "Often": 2,
            "Always": 3
        }

        # إنشاء قاموس يحتوي البيانات النهائية بنفس أسماء أعمدة الداتا
        user_input = {
            "caffeine_per_day": caffeine_per_day_map[q4_caffeine_per_day],
            "fast_food_per_week": fast_food_map[q3_fast_food],
            "sleep_hours": q1_sleep_hours,
            "physical_activity_days": q7_physical_activity_days,
            "screen_hours": q8_screen_hours,
            "sleep_quality": sleep_quality_map[q2_sleep_quality],
            "eat_after_10pm": yes_no_map[q6_eat_after_10pm],
            "caffeine_after_8pm": yes_no_map[q5_caffeine_after_8pm],
            "low_energy_frequency": low_energy_map[q9_low_energy]
        }

        # رسالة نجاح
        st.success("Assessment submitted successfully!")

        # عنوان البيانات المحولة
        st.subheader("Encoded Data")

        # عرض البيانات النهائية التي ستذهب للمودل
        st.json(user_input)
       