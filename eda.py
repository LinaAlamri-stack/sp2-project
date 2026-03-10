import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_auc_score
)

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline


# ==========================================
# 1. Load dataset
# ==========================================
file_path = "data\\survey_data.csv"
df = pd.read_csv(file_path)


# ==========================================
# 2. Clean text columns
# ==========================================
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip().str.lower()


# ==========================================
# 3. Define target source column
# ==========================================
energy_col = "15. How often do you feel low energy during the day?"

if energy_col not in df.columns:
    raise ValueError(f"Column not found: {energy_col}")


# ==========================================
# 4. Create target variables
# ==========================================
score_map = {
    "rarely": 0,
    "sometimes": 1,
    "mostly": 2
}

df["Low Energy Score"] = df[energy_col].map(score_map)
df["Low Energy Score"] = df["Low Energy Score"].fillna(0)
df["Risk Score"] = df["Low Energy Score"]


def classify_risk(score):
    if score == 0:
        return "low"
    elif score == 1:
        return "moderate"
    else:
        return "high"


df["Risk Level"] = df["Risk Score"].apply(classify_risk)


# ==========================================
# 5. Prepare feature columns
# ==========================================
exclude_cols = []

for col in df.columns:
    if col == energy_col:
        exclude_cols.append(col)
    elif col in ["Low Energy Score", "Risk Score", "Risk Level"]:
        exclude_cols.append(col)
    elif col.lower() == "timestamp":
        exclude_cols.append(col)

feature_cols = [col for col in df.columns if col not in exclude_cols]

model_df = df[feature_cols + ["Risk Level"]].copy()

for col in feature_cols:
    model_df[col] = model_df[col].fillna("unknown").astype(str).str.strip().str.lower()


# ==========================================
# 6. Convert to binary classification
# Keep only Low and High
# ==========================================
binary_df = model_df[model_df["Risk Level"].isin(["low", "high"])].copy()

if binary_df.empty:
    raise ValueError("No binary rows found. Check Risk Level generation.")

X = pd.get_dummies(binary_df[feature_cols], drop_first=False)

target_map = {
    "low": 0,
    "high": 1
}

target_names = ["Low", "High"]

y = binary_df["RiskLevel"] if "RiskLevel" in binary_df.columns else binary_df["Risk Level"]
y = y.map(target_map)

if y.isna().any():
    raise ValueError("Binary target contains unmapped values.")


# ==========================================
# 7. Train-test split
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

if len(X_train) == 0 or len(X_test) == 0:
    raise ValueError("Train/test split failed because the dataset is too small.")


# ==========================================
# 8. Show debug info before training
# ==========================================
print("\n=== Debug Info Before Training ===")
print("Original dataset size:", len(df))
print("Binary dataset size:", len(binary_df))
print("Train set size:", len(X_train))
print("Test set size:", len(X_test))

print("\nEnergy column distribution:")
print(df[energy_col].value_counts(dropna=False))

print("\nOriginal Risk Level distribution:")
print(df["Risk Level"].value_counts(dropna=False))

print("\nBinary Risk Level distribution:")
print(binary_df["Risk Level"].value_counts(dropna=False))

print("\ny_train distribution:")
print(y_train.value_counts().sort_index())

print("\ny_test distribution:")
print(y_test.value_counts().sort_index())


# ==========================================
# 9. Build model pipeline with safe SMOTE
# ==========================================
# k_neighbors=1 is safer for very small minority classes.
pipeline = Pipeline([
    ("smote", SMOTE(random_state=42, k_neighbors=1)),
    ("model", RandomForestClassifier(random_state=42))
])

param_grid = {
    "model__n_estimators": [100, 200, 300],
    "model__max_depth": [None, 5, 10],
    "model__min_samples_split": [2, 5],
    "model__min_samples_leaf": [1, 2],
    "model__class_weight": [None, "balanced", "balanced_subsample"]
}

cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)


# ==========================================
# 10. Train model with fallback
# ==========================================
try:
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1",
        cv=cv,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    used_smote = True

except Exception as e:
    print("\nSMOTE pipeline failed. Falling back to Random Forest without SMOTE.")
    print("Reason:", str(e))

    fallback_model = RandomForestClassifier(random_state=42)

    fallback_param_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth": [None, 5, 10],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2],
        "class_weight": [None, "balanced", "balanced_subsample"]
    }

    grid_search = GridSearchCV(
        estimator=fallback_model,
        param_grid=fallback_param_grid,
        scoring="f1",
        cv=cv,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    used_smote = False


# ==========================================
# 11. Predict
# ==========================================
y_pred = best_model.predict(X_test)

if hasattr(best_model, "predict_proba"):
    y_prob = best_model.predict_proba(X_test)[:, 1]
elif hasattr(best_model, "named_steps") and hasattr(best_model.named_steps["model"], "predict_proba"):
    y_prob = best_model.named_steps["model"].predict_proba(X_test)[:, 1]
else:
    y_prob = None


# ==========================================
# 12. Evaluate model
# ==========================================
print("\n=== Best Parameters ===")
print(grid_search.best_params_)

print("\n=== Best Cross-Validation F1 ===")
print(round(grid_search.best_score_, 4))

print("\n=== Test Accuracy ===")
print(round(accuracy_score(y_test, y_pred), 4))

print("\n=== Test F1 Score ===")
print(round(f1_score(y_test, y_pred), 4))

if y_prob is not None:
    print("\n=== ROC-AUC ===")
    print(round(roc_auc_score(y_test, y_prob), 4))

print("\n=== Classification Report ===")
print(classification_report(
    y_test,
    y_pred,
    labels=[0, 1],
    target_names=target_names,
    zero_division=0
))


# ==========================================
# 13. Save predictions
# ==========================================
results_df = X_test.copy()
results_df["Actual"] = y_test.values
results_df["Predicted"] = y_pred

if y_prob is not None:
    results_df["Predicted_Probability_High"] = y_prob

inverse_target_map = {
    0: "Low",
    1: "High"
}

results_df["Actual"] = results_df["Actual"].map(inverse_target_map)
results_df["Predicted"] = results_df["Predicted"].map(inverse_target_map)

results_df.to_csv("binary_model_predictions.csv", index=False)
print("\nSaved: binary_model_predictions.csv")


# ==========================================
# 14. Confusion Matrix
# ==========================================
cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

fig, ax = plt.subplots(figsize=(6, 5))
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=target_names
)
disp.plot(cmap="Blues", values_format="d", ax=ax)
ax.set_title("Binary Confusion Matrix (Low vs High)")
plt.tight_layout()
plt.savefig("binary_confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.show()

print("Saved: binary_confusion_matrix.png")


# ==========================================
# 15. Feature importance
# ==========================================
if hasattr(best_model, "named_steps"):
    rf_model = best_model.named_steps["model"]
else:
    rf_model = best_model

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf_model.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("\n=== Top 10 Important Features ===")
print(importance_df.head(10))

importance_df.to_csv("binary_feature_importance.csv", index=False)
print("\nSaved: binary_feature_importance.csv")

top_features = importance_df.head(10).sort_values(by="Importance")

plt.figure(figsize=(10, 6))
plt.barh(top_features["Feature"], top_features["Importance"])
plt.title("Top 10 Important Features (Binary Model)")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("binary_top_features.png", dpi=300, bbox_inches="tight")
plt.show()

print("Saved: binary_top_features.png")


# ==========================================
# 16. Data preview
# ==========================================
print("\n=== Data Preview ===")
print(df[[energy_col, "Low Energy Score", "Risk Score", "Risk Level"]].head())


# ==========================================
# 17. Summary
# ==========================================
print("\n=== Summary ===")
print("Selected model: Random Forest")
print(f"SMOTE used: {used_smote}")
print("Binary classification was applied successfully.")
print("Moderate cases were excluded from the training dataset only.")
print("Outputs generated:")
print("- binary_model_predictions.csv")
print("- binary_confusion_matrix.png")

if Path("binary_feature_importance.csv").exists():
    print("- binary_feature_importance.csv")

if Path("binary_top_features.png").exists():
    print("- binary_top_features.png")