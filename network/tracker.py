import argparse
import socket
import threading
import json

class Tracker:
    """
    Tracker class that manages a list of active peers.
    """
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.peer_ids = []
        self.public_keys = []
        self.lock = threading.Lock()

    def start(self):
        """
        Starts the Tracker server.
        
        Listens for incoming peer connections and spawns a thread to handle each peer.
        """
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()
        print(f"[Tracker] Listening on {self.host}:{self.port}...")

        while True:
            client_sock, addr = server_sock.accept()
            t = threading.Thread(target=self.handle_peer, args=(client_sock, addr))
            t.start()
    
    def handle_peer(self, client_sock, addr):
        """
        Handles an individual peer connection.
        
        Expects a 3-byte 'SYN' handshake, sends back the peer list,
        and monitors for connection closure.
        """
        peer_id = None
        try:
            syn = client_sock.recv(3)
            if syn != b"SYN":
                print(f"[Tracker] Invalid handshake from {addr}, closing connection.")
                client_sock.close()
                return
        
            port_data = client_sock.recv(64).decode().strip()
            public_key = client_sock.recv(512).decode().strip()
            peer_listen_port = int(port_data)
            ip = addr[0]
            peer_id = f"{ip}:{peer_listen_port}"

            with self.lock:
                self.peer_ids.append(peer_id)
                self.public_keys.append(public_key)
            print(f"[Tracker] Peer connected: {peer_id}")

            with self.lock:
                combined_list = [f"{pid}|{pk}" for pid, pk in zip(self.peer_ids, self.public_keys)]
            
            client_sock.sendall(json.dumps(combined_list).encode())

            while True:
                data = client_sock.recv(1024)
                if not data:
                    break

        except Exception as e:
            print(f"[Tracker] Error handling peer: {e}")

        finally:
            self.unregister_peer(peer_id)
            try:
                client_sock.close()
            except:
                pass
    
    def unregister_peer(self, peer_id):
        """
        Removes a peer from the peer list when it disconnects.
        """
        with self.lock:
            if peer_id in self.peer_ids:
                index = self.peer_ids.index(peer_id)
                del self.peer_ids[index]
                del self.public_keys[index]
                print(f"[Tracker] Peer disconnected: {peer_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tracker for managing peers.")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host IP to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    args = parser.parse_args()

    tracker = Tracker(host=args.host, port=args.port)
    tracker.start()