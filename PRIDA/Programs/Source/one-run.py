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
    compile = subprocess.Popen(f"./compile.py prida+ -M -E spdz2k {N} {M}".split())
    compile.wait()
    p0 = subprocess.Popen(f"spdz2k-party.x prida+-{N}-{M} -p 0 -h 0.0.0.0 -N 2 --batch-size {BATCH_SIZE} > logs/p0_N{N}_M{M}.txt 2>&1", cwd="/usr/src/MP-SPDZ", shell=True)
    p1 = subprocess.Popen(f"spdz2k-party.x prida+-{N}-{M} -p 1 -h 0.0.0.0 -N 2 --batch-size {BATCH_SIZE} > logs/p1_N{N}_M{M}.txt 2>&1", cwd="/usr/src/MP-SPDZ", shell=True)
    do = [subprocess.Popen(f"./ExternalIO/data_owner.py {i} 2 {M}".split(), cwd="/usr/src/MP-SPDZ") for i in range(N)]
    dc = [subprocess.Popen(f"./ExternalIO/data_customer.py {N+i} 2 {M}".split(), cwd="/usr/src/MP-SPDZ") for i in range(M)]

    # Wait for clients
    for i, c in enumerate(do):
        success = wait_with_timeout(c, CLIENT_TIMEOUT)
        if not success:
            print(f"DO {i} killed after timeout")

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
    parser.add_argument('-N', type=int, default=10, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Number of Data Customers')

    args = parser.parse_args()
    CLIENT_TIMEOUT = args.timeout
    SERVER_TIMEOUT = 5
    N=args.N
    M=args.M
    BATCH_SIZE = args.batch_size
    main()
