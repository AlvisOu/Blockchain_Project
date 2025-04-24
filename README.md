# Blockchain_Project

Team Members

Member 1: 
    Name: Sunny Carlin Qi
    UNI:  sq2284

Member 2: 
    Name: Alvis Ou
    UNI:  ao2844
    
Member 3: 
    Name: Sky Mingyang Sun
    UNI:  ms6124

Member 4: 
    Name: John Zhang Dong
    UNI:  jzd2103

Current issues:
- private key is lowkey not private rn

# Everything below is included to provide a context of what we may need to do 
# Suggested repo structure for reference (we will simplify and adjust this)
```
micro-crypto-economy/
│
├── blockchain/                 # Core blockchain logic (you already have this)
│   ├── __init__.py
│   ├── wallet.py               # Wallet + signature logic
│   ├── transaction.py          # Transaction object
│   ├── block.py                # Block object
│   └── chain.py                # Chain logic, mempool, mining, balances
│
├── network/                    # P2P network and tracker communication
│   ├── __init__.py
│   ├── peer.py                 # Each peer runs this (node logic)
│   ├── tracker.py              # Tracker server
│   └── connection.py           # Socket/gRPC wrappers (connect, broadcast)
│
├── scripts/                    # Simulation scripts for testing behavior
│   ├── run_script.py           # Runs a peer using instructions in a script.txt
│   └── example_script.txt      # Sample: Alice sends Bob 5, mine, print balance
│
├── tests/
│   ├── test_chain.py           # Test mining, fork resolution, double spend
│   ├── test_transaction.py     # Signature verification, invalid tx rejection
│   └── ...
│
├── utils/
│   ├── crypto.py               # Hashing, signing, base64 utils
│   └── config.py               # Constants: difficulty, port #s, etc.
│
├── run_peer.py                 # Entrypoint to launch a peer node
├── run_tracker.py              # Entrypoint to launch the tracker
├── requirements.txt
└── README.md
```
Potential script.txt for reference: 
CREATE_WALLET Alice
CREATE_WALLET Bob
SEND Alice 10 Bob
SEND Alice 15 Bob
MINE Alice
BALANCE Alice
BALANCE Bob
CHAIN

# Tentative high-level for reference 
(copy-pasted from GPT, for reference, skip the details, need to revist after going through Sunny's current implementation and discussing with the group what additional functionality we need)
## 1. Peer-to-Peer Network with Tracker (on Google VMs)
### Tracker server (central coordinator):
- Maintains the list of active peers.
- Broadcasts peer join/leave events.
### Each peer:
- Connects to tracker on startup.
- Maintains live awareness of all other peers.
- Uses sockets or gRPC for communication.

## 2. Blockchain Core Functionality
Each peer maintains a local blockchain and supports the following:
### a. Blockchain Copy
Full local copy with blocks and transactions.
Each block includes: block hash, previous hash, timestamp, nonce, transaction list, and Merkle root (optional).

### b. Block Mining
Simplified proof-of-work (PoW) using adjustable difficulty.
Mining reward in coins (to simulate mining incentives).
Peers mine valid blocks including market/transfer transactions.

### c. Broadcast and Verification
Newly mined blocks are broadcast to all peers.
Peers verify block hashes, transactions, and PoW validity.
Valid blocks get added to the chain; invalid blocks are ignored.

### d. Fork Resolution
Longest valid chain rule.
Forks occur if two blocks are mined nearly simultaneously.
Peers replace shorter chains with longer ones upon receiving them.

## 3. Demo Application: Crypto Market Simulation
Each peer acts as both a user and miner.

### Transactions Supported:
Transfer coins: “Alice sends 10 coins to Bob”
List item for sale: “Alice lists sword for 30 coins”
Bid on auction: “Bob bids 25 coins for Alice’s sword”
Auction resolve: Once bidding ends, the winner is recorded on-chain.
All these are wrapped into signed transaction structures.

### Transaction Flow:
Peers create and sign transactions.
Transactions get broadcast and collected into a mempool.
Miners pick transactions from the mempool and include them in new blocks.

## 4. Blockchain Resilience Demonstration
Showcase two things during your demo:

### a. Tamper Resistance
Manually alter a past block on one peer and show:
Block hashes break
Chain becomes invalid
Peer re-syncs to valid chain from others

### b. Invalid Transactions
Try to double-spend or submit an overdrawn payment.
Peers verify balances before accepting a transaction.
Invalid transactions are rejected and not mined.

## Extra Credit Opportunities
### Graphical Interface (Optional)
Build a simple React or web-based GUI to:
View your wallet balance
Browse the market
Send payments or place bids
Visualize your local blockchain (e.g., chain view)

### Dynamic Mining Difficulty
Every N blocks, adjust difficulty based on average block time.
Slower block generation → easier difficulty; fast mining → harder difficulty.

### Merkle Trees
Use Merkle root to summarize all transactions in a block.
Allow Merkle proof validation for individual transactions without downloading the entire block.


