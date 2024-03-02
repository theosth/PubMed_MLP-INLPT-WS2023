import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import development.commons.env as env

result_name = "retrieval_result_scores_s10_k3_rrf_ragas"
data_filepath = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}{result_name}.csv"
result_filepath = f"{env.RETRIEVAL_RESULT_FOLDER_PATH}{result_name}.png" 

data = pd.read_csv(data_filepath)

# Group by pipeline_weight and calculate mean for binary_at_k and rank_score
grouped_data = data.groupby('pipeline_weight')[['binary_at_k', 'rank_score']].mean().reset_index()

# Set style
sns.set_style("whitegrid")

# Create a figure and a set of subplots
fig, ax = plt.subplots(figsize=(10, 6))

# Plotting both Binary at K and Rank Score on the same plot
sns.lineplot(x='pipeline_weight', y='binary_at_k', data=grouped_data, marker='o', ax=ax, label='Binary at K')
sns.lineplot(x='pipeline_weight', y='rank_score', data=grouped_data, marker='s', ax=ax, label='Rank Score')

# Set title and labels for axes
ax.set_title('Binary at K and Rank Score vs Pipeline Weight', fontsize=16)
ax.set_xlabel('Pipeline Weight', fontsize=14)
ax.set_ylabel('Score', fontsize=14)

# Set the legend
ax.legend()

# Tight layout
plt.tight_layout()

# Save to file
plt.savefig(result_filepath)