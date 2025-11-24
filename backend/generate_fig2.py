import matplotlib.pyplot as plt
import numpy as np

# Fix IEEE-style font
plt.rcParams.update({
    "font.size": 10,
    "figure.dpi": 300,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "legend.fontsize": 9
})

# Models
models = ["TF-IDF", "BM25", "Hybrid"]

# Metrics from your table
precision = [0.63, 0.74, 0.81]
recall = [0.55, 0.63, 0.69]
f1 = [0.58, 0.68, 0.74]
ndcg = [0.68, 0.76, 0.83]

# Data grouped
metrics = [precision, recall, f1, ndcg]
metric_names = ["P@10", "R@10", "F1", "nDCG"]

x = np.arange(len(models))  # [0,1,2]
width = 0.2  # Width of bars

fig, ax = plt.subplots(figsize=(7,4))

# Plot each metric as grouped bars
for i, metric in enumerate(metrics):
    ax.bar(x + i*width, metric, width, label=metric_names[i])

# Labels and styling
ax.set_xticks(x + width*1.5)
ax.set_xticklabels(models)
ax.set_ylabel("Score")
ax.set_title("Performance Comparison of TF-IDF, BM25, and Hybrid Models")
ax.legend()

# Tight layout for IEEE formatting
plt.tight_layout()

# Save figure
plt.savefig("fig2_performance.png")
print("Saved fig2_performance.png successfully!")
