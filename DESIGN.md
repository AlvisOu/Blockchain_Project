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
The goal of our blockchain is to create a cryptocurrency that can be exchanged
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
blocks. It has a sign() function that gets called in the send_money()
function to provide a signature for a transaction.

Class Transaction:
A Transaction represents a single instance of one Wallet giving money
to another Wallet. This could be a user paying another user, or the
coinbase paying a miner. It simply contains the amount of money
exchanged and the payer (as a Wallet object) and the payee's public key
(since a payer doesn't have acccess to the payee's Wallet) involved in the
transaction. Transaction contains two similar but distinct functions to help
create the blocks.

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
functionality, including: - Adding blocks - Mining blocks - Tracking the
balances of every Wallet - Tracking the list of transactions not yet commited
to the blockchain

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

    Now, lets go over some of the functions:

    create_first_block() - essentially hardcodes the first
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

Class Peer:

    tracker_thread() - this thread is used to receive updates for the latest 
    public keys and their corresponding names, which are sent by the tracker. If 
    it discovers that new peers have joined, it updates balances accordingly, and 
    if peers have left, it deletes their entry in balances.

    handle_message() - used to handle messages received from other peers based on 
    the type of message received. Pickle and base64 is used for deserializing data.

    handle_chain() - when a peer receives a chain (along with the mempool and balances)
    from another peer, this function is used to keep track of the longest received 
    chain. If the received chain is longer than the current longest received chain, 
    then this gets updated along with the received mempool and balances. Once the peer 
    has received all chains, its chain, mempool, and balances get updated, and request 
    mode is turned off. 

    handle_block() - after a peer broadcasts their mined block, this function checks if 
    the block is valid by comparing the previous hash with the hash of the last block on 
    their chain, and adds it to their chain. It also checks if the nonce is correct, and 
    handles forks by calling request_chains().

    request_chains() - once a fork is detected, the peer enters request mode, meaning it 
    should only handle message of type "request" or "chain". The peer then broadcasts a 
    request message to all other peers in the network to inform them to send their chain,
    mempool, and balances.

    send_chain() - when a peer receives a request message, it broadcasts its chain, 
    mempool, and balances to all other peers. Serializing the data is done through 
    pickle and base64.


CONNECTING/DISCONNECTING:
Our current protocol allows for connecting and disconnecting mid session.
In other words, if users A and B joins, makes some transactions, and user
C joins, then user C will have no problem catching up to the correct chain
and being in sync with the rest of the network.
When a peer leaves, it is also able to leave gracefully.

We did make a specific design consideration where if a peer disconnects, then
it is impossible for that same peer to reconnect. Essentially, once you leave
the blockchain network, you cannot participate in it anymore. You can only
reconnect as a different user. One can leave the blockchain network by hitting
Ctrl+C to terminate the flask server, which is mapped to a Peer node 1-to-1.
The tracker and the other nodes will realize the departure of the new node,
terminate associated connections (listening threads) and clean up book-keeping
data structures such as peers and peer_name_map.

-- Please enter design about network


WEBSITE:
The UI is designed to be fun and nostalgic, reflecting a blend of McDonald’s
charm and Minecraft aesthetics. Each instance of the website corresponds to 
a distinct peer in the blockchain network, launching a standalone web interface
tied to its own wallet. Users can set a username to identify their wallet, view
the list of active peers on the network, check their current balance, and send
collectables to others.

To enhance interactivity, the output section automatically refreshes every 10
seconds after listing users or checking balances. A live countdown timer is 
displayed to indicate the time remaining until the next refresh. Additionally,
once a username is set, the input field becomes disabled and is visually styled
to signal that the wallet identity is locked for the session.

The app.py file defines the web server that each blockchain peer uses to expose
its functionality to a local web interface. Each instance of this server is
tied to a single peer, initialized with a specific username and port. The
server is built using Flask and exposes a small set of RESTful endpoints that
allow the frontend that’s served from index.html to interact with the
blockchain backend via HTTP requests.

The root route / serves the main frontend interface. When a user accesses the
peer in a browser, this route returns the static index.html page from the
static/ directory. This page contains the McDonald’s/Minecraft-themed UI
through which users interact with the peer.

The /api/init/<username> route is responsible for initializing the peer. When
the user enters a username in the UI, a request is sent to this route, which
creates a Peer object. The peer is then started in a background thread,
allowing it to connect to the tracker, form connections with other peers, and
begin mining.

The /api/list route returns the current list of active peers on the network.
Each peer is represented by its name and public key. This route is used by
the frontend to populate the dropdown for selecting a transaction recipient.

The /api/balance route returns the current wallet balance of the peer. The
frontend uses this route to allow users to check how many coins they have
available for sending. If the peer is not initialized or its wallet is not
recognized, appropriate error responses are returned.

The /api/send route allows a user to send collectables to another peer. This
is a POST endpoint that accepts a JSON payload with the sender’s name, the
recipient’s public key, and the amount to send. The server calls the
peer.transfer() method, which creates and signs a transaction, then
broadcasts it to the network.