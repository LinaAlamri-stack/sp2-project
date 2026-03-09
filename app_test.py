import pandas as pd

df = pd.read_csv("data/survey_data.csv")

print("Opened successfully")
print(df.head())
print(df.columns)