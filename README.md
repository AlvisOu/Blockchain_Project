# Blockchain_Project

Team Members
Member 1:
Name: Sunny Carlin Qi
UNI: sq2284

Member 2:
Name: Alvis Ou
UNI: ao2844

Member 3:
Name: Sky Mingyang Sun
UNI: ms6124

Member 4:
Name: John Zhang Dong
UNI: jzd2103

mcdonalds_collectable_blockchain/
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
│   └── tracker.py              # Tracker server
│
├── app/                        # Website interface for sending collectables
│   ├── app.py                  # Flask server for peer
│   └── static/
│       └── index.html          # HTML of web interface
│
├── testing/                    # Simulation scripts for testing behavior
│   ├── script_three_ppl.py     # Basic test with 3 peers
│   ├── script_mid_join.py      # Test with user joining mid-session
│   ├── script_fraud.py         # Test invalid transaction and block sends
│   └── script_many.py          # Stress test with 6 peers
│
├── requirements.txt            # Contains package and import requirements
├── README.md                   # Contains file structure and team info
├── DESIGN.md                   # Design details of project
└── TESTING.md                  # Testing script details and results

TESTING INSTRUCTIONS:
FOR TERMINAL ONLY
1. Open the server with `python network/tracker.py`
   - Can be kept on across multiple testing sessions
2. In a different terminal, run a script in the testing/
   folder with `python -m testing.<script_name>`
   - Do NOT add the `.py` extension
   - Ex. `python -m testing.script` to run script.py

WITH WEBSITE INTERFACE
