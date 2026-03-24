#!/usr/bin/python3
import sys
import threading
import argparse
sys.path.append('.')
from client import Client

def run_client(client_id):
    """
    client_id - The DC numbered as connects to [pridaservice:15000] to receive its private result.
    `pridaservice` is the docker container domain name in the `pridanet` virtual network
    """
    client = Client(['pridaservice'] * 2, 15000, client_id)
    print(f'Aggregation result for DC{client_id}: ', client.receive_outputs(1)[0])

def main():
    parser = argparse.ArgumentParser(description='Script for starting Data Customers')
    parser.add_argument('-M', type=int, default=1, help='Number of Data Customers')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for network throttling. Only `batch-size` clients will try to open connections with the aggregators at any time.')
    args = parser.parse_args()
    M = args.M
    batch_size = args.batch_size
    print("Starting DCs")
    for batch_start in range(0, M, batch_size):
        batch_ids = range(batch_start, min(batch_start + batch_size, M))
        threads = [
            threading.Thread(target=run_client, args=(i,))
            for i in batch_ids
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

if __name__ == '__main__':
    main()