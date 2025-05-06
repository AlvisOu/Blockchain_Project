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
```
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
```
TESTING INSTRUCTIONS:

Note: For all instructions, run it in the root directory

FOR TERMINAL ONLY
1. Open the server with `python -m network.tracker`
   - Can be kept on across multiple testing sessions
2. In a different terminal, run a script in the testing/
   folder with `python -m testing.<script_name>`
   - Do NOT add the `.py` extension
   - Ex. `python -m testing.script` to run script.py

WITH WEBSITE INTERFACE
1. Open the server with `python -m network.tracker`
   - Can be kept on across multiple testing sessions
2. For every single peer you want to create, open a 
   separate terminal and run `python -m app.app <port_number>`
   - Make sure every user has a different port number (5000, 5001, etc.)
3. Take the IP address of your peers and open it in different browsers
   - The address will be shown in the terminal when you run the 2nd command
   - i.e. run 127.0.0.1:5000 in a chrome browser.
4. In the "Set Your Username" box, type the name of the
   peer and click set. This will create the peer and wallet
   associated with the peer.
5. Click on "List Users" to retrieve the list of users you can
   send money to.
   - If you don't click on this button, send collectables will
     not recognize the existing users even if the blockchain does.
     The list of users will simply be empty according to the website
6. Click on check balance to retrieve the balance of your user.
