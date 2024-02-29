import pandas as pd
import matplotlib.pyplot as plt


data_filepath = "development/evaluate/retrieval/results/retrieval_result_scores_s10_k3.csv"

data = pd.read_csv(data_filepath)

# Group by pipeline_weight and calculate mean for binary_at_k and rank_score
grouped_data = data.groupby('pipeline_weight')[['binary_at_k', 'rank_score']].mean().reset_index()

# Plotting
plt.figure(figsize=(10, 6))

# Plotting both Binary at K and Rank Score on the same plot
plt.plot(grouped_data['pipeline_weight'], grouped_data['binary_at_k'], marker='o', linestyle='-', color='blue', label='Binary at K')
plt.plot(grouped_data['pipeline_weight'], grouped_data['rank_score'], marker='s', linestyle='-', color='red', label='Rank Score')

plt.title('Binary at K and Rank Score vs Pipeline Weight')
plt.xlabel('Pipeline Weight')
plt.ylabel('Score')
plt.grid(True)
plt.legend()

plt.tight_layout()


# save to file
plt.savefig("development/evaluate/retrieval/results/retrieval_result_scores_s10_k3.png")
 