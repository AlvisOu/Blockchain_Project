import socket, json, time, threading
from blockchain import Chain, Wallet, Transaction, Block

# TODO: blockchain specific functions, node-to-node message protocol, thread locks

class Peer:
    """
        Peer class that functions as each node in the network.
    """
    def __init__(self, port: int, name: str, tracker_addr: int, tracker_port: int):
        self.tracker_addr = tracker_addr
        self.tracker_port = tracker_port
        self.port = port
        self.peers = {} # tentatively {"addre:port" as one peer_id string : socket}
        self.wallet = Wallet(name=name)
        self.chain = Chain()
        self.socket_to_tracker = None

    def connect_to_tracker(self):
        try:
            self.socket_to_tracker = socket.create_connection((self.tracker_addr, self.tracker_port)) # create_connection is more robust than socket.connect then socket.bind
            print(f"[connect_to_tracker] tracker connected at {self.tracker_addr}:{self.tracker_port}")
        except Exception as e:
            print(f"[connect_to_tracker] error: {e}")

    def get_peer_list(self):
        """
            Get the list of peers from the tracker.
        """
        try:
            # for Sky: can data be formatted like:
            # data = '[ "192.168.1.5:5000", "192.168.1.6:5000" ]'
            self.socket_to_tracker.sendall(b"GET_PEER_LIST")
            data = self.socket_to_tracker.recv(4096).decode()
            peer_list = json.loads(data)
            return peer_list
        except Exception as e:
            print(f"[get_peer_list] error: {e}")
            return []
        
    def form_peer_connections(self):
        peers = self.get_peer_list()
        for peer in peers:
            if peer == f"localhost:{self.port}":
                continue # Don't connect to self
            
            if peer not in self.peers:
                try:
                    ip, port = peer.split(":")
                    sock = socket.create_connection((ip, int(port)))
                    peer_id = f"{ip}:{port}"
                    self.peers[peer_id] = sock
                    print(f"[form_peer_connections] connected to{peer}")
                    threading.Thread(target=self.receive_from_peer, args=(sock, peer_id), daemon=True).start()
                except Exception as e:
                    print(f"[refresh_peer_connections] connection error: {e}")
            
        self.last_refresh = time.time()

    def listener_thread(self):
        listenr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenr.bind(("localhost", self.port))
        listenr.listen()
        print(f"[listener_thread] listening for {self.port}")

        while True:
            conn, addr = listenr.accept()
            peer_id = f"{addr[0]}:{addr[1]}"
            self.peers[peer_id] = conn
            threading.Thread(target=self.receive_from_peer, args=(conn, peer_id), daemon=True).start()

    def receive_from_peer(self, conn, peer_id):
        with conn:
            try:
                buffer = ""
                while True:
                    data = conn.recv(4096).decode()
                    if not data:
                        break
                    buffer += data
                    # TODO: actually handle the data received
                    # Should do so by calling handle_message() after parsing the buffer using a delimiter set by message protocol
            except Exception as e:
                print(f"[receive_from_peer] error: {e}")
            finally:
                # we need this "if" check since the broadcast thread may have deleted that already
                if peer_id in self.peers:
                    del self.peers[peer_id]
    
    def handle_message(self, msg):
        """
        Handle the message received from peers.
        Calls handle_block() or handle_transaction() depending on the type of message, as set by the message protocol.
        """
        pass

    def handle_block(self, block):
        """
        Handle a block received from another peer after it successfully mines it.
        Need to call chain.update_balance()
        Need to handle forks
        """
        pass

    def handle_transaction(self, transaction):
        """
        Handle a transaction received from another peer.
        Need to call chain.recv_transaction()
        """
        pass
    
    def broadcast(self, msg):
        msg_str = json.dumps(msg) + "\n" # TODO: placeholder, need to evaluate message protocol between nodes

        for peer_id, conn in self.peers.items():
            try:
                conn.sendall(msg_str.encode())
            except Exception as e:
                print(f"[broadcast] error: {e}")
                conn.close()
                # we need this "if" check since the listener thread may have deleted that already
                if peer_id in self.peers:
                    del self.peers[peer_id]

    # I moved this logic from the blockchain layer:
    # For the genesis block, we don't need to do anything special to mine it, just easier if we don't trickle it down to the blockchain level
    # Sunny's original implementation also isn't compatible with how each peer node, upon creation, already gets a wallet
    """
    def create_first_block(self):
        first_wallet = Wallet("Satoshi Nakamoto")
        initial_tx = Transaction(100, self.coinbase, first_wallet)
        return Block("0" * 64, [initial_tx]), first_wallet
    
    """
    def genesis_block(self):
        """
        Logic to create the genesis block, if needed.
        """
        pass


    def mine_block(self):
        """
        Mine a block using the transactions in the mempool.
        Need to call chain.mine_block(), chain.add_block(), and need to broadcast the block to peers.
        Need to handle the case where a block is received from another peer, since it mined it first. 
        """
        pass

    def start(self):
        self.connect_to_tracker()
        self.form_peer_connections()
        threading.Thread(target=self.listener_thread, daemon=True).start()

        # Genesis case
        self.genesis_block()

        # Collects transaction from mempool to mine a block every 5 seconds
        while True:
            self.mine_block()
            time.sleep(5)


        