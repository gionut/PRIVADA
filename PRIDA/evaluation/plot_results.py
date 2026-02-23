import os
import re
import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt

LOG_DIR = sys.argv[1]

def parse_filename(filename):
    pattern = r"p0_N(\d+)_M(\d+)_B(\d+)_CB(\d+)_(\d+)_(\d+)"
    m = re.match(pattern, filename)
    if m == None:
        return None
    return {
        "N": int(m.group(1)),
        "M": int(m.group(2)),
        "batch_size": int(m.group(3)),
        "do_batch_size": int(m.group(4)),
        "n_threads": int(m.group(5)),
        "run": int(m.group(6)),
    }

def parse_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    match = re.search(r"([\d.]+) threads spent", content)
    threads = float(match.group(1)) if match else 1.0

    match = re.search(r"([\d.]+) seconds idling", content)
    idling_time =  float(match.group(1)) if match else 1.0

    cpu_time = float(re.search(r"CPU time = ([\d.]+)", content).group(1))
    client_communication = float(re.search(r"Time1 = ([\d.]+)", content).group(1))
    preliminary_count = float(re.search(r"Time2 = ([-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+)", content).group(1))
    aggregation = float(re.search(r"Time3 = ([-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+)", content).group(1))
    cc = float(re.search(r"Time4 = ([-+]?\d*\.\d+(?:[eE][-+]?\d+)?|\d+)", content).group(1))
    total_time = float(re.search(r"Time = ([\d.]+)", content).group(1))
    phase_match = re.search(
        r"pent.*? ([\d.]+) seconds.*?online phase.*? ([\d.]+) seconds.*?offline phase", content
    )
    online_time = float(phase_match.group(1))
    offline_time = float(phase_match.group(2))

    data_sent = float(re.search(r"Data sent = ([\d.]+) MB", content).group(1))
    global_data_sent = float(re.search(r"Global data sent = ([\d.]+) MB", content).group(1))

    return {
        "cpu_time": cpu_time,
        "offline_time": offline_time,
        "idling_time": idling_time / threads,
        "online_time": online_time,
        "total_time": total_time,
        "client_communication_time": client_communication + cc,
        "preliminary_count_time": preliminary_count,
        "aggregation_time": aggregation,
        "data_sent": data_sent,
        "global_data_sent": global_data_sent,
    }

results = []

for filename in sorted(os.listdir(LOG_DIR)):
    filepath = os.path.join(LOG_DIR, filename)
    file_params = parse_filename(filename)
    if file_params == None: 
        continue
    file_metrics = parse_file(filepath)
    results.append({**file_params, **file_metrics})

fieldnames = ["N", "M", "batch_size", "do_batch_size", "n_threads", "run",
              "cpu_time", "offline_time", "online_time", "total_time", "idling_time",
              "client_communication_time", "preliminary_count_time", "aggregation_time", "data_sent", "global_data_sent"]

with open("plot_results_logs.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

df = pd.read_csv("plot_results_logs.csv")
column = sys.argv[2]
avg = df.groupby(column).agg(
    online_time=("online_time", "mean"),
    idling_time=("idling_time", "mean"),
    offline_time=("offline_time", "mean"),
    client_communication_time=("client_communication_time", "mean"),
    total_time=("total_time", "mean"),
    preliminary_count_time=("preliminary_count_time", "mean"),
    aggregation_time=("aggregation_time", "mean"),
    cpu_time=("cpu_time", "mean"),
).reset_index().sort_values(column)

avg.to_csv('plot_results_avg.csv', index=False)
# Plot 1: online, offline, client_communication, total time
fig, ax = plt.subplots(figsize=(9, 5))
avg = avg.iloc[:, :]
# ax.plot(avg[column], avg["online_time"], marker="o", label="Online Phase")
ax.plot(avg[column], avg["offline_time"], marker="o", label="Offline Phase")
ax.plot(avg[column], avg["client_communication_time"], marker="o", label="Client Communication")
ax.plot(avg[column], avg["total_time"], marker="o", label="Total")
ax.set_xlabel(column)
ax.set_ylabel("Time (seconds)")
ax.set_title("Phase Times vs " + column)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig("plot_results_times.png", dpi=150)

# Plot 2: cpu_time
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(avg[column], avg["cpu_time"], marker="o", color="tab:orange", label="CPU Time")
ax.set_xlabel(column)
ax.set_ylabel("Time (seconds)")
ax.set_title("CPU Time vs " + column)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig("plot_results_cpu.png", dpi=150)

# Plot 3: preliminary and aggregation
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(avg[column], avg["preliminary_count_time"], marker="o", label="Preliminary Count Time")
ax.plot(avg[column], avg["aggregation_time"], marker="o", label="Aggregation Time")
ax.plot(avg[column], avg["preliminary_count_time"] + avg["aggregation_time"], marker="o", label="Total")
ax.set_xlabel(column)
ax.set_ylabel("Time (seconds)")
ax.set_title("Phase Times vs " + column)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig("plot_results_mpc.png", dpi=150)