import threading
import time
from network import Peer

def run_peer(port, name, tracker_host, tracker_port):
    peer = Peer(port=port, name=name, tracker_addr=tracker_host, tracker_port=tracker_port)
    peer_thread = threading.Thread(target=peer.start, daemon=True)
    peer_thread.start()
    return peer

def print_every_balance(peers):
    for peer in peers:
        print(peer[0] + ":")
        peer[1].chain.print_balances()

if __name__ == "__main__":
    start_time = time.time()

    tracker_host = "localhost"
    tracker_port = 8000

    peer1 = run_peer(5001, "Sunny", tracker_host, tracker_port)
    print(f"peer1's peers:{peer1.peers}")
    time.sleep(3)
    peer2 = run_peer(5002, "Alvis", tracker_host, tracker_port)
    print(f"peer2's peers:{peer2.peers}")
    time.sleep(3)
    peer3 = run_peer(5003, "Sky", tracker_host, tracker_port)
    print(f"peer3's peers:{peer3.peers}")

    time.sleep(5)
    peers = [("Sunny", peer1), ("Alvis", peer2), ("Sky", peer3)]
    print("Checking peer lists")
    print(peer1.peers)
    print(peer2.peers)
    print(peer3.peers)

    print("=== Starting Transactions ===")
    peer1.transfer(receiver_public_key=peer2.wallet.public_key, amount=5.0) # Sunny -> Alvis
    time.sleep(10)
    print_every_balance(peers)

    peer2.transfer(receiver_public_key=peer3.wallet.public_key, amount=2.0) # Alvis -> Sky
    time.sleep(10)
    print_every_balance(peers)

    peer3.transfer(receiver_public_key=peer1.wallet.public_key, amount=1.0) # Sky -> Sunny
    time.sleep(10)
    print_every_balance(peers)
