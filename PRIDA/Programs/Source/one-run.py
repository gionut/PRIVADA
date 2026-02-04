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
    compile = subprocess.Popen(f"./compile.py {PROG} -M -E spdz2k {N} {M} {DO_BATCH_SIZE}".split())
    compile.wait()
    p0 = subprocess.Popen(f"spdz2k-party.x {PROG}-{N}-{M}-{DO_BATCH_SIZE} -p 0 -h 0.0.0.0 -N 2 -v --batch-size {BATCH_SIZE} > logs/p0_N{N}_M{M}.txt 2>&1", cwd="/usr/src/MP-SPDZ", shell=True)
    p1 = subprocess.Popen(f"spdz2k-party.x {PROG}-{N}-{M}-{DO_BATCH_SIZE} -p 1 -h 0.0.0.0 -N 2 --batch-size {BATCH_SIZE} > logs/p1_N{N}_M{M}.txt 2>&1", cwd="/usr/src/MP-SPDZ", shell=True)
    
    
    n_batches = (N + DO_BATCH_SIZE - 1) // DO_BATCH_SIZE
    for batch_idx in range(n_batches):
        batch_start = batch_idx * DO_BATCH_SIZE
        batch_end = min(batch_start + DO_BATCH_SIZE, N)
        do = [subprocess.Popen(f"./ExternalIO/data_owner.py {i} 2 {M}".split(), cwd="/usr/src/MP-SPDZ") for i in range(batch_start, batch_end)]
        # Wait for DO batch to finish
        for i, c in enumerate(do):
            success = wait_with_timeout(c, CLIENT_TIMEOUT)
            if not success:
                print(f"DO {batch_start + i} killed after timeout")

    dc = [subprocess.Popen(f"./ExternalIO/data_customer.py {i} 2 {M}".split(), cwd="/usr/src/MP-SPDZ") for i in range(M)]
    for i, c in enumerate(dc):
        success = wait_with_timeout(c, CLIENT_TIMEOUT)
        if not success:
            print(f"DC {i} killed after timeout")

    # Servers should exit now, but force if needed
    for name, p in [("p0", p0), ("p1", p1)]:
        success = wait_with_timeout(p, SERVER_TIMEOUT)
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

    args = parser.parse_args()
    PROG = args.prog
    CLIENT_TIMEOUT = args.timeout
    SERVER_TIMEOUT = 5
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    DO_BATCH_SIZE=args.n_batch_size
    main()
