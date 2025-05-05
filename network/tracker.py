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
        self.peers = {}
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
        
            info = client_sock.recv(1024).decode().strip()
            try:
                port_data, public_key, name = info.split("|", 2)
            except ValueError:
                print(f"[Tracker] Invalid peer info format from {addr}: {info}")
                client_sock.close()
                return
            peer_listen_port = int(port_data)
            ip = addr[0]
            peer_id = f"{ip}:{peer_listen_port}"

            with self.lock:
                self.peers[peer_id] = {
                    'public_key': public_key,
                    'name': name,
                    'connection': client_sock
                }
            print(f"[Tracker] Peer connected: {peer_id}")
            
            peer_ids = list(self.peers.keys())
            client_sock.sendall(json.dumps(peer_ids).encode())

            self.broadcast_public_keys_and_names()

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
        Removes a peer from all tracking lists when the peer disconnects.
        """
        with self.lock:
            if peer_id and peer_id in self.peers:
                del self.peers[peer_id]
                print(f"[Tracker] Peer disconnected: {peer_id}")
            elif peer_id:
                print(f"[Tracker] Tried to unregister unknown peer: {peer_id}")
        self.broadcast_public_keys_and_names()

    def broadcast_public_keys_and_names(self):
        """
        Broadcasts the current list of public keys and names to all connected peers.
        """
        with self.lock:
            public_keys = [peer_data['public_key'] for peer_data in self.peers.values()]
            names = [peer_data['name'] for peer_data in self.peers.values()]
            public_keys_str = json.dumps(public_keys)
            names_str = json.dumps(names)
            combined = f"{public_keys_str}|{names_str}\n".encode()
            for peer_id, peer_data in list(self.peers.items()):
                try:
                    peer_data['connection'].sendall(combined)
                except Exception:
                    print(f"[Tracker] Failed to send to peer {peer_id}, removing connection")
                    del self.peers[peer_id]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tracker for managing peers.")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host IP to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    args = parser.parse_args()

    tracker = Tracker(host=args.host, port=args.port)
    tracker.start()