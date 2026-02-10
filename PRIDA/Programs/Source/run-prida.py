import subprocess
import time
import argparse

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
        compile = subprocess.Popen(f"./compile.py {PROG} -M -E spdz2k {N} {M} {DO_BATCH_SIZE} {N_THREADS}".split())
        compile.wait()
    p0 = subprocess.Popen(f"spdz2k-party.x {PROG}-{N}-{M}-{DO_BATCH_SIZE}-{N_THREADS} -p 0 -h 0.0.0.0 -N 2 -v --batch-size {BATCH_SIZE} > {LOG_DIR}/p0_N{N}_M{M}_B{BATCH_SIZE}_CB{DO_BATCH_SIZE}_{N_THREADS}_{RUN}.txt 2>&1", cwd="/usr/src/MP-SPDZ", shell=True)
    p1 = subprocess.Popen(f"spdz2k-party.x {PROG}-{N}-{M}-{DO_BATCH_SIZE}-{N_THREADS} -p 1 -h 0.0.0.0 -N 2 --batch-size {BATCH_SIZE} > {LOG_DIR}/p1_N{N}_M{M}_B{BATCH_SIZE}_CB{DO_BATCH_SIZE}_{N_THREADS}_{RUN}.txt 2>&1" , cwd="/usr/src/MP-SPDZ", shell=True)
    
    for name, p in [("p0", p0), ("p1", p1)]:
        success = wait_with_timeout(p, TIMEOUT)
        if not success:
            print(f"{name} killed after timeout")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluation framework for Prida+')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--prog', default="prida+", help='Program name')
    parser.add_argument('-N', type=int, default=10, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for preprocessing')
    parser.add_argument('--n-batch-size', type=int, default=500, help='Start Data Owners in batches')
    parser.add_argument('--log-dir', default="logs", help='Log dir name')
    parser.add_argument('--run', type=int, default=1, help='Run index')
    parser.add_argument('--n-threads', type=int, default=1, help='Number of threads')
    parser.add_argument('--compile', type=int, default=1, help='Number of threads')

    args = parser.parse_args()
    PROG = args.prog
    TIMEOUT = args.timeout
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    DO_BATCH_SIZE=args.n_batch_size
    RUN = args.run
    LOG_DIR = args.log_dir
    N_THREADS = args.n_threads
    COMPILE = args.compile
    main()
