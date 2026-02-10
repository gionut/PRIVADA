import time
import json
import argparse


def monitor_container_memory(interval, duration, output_file):
    """
    Monitor container memory usage and save to file.
    
    Args:
        interval: Seconds between measurements
        duration: Total seconds to monitor (None = run until interrupted)
        output_file: File to save stats
    """
    start_time = time.time()
    used_mb = 0
    max_mem = 7620
    initial_usage = 0
    max_cpu_percent = 0
    prev_cpu_usage = 0

    try:
        # Open CPU cgroup files onc
        mem_usage_file = open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r')
        initial_usage = int(mem_usage_file.read().strip()) / (1024 ** 2)

        # Open CPU cgroup files once
        cpu_usage_file = open('/sys/fs/cgroup/cpuacct/cpuacct.usage', 'r')
        
        # Get initial CPU usage
        cpu_usage_file.seek(0)
        prev_cpu_usage = int(cpu_usage_file.read().strip())
        prev_time = time.time()

        while True:
            current_time = time.time()
            # Get memory stats
            mem_usage_file.seek(0)
            current = int(mem_usage_file.read().strip()) / (1024 ** 2)
            used_mb = max(used_mb, current)
            
            # Read CPU usage (in nanoseconds)
            cpu_usage_file.seek(0)
            current_cpu_usage = int(cpu_usage_file.read().strip())
            
            # Calculate CPU usage percentage
            time_delta = current_time - prev_time
            cpu_delta = current_cpu_usage - prev_cpu_usage
            
            if time_delta > 0:
                # Convert nanoseconds to seconds and calculate percentage
                cpu_percent = (cpu_delta / 1e9) / time_delta * 100
                
                if cpu_percent > max_cpu_percent:
                    max_cpu_percent = cpu_percent
                    max_cpu_timestamp = current_time
            
            prev_cpu_usage = current_cpu_usage
            prev_time = current_time

            if duration and (time.time() - start_time) >= duration:
                break
                
            time.sleep(interval)
    finally:
        # Close files
        mem_usage_file.close()
        cpu_usage_file.close()

    used_mb -= initial_usage
    percent = (used_mb / max_mem * 100) if max_mem != float('inf') else None
    stats = {
        'mem_used_mb': used_mb,
        'mem_percent': percent,
        'limit_mb': max_mem,
        'cpu_percent': max_cpu_percent,
        'num_cpus': 20,
    }
    with open(output_file, 'a') as f:
        f.write(json.dumps(stats) + '\n')
        f.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mem usage background monitor')
    parser.add_argument('--duration', type=int, default=10, help='Monitoring duration')
    parser.add_argument('--interval', type=int, default=0.5, help='Interval interval')
    parser.add_argument('--file', default="logs/mem_usage.jsonl", help='Output File')
    args = parser.parse_args()
    monitor_container_memory(interval=args.interval, duration=args.duration, output_file=args.file)