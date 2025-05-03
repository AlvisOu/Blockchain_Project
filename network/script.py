import threading
import time
from peer import Peer

def run_peer(port, name, tracker_host, tracker_port):
    peer = Peer(port=port, name=name, tracker_addr=tracker_host, tracker_port=tracker_port)
    peer_thread = threading.Thread(target=peer.start, daemon=True)
    peer_thread.start()
    return peer

if __name__ == "__main__":
    tracker_host = "localhost"
    tracker_port = 8000

    peer1 = run_peer(5001, "Sunny", tracker_host, tracker_port)
    peer2 = run_peer(5002, "Alvis", tracker_host, tracker_port)
    peer3 = run_peer(5003, "Sky", tracker_host, tracker_port)

    time.sleep(5)

    print("=== Starting Transactions ===")
    peer1.transfer(receiver_public_key=peer2.wallet.public_key, amount=5.0)
    time.sleep(1)
    peer2.transfer(receiver_public_key=peer3.wallet.public_key, amount=2.0)
    time.sleep(1)
    peer3.transfer(receiver_public_key=peer1.wallet.public_key, amount=1.0)

    time.sleep(15)