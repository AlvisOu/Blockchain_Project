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

    sunny = run_peer(5001, "Sunny", tracker_host, tracker_port)
    time.sleep(3)
    alvis = run_peer(5002, "Alvis", tracker_host, tracker_port)
    time.sleep(3)
    john = run_peer(5003, "John", tracker_host, tracker_port)
    time.sleep(3)
    sky = run_peer(5004, "Sky", tracker_host, tracker_port)
    time.sleep(3)
    haruki = run_peer(5005, "Haruki", tracker_host, tracker_port)
    time.sleep(3)
    william = run_peer(5006, "William", tracker_host, tracker_port)
    time.sleep(15)
    
    print("=== Starting Transactions ===")

    time.sleep(10)

    sunny.transfer(receiver_public_key=alvis.wallet.public_key, amount=5.0)
    time.sleep(5)
    # print_every_balance(peers)

    john.transfer(receiver_public_key=sky.wallet.public_key, amount=9.0)
    time.sleep(5)

    haruki.transfer(receiver_public_key=william.wallet.public_key, amount=2.0) # Alvis -> Sky
    time.sleep(5)

    william.transfer(receiver_public_key=alvis.wallet.public_key, amount=3.0)
    
    time.sleep(40)

    peers = [("Sunny", sunny), ("Alvis", alvis), ("John", john), ("Sky", sky), ("Haruki", haruki), ("William", william)]
    print_every_balance(peers)
    for p in peers:
        print(f"{p[0]}'s chain: ")
        p[1].chain.print_chain()
