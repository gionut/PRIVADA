#!/usr/bin/python3

import sys

sys.path.append('.')

from client import *
from domains import *

client_id = int(sys.argv[1])
n_parties = int(sys.argv[2])

client = Client(['0.0.0.0'] * n_parties, 14000, client_id)


def run():
    print(f'Aggregation result for DC{client_id}: ', client.receive_outputs(1)[0])

run()