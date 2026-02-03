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

    def receive_from_clients(self, t, n_clients, size, portnum):
        client_values = t.Matrix(n_clients, size)
        
        # Start listening for client socket connections
        listen_for_clients(portnum)
        print_ln('Listening for input client connections on base port %s', portnum)

        # Start batching
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
                
        @for_range_multithread(n_threads=1, n_parallel=1, n_loops=n_clients)
        def _(i):
            client_values[i] = t.receive_from_client(size, i)
        
        @for_range(0, n_clients)
        def _(i):
            closeclientconnection(i)

        return client_values

def receive_data(ccm, N, M):
    shares = ccm.receive_from_clients(sint, N, 2*M, 14000)
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
    N = 10  # Data Owners
    M = 1 # Data Customers
    threshold = N//2+1
    
    ccm = ClientConnectionManager()

    (cv, d) = receive_data(ccm, N, M)
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