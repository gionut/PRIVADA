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
    dc = [subprocess.Popen(f"./ExternalIO/data_customer.py {i} 2 {M}".split(), cwd="/usr/src/MP-SPDZ") for i in range(M)]
    for i, c in enumerate(dc):
        success = wait_with_timeout(c, CLIENT_TIMEOUT)
        if not success:
            print(f"DC {i} killed after timeout")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluation framework for Prida+')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--prog', default="prida+", help='Program name')
    parser.add_argument('-N', type=int, default=10, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for preprocessing')
    parser.add_argument('--n-batch-size', type=int, default=500, help='Start Data Owners in batches')

    args = parser.parse_args()
    PROG = args.prog
    CLIENT_TIMEOUT = args.timeout
    SERVER_TIMEOUT = 5
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    DO_BATCH_SIZE=args.n_batch_size
    main()
