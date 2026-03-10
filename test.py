import pandas as pd

df = pd.read_csv("data\\survey_data.csv")

score_map = {
    "Rarely": 0,
    "Sometimes": 1,
    "mostly": 2,
}

df["Low Energy Score"] = df["15. How often do you feel low energy during the day?"].map(score_map)

df["Risk Score"] = df["Low Energy Score"]

def risk_level(score):
    if score == 0:
        return "Low"
    elif score == 1:
        return "Moderate"
    else:
        return "High"

df["Risk Level"] = df["Risk Score"].apply(risk_level)

print(df.head())

print("\nRisk Level Distribution:")
print(df["Risk Level"].value_counts())

df.to_csv("data\\survey_data_with_risk.csv", index=False)
plt.show()