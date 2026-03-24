#!/usr/bin/python3
import sys
import threading
import random
import argparse
sys.path.append('.')
from client import Client

def run_client(client_id, data):
    """
    client_id - The DO numbered as `client_id` connects to [pridaservice:14000] to send its private input.
                `pridaservice` is the docker container domain name in the `pridanet` virtual network.
    M - The number of DCs range(0, M)
    """
    client = Client(['pridaservice'] * 2, 14000, client_id)
    client.send_private_inputs(data)

def main():
    parser = argparse.ArgumentParser(description='Script for starting Data Owners')
    parser.add_argument('-N', type=int, default=100, help='Number of Data Owners')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for network throttling. Only `batch-size` clients will try to open connections with the aggregators at any time.')
    parser.add_argument('--prob', type=int, choices=[50, 60, 90, 100], default=100, help='Probability distribution for the choice vector')

    args = parser.parse_args()
    M = args.M
    N = args.N
    batch_size = args.batch_size
    p = args.prob / 100
    print("Starting DOs")
    # Initialize the choice vector so that each DC has a `p` chance of being chosen
    cv = [1 if random.random() < p else 0 for _ in range(M)]
    d = [10 * choice for choice in cv]
    data = cv + d

    for batch_start in range(0, N, batch_size):
        batch_ids = range(batch_start, min(batch_start + batch_size, N))
        threads = [
            threading.Thread(target=run_client, args=(i, data))
            for i in batch_ids
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    
    print(f"Data Customers should receive {10*N}")

if __name__ == '__main__':
    main()