from flask import Flask, request, jsonify, send_from_directory
import threading
from network import Peer
import sys

app = Flask(__name__, static_folder="static")

peer = None  # Global peer object
tracker_host = "localhost"
tracker_port = 8000

@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/init/<username>")
def api_init(username):
    global peer
    if peer is not None:
        return jsonify({"error": "Peer already initialized"}), 400

    try:
        peer_port = int(sys.argv[1])*5 if len(sys.argv) > 1 else 5000
        peer = Peer(peer_port, username, tracker_host, tracker_port)
        threading.Thread(target=peer.start, daemon=True).start()
        return jsonify({"message": f"Peer started for {username}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/list")
def api_list():
    if not peer:
        return jsonify({"error": "Peer not initialized"}), 400

    try:
        users = peer.list_users()
        return jsonify([
            {"name": name, "public_key": pubkey}
            for pubkey, name in users
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/balance")
def api_balance():
    if not peer:
        return jsonify({"error": "Peer not initialized"}), 400
    
    balance = peer.get_balance()
    if balance is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"balance": balance}), 200

@app.route("/api/send", methods=["POST"])
def api_send():
    if not peer:
        return jsonify({"success": False, "message": "Peer not initialized"}), 400

    data = request.get_json(force=True)
    sender = data.get("sender")
    recipient = data.get("recipient")
    amount = data.get("amount")

    try:
        success = peer.transfer(receiver_public_key=recipient, amount=int(amount))
        if success:
            return jsonify({
                "success": success,
                "message": f"Sent {amount} from {sender} to {recipient}"
            }), 200
        else:
            return jsonify({
                "success": success,
                "message": f"Tried to send {amount} from {sender} to {recipient}"
            }), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port)