import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# 1) قراءة الداتا الجاهزة للكلستر
df = pd.read_csv("data/clustering_features.csv")

print("✅ Data loaded successfully!")
print(df.head())
print("\nShape:", df.shape)

# 2) Scaling
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)

print("\n✅ Data scaled successfully!")

# 3) Elbow Method
inertia = []
k_values = range(1, 6)

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

# رسم Elbow Method
plt.figure(figsize=(8, 5))
plt.plot(k_values, inertia, marker='o')
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method for Optimal k")
plt.show()


# 4) تطبيق KMeans
# اختار عدد الكلستر بعد مشاهدة الرسم
# مبدئيًا نخليه 3

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(scaled_data)

df["cluster"] = clusters

print("\n✅ Clustering completed!")
print(df.head())

# 5) حفظ النتائج

df.to_csv("data/clustering_results.csv", index=False)

print("\n✅ Results saved as data/clustering_results.csv")
pd.set_option('display.max_columns', None)
# 6) متوسط كل cluster
print("\nCluster Summary:")
print(df.groupby("cluster").mean().round(2))

# Cluster Visualization (Final)

cluster_summary = df.groupby("cluster").mean().round(2)
cluster_counts = df["cluster"].value_counts().sort_index()

x = cluster_summary["caffeine_per_day"]
y = cluster_summary["screen_hours"]

sizes = cluster_counts.values * 25
colors = ["#ff4fc3", "#19d4ff", "#9b5cff"]
labels = ["Cluster A", "Cluster B", "Cluster C"]

plt.style.use("dark_background")

fig, ax = plt.subplots(figsize=(10,6))

# خلفية الداشبورد
fig.patch.set_facecolor("#101935")
ax.set_facecolor("#101935")

# رسم الفقاعات
for i in range(len(cluster_summary)):
    
    ax.scatter(
        x.iloc[i],
        y.iloc[i],
        s=sizes[i],
        color=colors[i],
        alpha=0.8,
        edgecolors="white",
        linewidth=2,
        label=labels[i]
    )

    # نص الكلستر
    ax.text(
        x.iloc[i] + 0.01,
        y.iloc[i] + 0.03,
        f"{labels[i]}\nUsers: {cluster_counts.iloc[i]}",
        fontsize=11,
        weight="bold",
        color="white"
    )

# العنوان والمحاور
ax.set_title("Cluster Comparison Chart", fontsize=20, weight="bold", color="white")
ax.set_xlabel("Average Caffeine Intake (cups/day)", fontsize=12, color="white")
ax.set_ylabel("Average Screen Hours", fontsize=12, color="white")

# حدود الرسم
ax.set_xlim(1.35, 1.75)
ax.set_ylim(1.5, 8.5)

# الأرقام
ax.tick_params(colors="white")

# إطار الرسم
for spine in ax.spines.values():
    spine.set_color("white")

# الشبكة
ax.grid(True, color="white", alpha=0.15)

# legend تحت
legend = ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.1),
    ncol=3,
    facecolor="#101935",
    edgecolor="white",
    fontsize=11,
    markerscale=0.4
)

for text in legend.get_texts():
    text.set_color("white")

plt.tight_layout()

# حفظ الصورة
plt.savefig("data/cluster_visualization.png", dpi=300, facecolor="#101935")

plt.show()