"""
Evaluation script to start batched evaluation. The default batch size is 10
"""
import argparse
import subprocess
import time

def wait_with_timeout(process, timeout):
    """Wait for process with timeout, kill if exceeded"""
    try:
        process.wait(timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        return False

def main():
    if COMPILE == 1:
        compile = subprocess.Popen(f"docker exec pridaservice sh -c \"./compile.py {PROG} -M -E spdz2k {N} {M} {DO_BATCH_SIZE} {N_THREADS}\"", shell=True)
        compile.wait()
        time.sleep(5)

    for run_idx in range(TIMES):
        p = subprocess.Popen(f"""python Programs/Source/run-separate.py \
        -M {M} \
        -N {N} \
        --compile 0 \
        --batch-size {BATCH_SIZE} \
        --n-batch-size {DO_BATCH_SIZE} \
        --prog {PROG} \
        --timeout {CLIENT_TIMEOUT} \
        --run {run_idx} \
        --n-threads {N_THREADS} \
        --prob {PROB} \
        --log-dir {LOG_DIR}""", shell=True)
        wait_with_timeout(p, timeout=CLIENT_TIMEOUT+5)
    
    print("Done")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluation framework for Prida+')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--prog', default="prida+", help='Program name')
    parser.add_argument('-N', type=int, default=10, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for preprocessing')
    parser.add_argument('--n-batch-size', type=int, default=500, help='Start Data Owners in batches')
    parser.add_argument('--n-threads', type=int, default=1, help='number of threads')
    parser.add_argument('--log-dir', default="logs", help='log dir name')
    parser.add_argument('--times', type=int, default=10, help='number of executions')
    parser.add_argument('--compile', type=int, default=1, help='compile the program')
    parser.add_argument('--prob', type=int, choices=[50, 60, 90, 100], default=100, help='Probability distribution for the choice vector')

    args = parser.parse_args()
    PROG = args.prog
    CLIENT_TIMEOUT = args.timeout
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    DO_BATCH_SIZE=args.n_batch_size
    TIMES = args.times
    N_THREADS = args.n_threads
    LOG_DIR = args.log_dir
    COMPILE = args.compile
    PROB = args.prob
    main()
