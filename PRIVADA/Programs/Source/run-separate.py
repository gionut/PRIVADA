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
    print(f"Running {PROG}-N{N}-M{M}-B{BATCH_SIZE}-CB{DO_BATCH_SIZE}-{N_THREADS}-{RUN}")
    mem_prida = subprocess.Popen(f"python3 Programs/Source/mem_usage.py --duration {CLIENT_TIMEOUT} --file {LOG_DIR}/{PROG}-N{N}-M{M}-B{BATCH_SIZE}-DB{DO_BATCH_SIZE}-{N_THREADS}-{RUN}-mem.json --container pridaservice", shell=True)
    mem_do = subprocess.Popen(f"python3 Programs/Source/mem_usage.py --duration {CLIENT_TIMEOUT} --file {LOG_DIR}/do-N{N}-M{M}-B{BATCH_SIZE}-DB{DO_BATCH_SIZE}-{N_THREADS}-{RUN}-mem.json --container doservice", shell=True)
    processes = [subprocess.Popen(f"docker exec pridaservice sh -c \"python Programs/Source/run-prida.py --compile {COMPILE} --prog {PROG} -N {N} -M {M} --batch-size {BATCH_SIZE} --n-batch-size {DO_BATCH_SIZE} --timeout {CLIENT_TIMEOUT} --run {RUN} --n-threads {N_THREADS} --log-dir {LOG_DIR}\"", shell=True), 
    subprocess.Popen(f"docker exec doservice sh -c \"python ExternalIO/data_owner.py -M {M} -N {N} --batch-size {DO_BATCH_SIZE} --prob {PROB}\"", shell=True),
    ]
    
    wait_with_timeout(processes[1], timeout=CLIENT_TIMEOUT+5)    
    dc = subprocess.Popen(f"docker exec dcservice sh -c \"python ExternalIO/data_customer.py -M {M} --batch-size {DO_BATCH_SIZE}\"", shell=True)
    wait_with_timeout(processes[0], timeout=CLIENT_TIMEOUT+5)
    wait_with_timeout(dc, timeout=1)

    wait_with_timeout(mem_prida, timeout=1)
    wait_with_timeout(mem_do, timeout=1)
    print(f"Done running {PROG}-N{N}-M{M}-B{BATCH_SIZE}-CB{DO_BATCH_SIZE}-{N_THREADS}-{RUN}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluation framework for Prida+')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--prog', default="prida+", help='Program name')
    parser.add_argument('-N', type=int, default=10, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for preprocessing')
    parser.add_argument('--n-batch-size', type=int, default=500, help='Start Data Owners in batches')
    parser.add_argument('--run', type=int, default=1, help='run index')
    parser.add_argument('--n-threads', type=int, default=1, help='number of threads')
    parser.add_argument('--log-dir', default="logs", help='log dir name')
    parser.add_argument('--compile', type=int, default=1, help='log dir name')
    parser.add_argument('--prob', type=int, choices=[50, 60, 90, 100], default=100, help='Probability distribution for the choice vector')

    args = parser.parse_args()
    PROG = args.prog
    CLIENT_TIMEOUT = args.timeout
    SERVER_TIMEOUT = 5
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    DO_BATCH_SIZE=args.n_batch_size
    RUN = args.run
    N_THREADS = args.n_threads
    LOG_DIR = args.log_dir
    COMPILE = args.compile
    PROB = args.prob
    main()
