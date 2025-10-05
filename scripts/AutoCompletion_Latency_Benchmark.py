
################################## Benchmarking Script ##################################
# This script benchmarks the latency of the autocomplete service

# you have to add username and password for authentication
# to the script before running it.
# upload the dataset that has three columns (text, length and language)
import time
import requests
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

ENDPOINT_URL = "http://127.0.0.1:8000/api/v1/autocomplete"


# Main benchmark function
def benchmark_autocomplete(csv_file: str):

    df = pd.read_csv(csv_file, usecols=[0, 1, 2])

    results = []
    max_predictions_choices = [2, 4, 5, 10]
    latencies = []

    for idx, row in df.iterrows():
        data = {
            "input": str(row['text']),
            "max_predictions": int(np.random.choice(max_predictions_choices)),
            "output_language": str(row['language'])
        }

        start_time = time.time()
        response = requests.post(ENDPOINT_URL, json=data, headers=headers)
        elapsed = (time.time() - start_time) * 1000  # milliseconds

        if response.ok:
            suggestions = response.json()['data']['suggestions']
        else:
            suggestions = []

        latency_sec = elapsed / 1000
        rps = 1 / latency_sec if latency_sec else 0  # throughput per request

        results.append({
        "texts": row['text'],
        "character_length": row['length'],
        "max_predictions": data["max_predictions"],
        "lang": row['language'],
        "latency_ms": elapsed,
        "rps": rps,
        "suggestions": len(suggestions)
        # "suggestions": suggestions   # Uncomment when you want to print the suggestions of dataset
        })

    latencies = [res["latency_ms"] for res in results]
    p95_latency = np.percentile(latencies, 95)
    avg_latency = np.mean(latencies)
    total_requests = len(df)
    total_time_seconds = sum(latencies) / 1000
    rps = total_requests / total_time_seconds if total_time_seconds else 0

    # Build Markdown table
    lines = [
        "| texts | character length | max_predictions | lang | latency_ms | Throughput (req/sec) | suggestions |",
        "|------:|-----------------:|----------------:|:----:|-----------:|----:|------------:|",
    ]

    for res in results:
        lines.append(
            f"| {res['texts'][:30]:>30} | {res['character_length']:>15} | {res['max_predictions']:>14} | {res['lang']:>4} | {res['latency_ms']:10.2f} | {res['rps']:5.2f} | {res['suggestions']:>11} |"
        )

    # Overall P95
    lines.append(f"\n**Overall P95 latency:** {p95_latency:.2f} ms")
    lines.append(f"**Average latency:** {avg_latency:.2f} ms")
    lines.append(f"**Overall RPS:** {rps:.2f}")

    markdown_table = "\n".join(lines)
    print(markdown_table)
    df = pd.DataFrame(results)

    # 1. Latency vs Character Length (max_predictions fixed, say = 4)
    fixed_max_pred = 4
    df1 = df[df['max_predictions'] == fixed_max_pred]
    plt.figure(figsize=(8, 5))
    plt.plot(df1['character_length'], df1['latency_ms'], marker='o')
    plt.title(f'Latency vs Character Length (max_predictions={fixed_max_pred})')
    plt.xlabel('Character Length')
    plt.ylabel('Latency (ms)')
    plt.grid(True)
    plt.show()

    # 2. Latency vs Max Predictions (character length fixed, say = 30)
    fixed_char_len = 30
    df2 = df[df['character_length'] == fixed_char_len]
    plt.figure(figsize=(8, 5))
    plt.plot(df2['max_predictions'], df2['latency_ms'], marker='o')
    plt.title(f'Latency vs Max Predictions (character_length={fixed_char_len})')
    plt.xlabel('Max Predictions')
    plt.ylabel('Latency (ms)')
    plt.grid(True)
    plt.show()

    # 3. Throughput vs Max Predictions (character length fixed, say = 30)
    plt.figure(figsize=(8, 5))
    plt.plot(df2['max_predictions'], df2['rps'], marker='o')
    plt.title(f'Throughput vs Max Predictions (character_length={fixed_char_len})')
    plt.xlabel('Max Predictions')
    plt.ylabel('Throughput (req/sec)')
    plt.grid(True)
    plt.show()

    # Uncomment when you want to print the suggestions of dataset
    # for res in results:
    #     print(
    #         f" text:  {res['texts']} \n characters: {res['character_length']} \n Amount of predictions {res['max_predictions']} suggestions: \n {res['suggestions']}  \n"
    #         " ------------------------------------------------------------------------------------------ \n"
    #     )


# # Run the benchmark
benchmark_autocomplete("/mnt/c/Users/SyedAfrazShah/OneDrive - Automotive Artificial Intelligence (AAI) GmbH/Documents/repos/GEN-708/legal_sentences_dataset.csv")
# # Uncomment when you want to print the suggestions of dataset
# # benchmark_autocomplete("/mnt/c/Users/SyedAfrazShah/OneDrive - Automotive Artificial Intelligence (AAI) GmbH/Documents/repos/GEN-708/legal_sen_database_suggestions.csv")
