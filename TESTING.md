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

Our results indicate all chains are synchronized,
there is no double counting with transactions, and
the balances of all the peers add up. Forks do often
occur in this testing script and they get resolved.

---

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

Our results indicate all chains are synchronized,
there is no double counting with transactions, and
the balances of all the peers add up. Importantly,
John, the late-comer, has the longest PoW chain by
the end of the session. Fork inevitably occurs in this
test (since John needs to catch up), so it shows
fork resolution.

---

Testcase 3 - Many peers:
Script: script_many.py

Description: Testcase creates 6 peers at the start, and all
of them exchange in a transaction at least once.

- Sunny, Alvis, John, Sky, Haruki, and William joins network
- Sunny -> Alvis 5 coins
- John -> Sky 9 coins
- Haruki -> William 2 coins
- William -> Alvis 3 coins

Our results indicate all chains are synchronized,
there is no double counting with transactions, and
the balances of all the peers add up. Fork occurs often
in this test (due to number of peers), so this shows
fork resolution.4

---

Testcase 4 - Fraudulent Block:
Script: script_fraud.py

Description: Testcase creates 3 peers at the start. A
fraudulent block with a fradulent transaction is created.
The transaction sends money from sky to sunny, but the
block's hash does not start with the four 0s, so it does
not pass proof of work.
Additionally, Sunny attempts sending Alvis negative money,
which is also invalid.

- Sunny, Alvis, Sky joins the network
- Sunny -> Alvis -90 coins
- Sunny broadcasts fradulent block.

Our results indicate all chains are synchronized,
the negative money transaction was spotted and marked
invalid, and the block was also marked invalid for lacking
proof of work.
