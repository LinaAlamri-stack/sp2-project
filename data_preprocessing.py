import pandas as pd


# 1) قراءة الداتا

df = pd.read_csv("data/survey_data.csv")


# 2) إعادة تسمية الأعمدة لأسامي أسهل


df = df.rename(columns={
    "4. Number of caffeine drinks per day": "caffeine_per_day",
    "8. Number of fast food per week": "fast_food_per_week",
    "11. Average number of hours of sleep per night": "sleep_hours",
    "13. Number of days of physical activity per week": "physical_activity_days",
    "14. Number of hours of screen use per day": "screen_hours",
    "12. Sleep Quality Assessment": "sleep_quality",
    "10. Eat after 10 pm": "eat_after_10pm",
    "7. Caffeine consumption after 8 pm": "caffeine_after_8pm",
    "15. How often do you feel low energy during the day?": "low_energy_frequency"
})


# 3) تنظيف النصوص العامة

for col in [
    "caffeine_per_day",
    "fast_food_per_week",
    "sleep_hours",
    "physical_activity_days",
    "screen_hours",
    "sleep_quality",
    "eat_after_10pm",
    "caffeine_after_8pm",
    "low_energy_frequency"
]:
    df[col] = df[col].astype(str).str.strip().str.lower()

print("\n=== UNIQUE VALUES CHECK ===")

cols_to_check = [
    "caffeine_per_day",
    "fast_food_per_week",
    "sleep_hours",
    "physical_activity_days",
    "screen_hours",
    "sleep_quality",
    "eat_after_10pm",
    "caffeine_after_8pm",
    "low_energy_frequency"
]

for col in cols_to_check:
    print(f"\n{col}:")
    print(df[col].unique())

# 4) تحويل caffeine_per_day
# إذا فيه 1-2 نخليه 1.5
# ولو أرقام مباشرة بيحولها

df["caffeine_per_day"] = df["caffeine_per_day"].replace({
    "1-2": 1.5,
    "1 - 2": 1.5,
    "more than 4": 5,
    "more than four": 5
})

df["caffeine_per_day"] = pd.to_numeric(df["caffeine_per_day"], errors="coerce")


# 5) تحويل fast_food_per_week

df["fast_food_per_week"] = df["fast_food_per_week"].replace({
    "0": 0,
    "1-2": 1.5,
    "1 - 2": 1.5,
    "3-4": 3.5,
    "3 - 4": 3.5,
    "more than 4": 5
})

df["fast_food_per_week"] = pd.to_numeric(df["fast_food_per_week"], errors="coerce")


# 6) تحويل sleep_hours

df["sleep_hours"] = df["sleep_hours"].replace({
    "less than 5": 4,
    "5-6": 5.5,
    "5 - 6": 5.5,
    "7-8": 7.5,
    "7 - 8": 7.5,
    "more than 8": 9
})

df["sleep_hours"] = pd.to_numeric(df["sleep_hours"], errors="coerce")


# 7) تحويل physical_activity_days
df["physical_activity_days"] = df["physical_activity_days"].replace({
    "0": 0,
    "1-2": 1.5,
    "1 - 2": 1.5,
    "3-4": 3.5,
    "3 - 4": 3.5,
    "5+": 5,
    "5 +": 5
})
df["physical_activity_days"] = pd.to_numeric(df["physical_activity_days"], errors="coerce")


# 8) تحويل screen_hours

df["screen_hours"] = df["screen_hours"].replace({
    "less than 3": 2,
    "3-5": 4,
    "3 - 5": 4,
    "6-8": 7,
    "6 - 8": 7,
    "more than 8": 9
})

df["screen_hours"] = pd.to_numeric(df["screen_hours"], errors="coerce")


# 9) تحويل sleep_quality

df["sleep_quality"] = df["sleep_quality"].replace({
    "bad": 1,
    "average": 2,
    "good": 3,
    "excellent": 4
})

df["sleep_quality"] = pd.to_numeric(df["sleep_quality"], errors="coerce")


# 10) تحويل eat_after_10pm

df["eat_after_10pm"] = df["eat_after_10pm"].replace({
    "no": 0,
    "sometimes": 1,
    "mostly": 2
})

df["eat_after_10pm"] = pd.to_numeric(df["eat_after_10pm"], errors="coerce")


# 11) تحويل caffeine_after_8pm

df["caffeine_after_8pm"] = df["caffeine_after_8pm"].replace({
    "no": 0,
    "yes": 1
})

df["caffeine_after_8pm"] = pd.to_numeric(df["caffeine_after_8pm"], errors="coerce")


# 12) تحويل low_energy_frequency

df["low_energy_frequency"] = df["low_energy_frequency"].replace({
    "Rarely": 1,
    "Sometimes": 2,
    "mostly": 3
})

df["low_energy_frequency"] = pd.to_numeric(df["low_energy_frequency"], errors="coerce")


# 13) اختيار الأعمدة النهائية

features = df[[
    "caffeine_per_day",
    "fast_food_per_week",
    "sleep_hours",
    "physical_activity_days",
    "screen_hours",
    "sleep_quality",
    "eat_after_10pm",
    "caffeine_after_8pm",
    "low_energy_frequency"
]]




features = features.fillna(features.mean())

# نخلي df بنفس الصفوف الموجودة في features
df_clean = df.loc[features.index].copy()


# 15) حفظ الداتا النظيفة

df_clean.to_csv("data/cleaned_survey_data.csv", index=False)
features.to_csv("data/clustering_features.csv", index=False)

print("Preprocessing finished successfully!")
print("\nCleaned features preview:")
print(features.head())

print("\nShape of clustering data:")
print(features.shape)