import time
import json
import argparse
import os
import docker

def monitor_container_memory(interval, duration, output_file, container_name):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        print(f"Error: Container '{container_name}' not found.")
        return

    stats_gen = container.stats(stream=True, decode=True)
    mem_usage = mem_limit = 0
    cpu_percent = 0
    initial_rx = initial_tx = 0
    prev_cpu_total = 0.0
    prev_system_total = 0.0
    online_cpus = 20
    start_time = time.time()
    try:
        for stats in stats_gen:
            current_time = time.time()
            if current_time - start_time > duration:
                break

           # --- CPU Calculation ---
            cpu_stats = stats.get('cpu_stats', {})
            # Use .get() to avoid KeyErrors if the dictionary is thin
            cpu_usage = cpu_stats.get('cpu_usage', {})
            
            curr_cpu_total = cpu_usage.get('total_usage', 0)
            curr_system_total = cpu_stats.get('system_cpu_usage', 0)
            
            # Calculate Deltas
            cpu_delta = curr_cpu_total - prev_cpu_total
            system_delta = curr_system_total - prev_system_total
            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_percent = max(cpu_percent, (cpu_delta / system_delta) * online_cpus * 100.0)
            
            # Update previous values for the next iteration
            prev_cpu_total = curr_cpu_total
            prev_system_total = curr_system_total

            # --- Memory & Network (Standard) ---
            crt_mem = stats['memory_stats'].get('usage', 0) / (1024 * 1024)
            mem_usage = max(mem_usage, crt_mem)
            networks = stats.get('networks', {})['eth0']
            if initial_rx == 0:
                initial_rx = networks['rx_bytes'] / 1024
                initial_tx = networks['tx_bytes'] / 1024
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        mem_limit = stats['memory_stats']['limit'] / (1024 * 1024)
        rx, tx = networks['rx_bytes'] / 1024 - initial_rx, networks['tx_bytes'] / 1024 - initial_tx
        stats_gen.close()

    stats = {
        'mem_usage': mem_usage,
        'mem_limit': mem_limit,
        'cpu_percent': cpu_percent,
        'rx_total': rx,
        'tx_total': tx,
    }
    with open(output_file, 'a') as f:
        f.write(json.dumps(stats) + '\n')
        f.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mem usage background monitor')
    parser.add_argument('--duration', type=int, default=10, help='Monitoring duration')
    parser.add_argument('--interval', type=int, default=0.5, help='Interval interval')
    parser.add_argument('--file', default="logs/mem_usage.jsonl", help='Output File')
    parser.add_argument('--container', default="", help='Container Name')
    args = parser.parse_args()
    monitor_container_memory(interval=args.interval, duration=args.duration, output_file=args.file, container_name=args.container)