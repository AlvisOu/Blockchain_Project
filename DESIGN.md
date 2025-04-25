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

BLOCKCHAIN APPLICATION:
The goal our blockchain is to create a cryptocurrency that can be exchanged
P2P in a decentralized manner, similar to that of Bitcoin.

BLOCKCHAIN COMPONENTS:
As the name implies, there will be a Block class and Chain class in our
implementation. Besides these two, there will also be the Wallet and
Transaction classes.

Class Wallet:
A Wallet represents a single, uniquely identifiable user who can send money
to other users if they have enough coins. A Wallet is also capable of
mining blocks to get a reward from the coinbase. In essence, a Wallet
is a generic user in a crypto economy that can exchange crypto and mine
blocks.

Class Transaction:
A Transaction represents a single instance of one Wallet giving money
to another Wallet. This could be a user paying another user, or the
coinbase paying a miner. It simply contains the amount of money
exchanged and the payer and payee involved in the transaction. Transaction
contains two similar but distinct functions to help create the blocks.

    to_dict() - creates a dictionary containing all the Transaction information,
    which is then used to produce the hash for a block.

    to_sign() - creates a string that is used to 'sign' the transaction,
    effectively giving the transaction a unique identifier. The signature
    starts as a simple string in the form:

    "{amount}:{payer.public_key}->{payee.public_key}:{timestamp}"

    This is then encrypted using a Wallet's secret key so that only that
    specific Wallet's user can actually produce the correct signature
    in conjunction with the public key to authorize the transaction.
    The specific encryption method used is ECDSA.

    Essentially, in steps:
    1. Make raw signature
    2. Wallet takes raw signature and encrypts with secret key
    3. Wallet gives the blockchain the encrypted signature and public key
    4. Blockchain verifies signature + public key and allows transaction

Class Block:
Our implementation of a block is similar to the one described in the
Bitcoin whitepaper. Specifically, it is made up of the following
components:

    - The previous block's hash: ensures order of blocks cannot be changed.
    - A list of transactions: the main data we want to store
    - A nonce: a specific value that makes the hash start with X number of 0s.
               This is what is used to create a proof of work (PoW), and what
               miners are looking for.
    - A timestamp: The time of block creation.

    The class itself acts mainly as a container of the above information, and
    simply holds a property "hash()" which takes all the contained data
    to generate a unique hash. This hashing uses SHA256, which is a one-way
    encrypting process, meaning it is easy to verify the input with an output
    hash, but practically impossible to reverse engineer an input from an
    output hash.

    For the list of transactions, it will only contain transactions that have
    occured since the previous blocks, and every block will contain excatly one
    'mining' transaction which involves a reward from the coinbase to the
    Wallet that mined the block.

Class Chain:
The actual block-chain itself. This class contains most of the blockchain
functionality, including: - Adding blocks - Mining blocks - Tracking the balances of every Wallet - Tracking the list of transactions not yet commited to the blockchain

    The first step of the chain class is initialization. Obviously, someone has
    to start with some money for this crypto economy to work.

    In the initialization, we follow the steps below:
    - Create the coinbase Wallet (the bank)
    - Create the first 'real' user (Satoshi Nakamoto)
    - Create the first transaction (coinbase gives satoshi 100 coins)
    - Create the first block, containing only this above transaction.
        - This first block's previous hash is set as 64 0s
    - The first block is added to the chain, which is represented as
      a list of blocks.
    - Run update_balances(), which adds Satoshi to the balances dictionary and
      notes down his newfound 100 coin wealth.

    All of the above steps take place in __init__() and create_first_block().

        Note, this is the first big deviation in design choice, since the actual
        'genesis' wealth isn't simply given to some user, but rather earned through
        mining.

        In Satoshi's paper, the first (block 0) transaction was mined, giving
        Satoshi 50 BTC, but this BTC was ceremonial and not actually usable. It was
        the second (block 1) mined that gave a usuable reward to Satoshi.

        In other words, our 'genesis wealth' is seemingly given instead of mined,
        and this is because the condition for block creation in our block chain
        is that there must be transactions present. Thus, if we don't hardcode
        a transaction in, no blocks can exist, and no Wallets will ever have
        money to spend and thus create a transaction (chicken and egg problem).

        We plan to change this system so that we broadcast the first block
        as an empty block (contains no transaction), and the first Wallet to
        mine it will get the genesis wealth. To do this, we may implement a
        timer system so that every, say, 30 seconds, it will check if there are
        still no transactions in the mempool. If that is the case,a block will
        just be created automatically to keep the blockchain progressing.

    Now, lets go over some of the functions:

    create_first_block() - as explained above, essentially hardcodes the first
    transaction and block into the blockchain.

    recv_transaction() - puts a transaction into the mempool. The mempool is
    where future blocks will take transactions from to be created. The mempool
    essentially contains unconfirmed transactions. It also checks for the
    signature and for Wallet balance to see if a transaction is legitimate.

        Note, the wallet balance checking is affected by the mempool's
        existing transactions. If, say, Satoshi has 20 coins, and sends
        20 coins in a transaction still in the mempool, even though that
        expenditure has not actually occured yet (not in the blockchain),
        he cannot attempt another transaction to send more coins since
        according to the mempool, he has 0 coins.

        Additionally, it doesn't check the coinbase's balance when it
        is a payer (effecitvely giving it infinite money), and blocks
        transactions to the coinbase (so that coins cannot dissapear
        once created).

    mine_block() - 'mines' the block by iterating over different values of
    nonce until it produces a hash starting with x number of 0s. Calls
    add_block() once it finds the nonce.

    add_block() - appends the newly mined block to the blockchain and
    updates the balances dictionary according to the commited transactions.
    It also removes the commited transactions from the mempool.

    update_balances() - updates Wallet balances based on a transaction. If
    a new Wallet is involved in a transaction, it is added to the balancesheet
    here. update_balances also ignores coinbase as a payer since coinbase
    as a payer.

    get_balance() - returns Wallet balance according to the blockchain.

    get_effective_balance() - returns Wallet blanace according to the
    blockchain and the mempool. Used in recv_transaction().

    print_balances() - prints out balances of every wallet (not incl. coinbase)

    print_chain() - prints out the entire blockchain, including information
    on the prev_hash, hash, list of transactions, nonce, and time of each
    block.

REMAINING DESIGN IMPLEMENTATION REQUIREMENTS:
Currently, our implementation is only feasible on a single computer.
There is only one blockchain, and every Wallet makes transactions on
this one blockchain.

    We will still need to adjust this implementation so that it will operate
    on multiple nodes, with each node maintaining their own blockchain and
    having the ability to broadcast new blocks. This will also necessitate
    fork handling functionality. That is, given a conflict resulted by
    two blocks being created at nearly the same time, a node must pick the
    blockchain with the most PoW.

    To do this, we will use the following protocol:
    During initialization, every single peer initialize with the exact
    same process. I.e., if there are four nodes, instead of one node doing the
    initialization and broadcasting it to everyone else, every single peer
    will simply just follow an identical initialization process. This should
    cause every node to create an identical block, which will be broadcast to
    every other peer, thus starting the mining of the first block.

    Obviously, this doesn't address the case where a peer joins later or
    disconnects and reconnects later. In this case, the peer will request
    a copy of the blockchain from every other peer. It will then compare each
    peer's blockchain and take the longest one there is.

    For forking, we will address simultaneous blocks on the network level. If,
    say, there are two chains, and a fork occurs creating blocks A and B,
    the chains will individually just accept whatever block comes first,
    since both blocks will have the same height and thus have no priority
    over the other. This creates a scenario where chain 1 may lead with
    block A, while chain 2 leads with block B. At this point, it is a matter
    of which block will be mined next. If A's block is mined next, chain 1
    will simply append it, while chain 2 will detect that this new block is
    not only inconsistent with its own chain but that it also has a longer
    height. In this case, chain 2 will reach out to other peers to find the
    peer with the matching block. When found, it will simply replace its own
    chain with this new longest chain.

    While this replacement occurs, the node will compile a list of
    transactions from the old chain and the new chain. Any transactions in
    the old chain but not the new one will be added to the mempool. This
    ensures the mempool is updated and valid.

    We will also need to test our blockchain protocol for resilience towards
    invalid transactions and modifications.

    If these above feature are attained, then the core of the assignment
    will be completed.

FUTURE DESIGN CONSIDERATIONS:
There are several optional areas of improvement we can make. Given time,
we will likely attempt to create a graphical interface for our crypto
exchange protocol, and the use of a merkle tree to verify and include
multiple transactions (blocks already contain multiple transactions,
but not using a merkle tree). A merkle tree's main advantage is to
verify the existance of a transaction in a block without needing
the entire block, making hashing efficient.

MISC NOTES:
Broadcasting the blocks should occur within the mining of the block.

Also, while mining, the miner should check for other block broadcasts.
If it hears a new block broadcasted, it should stop mining the current
block and mine the new block.

Below is an example of what our repository may be structured like:

```
micro-crypto-economy/
│
├── blockchain/                 # Core blockchain logic
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
