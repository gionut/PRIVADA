### Find a way to import mpc files as modules

class ClientConnectionManager:
    def send_to_clients(self, n_clients, values, portnum):
        # Start listening for client socket connections
        listen_for_clients(portnum)
        print_ln('Listening for output client connections on base port %s', portnum)

        self.seen = Array(n_clients, regint)
        self.seen.assign_all(0)
        # Loop round waiting for each client to connect
        @do_while
        def client_connections():
            client_socket_id = accept_client_connection(portnum)
            @if_(client_socket_id >= n_clients)
            def _():
                print_ln('client id too high')
                crash()
            self.seen[client_socket_id] = 1
            
            return (sum(self.seen) < n_clients)

        @for_range(0, n_clients)
        def _(i):
            sint.reveal_to_clients(i, [values[i]])
        
        @for_range(0, n_clients)
        def _(i):
            closeclientconnection(i)

    def receive_from_clients(self, t, n_clients, size, portnum, batch_size):
        if batch_size is None:
            batch_size = n_clients

        client_values = t.Matrix(n_clients, size)
        
        # Start listening for client socket connections
        listen_for_clients(portnum)
        print_ln('Listening for input client connections on base port %s', portnum)
        
        n_batches = (n_clients + batch_size - 1) // batch_size
        for batch_idx in range(n_batches):
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, n_clients)
            actual_batch_size = batch_end - batch_start
            print_ln('Processing batch %s: clients %s to %s', batch_idx, batch_start, batch_end - 1)
            
            self.seen = Array(actual_batch_size, regint)
            self.seen.assign_all(0)
            # Loop round waiting for each client to connect
            @do_while
            def client_connections():
                client_socket_id = accept_client_connection(portnum)
                @if_(client_socket_id >= batch_start+actual_batch_size)
                def _():
                    print_ln('client id too high')
                    crash()
                self.seen[client_socket_id-batch_start] = 1
                
                return (sum(self.seen) < actual_batch_size)
                    
            @for_range_multithread(n_threads=1, n_parallel=1, n_loops=actual_batch_size)
            def _(offset):
                idx = batch_start + offset
                client_values[idx] = t.receive_from_client(size, idx)
            
            @for_range(batch_start, batch_end)
            def _(i):
                closeclientconnection(i)
            print_ln('Batch %s completed and connections closed', batch_idx)

        return client_values

def receive_data(ccm, N, M, batch_size):
    shares = ccm.receive_from_clients(sint, N, 2*M, 14000, batch_size)
    cv = sint.Matrix(N, M)
    d = sint.Matrix(N, M)
    for id in range(N):
        cv[id] = shares[id][:M]
        d[id] = shares[id][M:]

    return (cv, d)

def preliminary_counting(cv, N, M):
    result = sint.Array(M)
    result.assign_all(0)

    for i in range(N):
        for j in range(M):
            result[j] += cv[i][j]

    return result

def main():
    N = int(program.args[1]) # Data Owners
    M = int(program.args[2]) # Data Customers
    batch_size = int(program.args[3]) # Batch size for DO connections
    threshold = N//2+1
    
    ccm = ClientConnectionManager()

    (cv, d) = receive_data(ccm, N, M, batch_size)
    cv_total = preliminary_counting(cv, N, M).reveal_list()
    whitelist = [cv_j >= threshold for cv_j in cv_total]

    res = sint.Array(M)
    res.assign_all(0)
    for j in range(M):
        @if_(whitelist[j] == 1)
        def _():
            for i in range(N):
                res[j] += d[i][j]
    
    ccm.send_to_clients(M, res, 15000)

    
main()