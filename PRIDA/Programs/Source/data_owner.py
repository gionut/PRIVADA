#!/usr/bin/python3

import sys

sys.path.append('.')

from client import *
from domains import *

client_id = int(sys.argv[1])
n_parties = int(sys.argv[2])
M = int(sys.argv[3])

client = Client(['0.0.0.0'] * n_parties, 14000, client_id)

def run():
    cv = [1] * M
    d = [10] * M
    x = cv + d
    client.send_private_inputs(x)

run()
