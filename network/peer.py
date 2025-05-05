import socket, json, time, threading
from blockchain import Chain, Wallet, Transaction, Block
import pickle
import base64

class Peer:
    """
        Peer class that functions as each node in the network.
    """
    def __init__(self, port: int, name: str, tracker_addr: int, tracker_port: int):
        self.tracker_addr = tracker_addr
        self.tracker_port = tracker_port
        self.port = port
        self.peers = {} # {"addre:port" as one peer_id string : socket}
        self.wallet = Wallet(name=name)
        self.chain = Chain()
        self.socket_to_tracker = None
        self.longest_chain = None
        self.request_mode = False
        self.requests = 0
        self.longest_chain_length = 0
        self.peer_name_map = {}
        self.lock = threading.Lock()

    def connect_to_tracker(self):
        """
        Connects to the tracker.
        """
        try:
            self.socket_to_tracker = socket.create_connection((self.tracker_addr, self.tracker_port)) # create_connection is more robust than socket.connect then socket.bind
            print(f"[connect_to_tracker] {self.port} connected to tracker at {self.tracker_addr}:{self.tracker_port}")
        except Exception as e:
            print(f"[connect_to_tracker] {self.port} error: {e}")

    def get_peer_list(self):
        """
            Get the list of peers from the tracker upon joining the network system.
        """
        try:
            self.socket_to_tracker.sendall(b"SYN")
            self.socket_to_tracker.sendall(f"{self.port}|{self.wallet.public_key}|{self.wallet.name}\n".encode())
            data = self.socket_to_tracker.recv(4096).decode()
            peer_list = json.loads(data)
            return peer_list
        except Exception as e:
            print(f"[get_peer_list] error: {e}")
            return []
        
    def form_peer_connections(self):
        """
        Forms connections to each peer in the network, according to the peer list.
        Each connection creates a thread to listen for messages from that peer.

        A massive sweep of connections like this is only done when the peer joins the network.
        After that, it will listen for connections to accept from newly joined peers and add to the peer list.
        Or it will realize a peer has disconnected when failing to receive or send data to it, before removing it from the peer list.
        """
        peers = self.get_peer_list()
        for peer in peers:
            if peer == f"127.0.0.1:{self.port}":
                continue # Don't connect to self
            
            if peer not in self.peers:
                try:
                    ip, port = peer.split(":")
                    sock = socket.create_connection((ip, int(port)))
                    peer_id = f"{ip}:{port}"
                    with self.lock:
                        self.peers[peer_id] = sock
                    print(f"[form_peer_connections] {self.port} connected to {peer}")
                    threading.Thread(target=self.receive_from_peer, args=(sock, peer_id), daemon=True).start()
                except Exception as e:
                    print(f"[refresh_peer_connections] {self.port} connection error when connecting to {peer}: {e}")
            
        self.last_refresh = time.time()

    def listener_thread(self):
        """
        Called by the genesis background thread to listen for incoming connections from newly joined peers.
        Upon discovering a new peer, it will create a thread to listen for messages from that peer.
        """
        listenr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenr.bind(("localhost", self.port))
        listenr.listen()
        print(f"[listener_thread] {self.port} is listening")

        while True:
            conn, addr = listenr.accept()
            print(f"[listener_thread] {self.port} accepted connection from {addr}")
            peer_id = f"{addr[0]}:{addr[1]}"
            with self.lock:
                self.peers[peer_id] = conn
            threading.Thread(target=self.receive_from_peer, args=(conn, peer_id), daemon=True).start()

    def tracker_thread(self):
        while True:
            data = self.socket_to_tracker.recv(4096).decode()
            public_keys_str, names_str = data.strip().split("|", 1)
            updated_public_keys = json.loads(public_keys_str)
            updated_names = json.loads(names_str)
            with self.lock:
                self.peer_name_map = dict(zip(updated_public_keys, updated_names))
                updated_public_keys = set(updated_public_keys)
                current_public_keys = list(self.chain.balances.keys())

                for public_key in updated_public_keys:
                    if public_key not in self.chain.balances:
                        self.chain.balances[public_key] = 0

                for public_key in current_public_keys:
                    if public_key not in updated_public_keys:
                    # if public_key not in updated_public_keys and public_key != "0x1" and public_key != "0x0":
                        del self.chain.balances[public_key]
                print(f"[tracker_thread] {self.port} successfully received updated public keys")

    def receive_from_peer(self, conn, peer_id):
        """
        Receive messages from a peer connection.
        Calls handle_message() to handle the message received.
        """
        with conn:
            try:
                buffer = ""
                while True:
                    data = conn.recv(4096).decode()
                    if not data:
                        break
                    buffer += data

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        try:
                            msg = json.loads(line)
                            if self.request_mode:
                                if msg["type"] == "chain" or msg["type"] == "request":
                                    self.handle_message(msg)
                            else:
                                self.handle_message(msg)
                        except json.JSONDecodeError as e:
                            print(f"[receive_from_peer] JSON decode error: {e}")
            except Exception as e:
                print(f"[receive_from_peer] error: {e}")
            finally:
                # we need this "if" check since the broadcast thread may have deleted that already
                with self.lock:
                    if peer_id in self.peers:
                        del self.peers[peer_id]
    
    def handle_message(self, msg):
        """
        Handle the message received from peers.
        Calls handle_block() or handle_transaction() depending on the type of message, as set by the message protocol.
        """
        print(self.wallet.name + " received a message of type " + msg["type"])
        if msg["type"] == "transaction":
            tx_bytes = base64.b64decode(msg["data"])
            tx = pickle.loads(tx_bytes)
            sign = msg["signature"]
            self.handle_transaction(tx, sign)
        elif msg["type"] == "block":
            block_bytes = base64.b64decode(msg["data"])
            block = pickle.loads(block_bytes)
            self.handle_block(block)
        elif msg["type"] == "chain":
            chain_bytes = base64.b64decode(msg["data"])
            chain = pickle.loads(chain_bytes)
            self.handle_chain(chain)
        elif msg["type"] == "request":
            requester = msg["requester"]
            print(type(chain))
            self.send_chain(requester)

    def handle_chain(self, chain):
        """
        Handle a chain received from another peer
        """
        print(f"[handle_chain] {self.wallet.name} received a chain")
        with self.lock:
            if len(chain.chain) > self.longest_chain_length:
                self.longest_chain = chain
                self.longest_chain_length = len(chain.chain)
            self.requests += 1
            if self.requests == len(self.peers):
                self.request_mode = False
                self.requests = 0
                self.longest_chain_length = 0

    def handle_block(self, block):
        """
        Handle a block received from another peer after it successfully mines it.
        Need to call chain.update_balance()
        Need to handle forks
        """
        with self.lock:
            if block.prev_hash == self.chain.chain[-1].hash:
                self.chain.add_block(block)
                print(f"[handle_block] {self.wallet.name} block {block.hash[:8]} added to chain")
            else:
                print(f"[handle_block] Fork detected!")
                self.request_chains()
                self.chain.chain = self.longest_chain

    def handle_transaction(self, transaction, sign):
        """
        Handle a transaction received from another peer.
        Need to call chain.recv_transaction()
        """
        print(f"[handle_transaction] {self.wallet.name} received a transaction")
        with self.lock:
            self.chain.recv_transaction(transaction, sign, True)
    
    def broadcast(self, msg):
        """
        Broadcast a message to all peers in the network.
        This message may be a new transaction or a new block mined.
        """
        msg_str = json.dumps(msg) + "\n"
        with self.lock:
            for peer_id, conn in self.peers.items():
                try:
                    conn.sendall(msg_str.encode())
                except Exception as e:
                    print(f"[broadcast] error: {e}")
                    conn.close()
                    # we need this "if" check since the listener thread may have deleted that already
                    if peer_id in self.peers:
                        del self.peers[peer_id]
    
    def request_chains(self):
        print("[request_chains] fork detected, requesting chains from peers")
        with self.lock:
            self.request_mode = True
            self.requests_needed = len(self.peers)
            msg = {
                "type": "request",
                "requester": f"localhost:{self.port}"
            }
            self.broadcast(msg)
        
    def send_chain(self, requester):
        """
        Sends this peer's current blockchain to a requesting peer.
        """
        print(f"[send_chain] {self.wallet.name} Sending chain to {requester}")
        pickled_chain = pickle.dumps(self.chain)
        # Encode the bytes into a JSON-safe string
        encoded_chain = base64.b64encode(pickled_chain).decode('utf-8')
        msg = {
            "type": "chain",
            "data": encoded_chain
        }
        msg_str = json.dumps(msg) + "\n"

        with self.lock:
            conn = self.peers[requester]
        
        if requester in self.peers:
            conn.sendall(msg_str)
        else:
            print(f"[send_chain] Peer {requester} not found in peers list.")

    def transfer(self, receiver_public_key: str, amount: float):
        """
        Creating a transaction to send money to another peer.
        Calls broadcast() to announce the transaction to all peers.
        """
        transaction = Transaction(amount, self.wallet, receiver_public_key)
        sign = self.wallet.sign(transaction)
        pickled_transaction = pickle.dumps(transaction)
        # Encode the bytes into a JSON-safe string
        encoded_transaction = base64.b64encode(pickled_transaction).decode('utf-8')
        message = {
            "type": "transaction",
            "signature": sign,
            "data": encoded_transaction
        }
        success, status = self.wallet.send_money(amount, receiver_public_key, self.chain)
        if success:
            self.broadcast(message)
            receiver_name = self.peer_name_map.get(receiver_public_key, receiver_public_key)
            print(f"[transfer] {self.wallet.name} sent {amount} to {receiver_name}")
            return True
        else:
            print(f"[transfer] error: {status}")
            return False

    def mine_block(self):
        """
        Mine a block using the transactions in the mempool.
        Need to call chain.mine_block() and broadcast the block to peers.
        Need to handle the case where a block is received from another peer, since it mined it first. 
        """
        with self.lock:
            block = self.chain.mine_block(self.wallet)
            if block == False:
                print("[mine_block] New block already added by peer. Aborting own block.")
                return
            if block:
                self.chain.add_block(block)
        
        if block:
            pickled_block = pickle.dumps(block)
            # Encode the bytes into a JSON-safe string
            encoded_block = base64.b64encode(pickled_block).decode('utf-8')
            message = {
                "type": "block",
                "data": encoded_block
            }
            print("Broadcasting block: " + block.hash[:8])
            self.broadcast(message)

    def start(self):
        self.connect_to_tracker()
        self.form_peer_connections()
        threading.Thread(target=self.listener_thread, daemon=True).start()
        threading.Thread(target=self.tracker_thread, daemon=True).start()
        
        # Collects transaction from mempool to mine a block every 5 seconds
        while True:
            time.sleep(10)
            self.mine_block()