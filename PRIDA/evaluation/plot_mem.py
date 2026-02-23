import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import io
import sys
import numpy as np


def parse_benchmark_files(directory):
    data_list = []
    
    # This regex captures: PROG, N, M, BATCH, DO_BATCH, THREADS, and RUN
    # It handles both the "do-" prefix and the standard format
    file_pattern = re.compile(
        r"(?:do-)?(?P<PROG>.+?)-N(?P<N>\d+)-M(?P<M>\d+)-B(?P<BATCH>\d+)-DB(?P<DO_BATCH>\d+)-(?P<THREADS>\d+)-(?P<RUN>\d+)-mem\.json"
    )

    for filename in os.listdir(directory):
        match = file_pattern.match(filename)
        if match:
            # 1. Extract metadata from the filename
            metadata = match.groupdict()
            
            # 2. Load the JSON metrics
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as f:
                    metrics = json.load(f)
                
                # Combine metadata and metrics into one dictionary
                combined_entry = {**metadata, **metrics}
                data_list.append(combined_entry)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {filename}: {e}")

    # 3. Convert to Pandas DataFrame
    df = pd.DataFrame(data_list)
    
    # Convert numeric columns from strings to actual numbers
    numeric_cols = ['N', 'M', 'BATCH', 'DO_BATCH', 'THREADS', 'RUN']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
    
    return df

# --- Execution ---
data_dir = sys.argv[1]  # Change this to your folder path
df = parse_benchmark_files(data_dir)

# 2. Define your "Configuration" columns and your "Metric" columns
config_cols = ['PROG', 'N', 'M', 'BATCH', 'DO_BATCH', 'THREADS']
metric_cols = ['mem_usage', 'mem_limit', 'cpu_percent', 'rx_total', 'tx_total']

column = sys.argv[2]

avg = df.groupby(column).agg(
    mem_usage=("mem_usage", "mean"),
    cpu_percent=("cpu_percent", "mean"),
    rx_total=("rx_total", "mean"),
    tx_total=("tx_total", "mean"),
).reset_index().sort_values(column)
# 3. Group by the configuration and calculate the mean
# We exclude 'RUN' from the grouping because we want to average across it
df = df.groupby(config_cols)[metric_cols].mean().reset_index()
# 5. Save the averaged results
df.to_csv('plot_mem_avg.csv', index=False)

# To handle multiple programs, we group by 'PROG'
df['PROG'] = np.where(df['PROG'] == 'do', 'client container', 'parties container')
programs = df['PROG'].unique()

# --- Plot 1: Memory Usage and CPU Usage ---
plt.figure(figsize=(12, 6))

# Subplot for Memory
plt.subplot(1, 2, 1)
for prog in programs:
    subset = df[df['PROG'] == prog].sort_values('M')
    plt.plot(subset[column], subset['mem_usage'], marker='o', label=f'{prog}')
plt.title('Memory Usage vs ' + column)
plt.xlabel(column)
plt.ylabel('Memory Usage (MB)')
plt.legend()
plt.grid(True)

# Subplot for CPU
plt.subplot(1, 2, 2)
for prog in programs:
    subset = df[df['PROG'] == prog].sort_values(column)
    plt.plot(subset[column], subset['cpu_percent'], marker='x', linestyle='--', label=f'{prog}')
plt.title('CPU Usage (%) vs ' + column)
plt.xlabel(column)
plt.ylabel('CPU %')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('plot_mem_resources.png')

# --- Plot 2: RX and TX Total ---
plt.figure(figsize=(10, 6))
for prog in programs:
    subset = df[df['PROG'] == prog].sort_values(column)
    plt.plot(subset[column], subset['rx_total'], marker='o', label=f'{prog} - RX')
    plt.plot(subset[column], subset['tx_total'], marker='s', linestyle=':', label=f'{prog} - TX')

plt.title('Network Traffic (RX/TX) vs ' + column)
plt.xlabel(column)
plt.ylabel('Total Traffic')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('plot_mem_traffic.png')

print("Processing complete. Plots saved as 'plot_mem_resources.png' and 'plot_mem_traffic.png'.")