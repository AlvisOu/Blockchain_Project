import socket, json, time, threading
from blockchain import Chain, Wallet, Transaction, Block

# TODO: blockchain specific functions (stubbed out with pass), node-to-node message protocol (commented with TODO), thread locks where needed

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

    def connect_to_tracker(self):
        """
        Connects to the tracker.
        """
        try:
            self.socket_to_tracker = socket.create_connection((self.tracker_addr, self.tracker_port)) # create_connection is more robust than socket.connect then socket.bind
            print(f"[connect_to_tracker] tracker connected at {self.tracker_addr}:{self.tracker_port}")
        except Exception as e:
            print(f"[connect_to_tracker] error: {e}")

    def get_peer_list(self):
        """
            Get the list of peers from the tracker upon joining the network system.
        """
        try:
            # For Sky: can data of peer list information be formatted like:
            # data = '[ "192.168.1.5:5000", "192.168.1.6:5000" ]'
            self.socket_to_tracker.sendall(b"SYN") # For Sky: this is the handshake protocol from my side
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
            if peer == f"localhost:{self.port}":
                continue # Don't connect to self
            
            if peer not in self.peers:
                try:
                    ip, port = peer.split(":")
                    sock = socket.create_connection((ip, int(port)))
                    peer_id = f"{ip}:{port}"
                    self.peers[peer_id] = sock
                    print(f"[form_peer_connections] connected to {peer}")
                    threading.Thread(target=self.receive_from_peer, args=(sock, peer_id), daemon=True).start()
                except Exception as e:
                    print(f"[refresh_peer_connections] connection error: {e}")
            
        self.last_refresh = time.time()

    def listener_thread(self):
        """
        Called by the genesis background thread to listen for incoming connections from newly joined peers.
        Upon discovering a new peer, it will create a thread to listen for messages from that peer.
        """
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
                    # TODO: actually handle the data received
                    # Should do so by calling handle_message() after parsing the buffer using a delimiter set by message protocol
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        try:
                            msg = json.loads(line)
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
        if msg["type"] == "transaction":
            tx_data = msg["data"]
            tx = Transaction(
                amount=tx_data["amount"],
                payer=self.wallet,
                payee_public_key=tx_data["payee"]
            )
            self.handle_transaction(tx)
        elif msg["type"] == "block":
            block_data = msg["data"]
            transactions = []
            for tx in block_data["transaction"]:
                transactions.append(Transaction(
                    amount=tx["amount"],
                    payer=self.wallet,
                    payee_public_key=tx["payee"]
                ))
            block = Block(
                prev_hash=block_data["prev_hash"],
                transactions=transactions,
                nonce=block_data["nonce"]
            )
            self.handle_block(block)

    def handle_block(self, block):
        """
        Handle a block received from another peer after it successfully mines it.
        Need to call chain.update_balance()
        Need to handle forks
        """
        with self.lock:
            if block.prev_hash == self.chain.chain[-1].hash:
                self.chain.add_block(block)
                print(f"[handle_block] Block {block.hash} added to chain")
            else:
                for i in reversed(range(len(self.chain.chain))):
                    if self.chain.chain[i].hash == block.prev_hash:
                        candidate_chain = self.chain.chain[:i+1] + [block]
                        if len(candidate_chain) > len(self.chain.chain):
                            print("[handle_block] Longer fork found — replacing current chain.")
                            self.chain.chain = candidate_chain
                        else:
                            print("[handle_block] Received block is part of a shorter fork. Ignored.")
                        return

                print("[handle_block] Received block does not connect to known chain. Ignored.")

    def handle_transaction(self, transaction):
        """
        Handle a transaction received from another peer.
        Need to call chain.recv_transaction()
        """
        with self.lock:
            sign = self.wallet.sign(transaction)
            self.chain.recv_transaction(transaction, sign)
    
    def broadcast(self, msg):
        """
        Broadcast a message to all peers in the network.
        This message may be a new transaction or a new block mined.
        """
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

    def transfer(self, receiver_public_key: str, amount: float):
        """
        Creating a transaction to send money to another peer.
        Calls broadcast() to announce the transaction to all peers.
        """
        transaction = Transaction(amount, self.wallet, receiver_public_key)

        # TODO: tentative, need to define message protocol between nodes
        message = {
            "type": "transaction",
            "data": transaction.to_dict()
        }
        self.broadcast(message)
        self.wallet.send_money(amount, receiver_public_key, self.chain)
        print(f"[transfer] {self.wallet.name} sent {amount} to {receiver_public_key}")

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
        # block = self.chain.mine_block(self.wallet)
        with self.lock:
            latest_hash_before = self.chain.chain[-1].hash
            block = self.chain.mine_block(self.wallet)
            if self.chain.chain[-1].hash != latest_hash_before:
                print("[mine_block] New block already added by peer. Aborting own block.")
                return
        
        if block:
            message = {
                "type": "block",
                "data": {
                    "prev_hash": block.prev_hash,
                    "transaction": [tx.to_dict() for tx in block.transactions],
                    "nonce": block.nonce,
                    "timestamp": block.timestamp
                }
            }
            self.broadcast(message)
        # TODO: Need to handle the case where a block is received from another peer, since it mined it first.

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


        