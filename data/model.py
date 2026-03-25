import pandas as pd
import os

def load_data():
    paths = ["data/survey_data.csv", "survey_data.csv", "../data/survey_data.csv"]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None


def get_metrics(df):
    total_users = len(df)
    male_count = len(df[df.iloc[:, 2] == 'Male'])
    female_count = len(df[df.iloc[:, 2] == 'Female'])

    return total_users, male_count, female_count
