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
    sky = run_peer(5003, "Sky", tracker_host, tracker_port)
    time.sleep(10)

    print("=== Starting Transactions ===")
    print(sunny.peer_name_map)
    print(alvis.peer_name_map)
    print(alvis.peer_name_map)

    time.sleep(10)

    sunny.transfer(receiver_public_key=alvis.wallet.public_key, amount=2.0)
    time.sleep(5)
    # print_every_balance(peers)

    sunny.transfer(receiver_public_key=alvis.wallet.public_key, amount=3.0)
    time.sleep(5)

    alvis.transfer(receiver_public_key=sky.wallet.public_key, amount=4.0) # Alvis -> Sky
    time.sleep(5)

    sky.transfer(receiver_public_key=sunny.wallet.public_key, amount=5.0)
    
    time.sleep(20)
    peers = [("Sunny", sunny), ("Alvis", alvis), ("Sky", sky)]
    print_every_balance(peers)

    print("Sunny's chain: ")
    sunny.chain.print_chain()

    print("Alvis's chain: ")
    alvis.chain.print_chain()

    print("Sky's chain: ")
    sky.chain.print_chain()