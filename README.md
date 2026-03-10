# sp2-project
Web application project for SP2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("data/survey_data.csv")

print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())

df.hist(figsize=(10,8))
plt.show()

plt.figure(figsize=(8,6))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.show()

if "risk_level" in df.columns:
    sns.countplot(x="risk_level", data=df)
    plt.show()