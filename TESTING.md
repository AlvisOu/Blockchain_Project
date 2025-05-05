TESTING INSTRUCTIONS:

1. Open the server with `python network/tracker.py`
   - Can be kept on across multiple testing sessions
2. Run a script in testing/ folder with `python -m testing.<script_name>`
   - Do NOT add the `.py` extension
   - Ex. `python -m testing.script` to run script.py

Testcase 1 - Basic 3 peers:
Script: script_three_ppl.py

Description: Testcase creates 3 peers at the start and handles
a few transactions:

- Sunny joins network
- Alvis joins network
- Sky joins network
- Sunny -> Alvis 2 coins
- Sunny -> Alvis 3 coins
- Alvis -> Sky 4 coins
- Sky -> Sunny 5 coins

Our results indicate all chains are synchronized, and
there is no double counting with transactions.

Testcase 2 - Joining midway:
Script: script_mid_join.py

Description: Testcase creates 2 peers at the start. The 2 peers
have some transactions. Then, another peer is added, and a few
more transactions involving the new peer is conducted.

- Sunny joins network
- Alvis joins network
- Sunny -> Alvis 5 coins
- Sunny -> Alvis 9 coins
- John joins network
- Sunny -> John 4 coins
- John -> Sunny 3 coins
