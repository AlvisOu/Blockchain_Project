# simple_market/app.py
from flask import Flask, request, jsonify, send_from_directory

#from blockchain import list_users, get_balance, send_coins

app = Flask(__name__, static_folder="static")


@app.route("/")                       # serve the front‑end
def root():
    return send_from_directory(app.static_folder, "index.html")

# ---- API endpoints ----
@app.route("/api/list")
def api_list():
    return jsonify(["Sunny", "Alvis", "John", "Sky"])  
    #return jsonify(list_users())      # → ["alice", "bob", ...]


@app.route("/api/balance/<username>")
def api_balance(username):
    # bal = get_balance(username)
    # if bal is None:
    #     return jsonify({"error": "user not found"}), 404
    return jsonify({"user": username, "balance": 100})


@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.get_json(force=True)
    # success, msg = send_coins(
    #     data.get("sender"), data.get("recipient"), data.get("amount")
    # )
    # status = 200 if success else 400
    # return jsonify({"success": success, "message": msg}), status
    return jsonify({
        "success": True,
        "message": f"Mock send {data.get('amount')} from {data.get('sender')} to {data.get('recipient')}"
    })


if __name__ == "__main__":
    app.run(debug=True)               # http://localhost:5000
