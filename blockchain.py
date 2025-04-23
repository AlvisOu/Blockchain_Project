import json
import time
import hashlib
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import base64

def verify(data: str, signature: str, public_hex: str) -> bool:
    """
        Verifies signature with a user's public key.
    """
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(public_hex), curve=SECP256k1)
        return vk.verify(base64.b64decode(signature), data.encode())
    except Exception:
        return False

# Class definitions
    
class Wallet:
    """
        Essentially identifies a user. Contains their public/private key and
        their name.
    """
    def __init__(self, name: str):
        """
            name: the name of the user, doesn't need to be unique
            _sk: the secret key
            _vk: the verifying key
            private_key: the str version of _sk
            public_key: the str version of _vk
        """
        self.name = name
        self._sk = SigningKey.generate(curve=SECP256k1) # secret/private key
        self._vk = self._sk.verifying_key # verifying/pulbic key

        self.private_key = self._sk.to_string().hex()
        self.public_key = self._vk.to_string().hex()

    def sign(self, transaction):
        """
            Creates a signature using the transaction and returns it as a str.
        """
        message = transaction.to_sign()
        message_bytes = message.encode()
        raw_sign = self._sk.sign(message_bytes)
        return base64.b64encode(raw_sign).decode()

    def send_money(self, amount: float, payee: "Wallet", chain: "Chain"):
        """
            Adds a transaction to the mempool along with its signature.
        """
        print(self.name + " sends " + str(amount) +  " to " + payee.name)
        transaction = Transaction(amount, self, payee)
        sign = self.sign(transaction)
        chain.recv_transaction(transaction, sign)

class Transaction:
    """
        Transaction packages one transaction instance, containing
        info on the payer, payee, and the amount exchanged.
    """
    def __init__(self, amount: float, payer: Wallet, payee: Wallet):
        """
            amount: amount of money being sent
            payer: money sender
            payee: money receiver
        """
        self.amount = amount
        self.payer = payer
        self.payee = payee

    def to_dict(self): # for hashing
        """
            Converts the transaction into a formatted dictionary which
            is then used in the hashing of the block.
        """
        return {
            "amount": self.amount,
            "payer": self.payer.public_key if self.payer else "coinbase",
            "payee": self.payee.public_key
        }

    def to_sign(self): # changes into payload for signature
        """
            Converts the transaction into a string which is used for signing
            the block.
        """
        return f"{self.amount}:{self.payer.public_key}->{self.payee.public_key}"
    
class Block:
    """
        A block. Contains previous block's hash, a list of transactions,
        the nonce (to produce a hash with x no. of 0s), and the timestamp
        of the transaction.
    """
    def __init__(self, prev_hash: str, transactions: list, nonce: int = 0):
        """
            prev_hash: hash of previous block. 64 0s for the first block
            transactions: list of transactions associated with this block
            nonce: a specific value that makes hash start with X number of 0s
            timestamp: when the block was made
        """
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = time.time()

    @property
    def hash(self):
        """
            hash() combines all of the block's data and returns the hash based on it.
        """
        # turn block object into singular json entity
        block_data = {
            'prev_hash': self.prev_hash,
            'transaction': [tx.to_dict() for tx in self.transactions],
            'nonce': self.nonce,
            'timestamp': self.timestamp
        }
        # Hash on entire json object. Sort_keys so order of keys is consistent
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()



class Chain:
    """
        The 'block-chain'. Responsible for adding blocks, managing balances,
        and mining blocks.
    """
    def __init__(self):
        """
            Sets up the chain with a genesis transaction and wallet.

            coinbase: the 'bank', source of reward crypto and initial 100 coins
            balances: dict of balances for each wallet,
            reward: reward of mining one block
            genesis_block: the very first block where coinbase gives the first
                           user 100 coins
            genesis_wallet: the first 'real' user (Satoshi Nakamoto)
            chain: The actual 'chain', represented as a list of blocks
            mempool: list of transactions not commited to blockchain yet
        """
        self.coinbase = Wallet("coinbase")
        self.balances = {} # dict[Wallet.public_key(str), [Wallet.name(str), balance(float)]]
        self.reward = 50 # reward for mining

        genesis_block, self.genesis_wallet = self.create_first_block()
        self.chain = [genesis_block]
        self.mempool: list[tuple[Transaction, str]] = [] # List of (tx, signature)
        self.update_balances(genesis_block.transactions[0])
    
    def create_first_block(self):
        """
            Called during genesis, gives the first user
            100 coins from the coinbase.
        """
        first_wallet = Wallet("Satoshi Nakamoto")
        initial_tx = Transaction(100, self.coinbase, first_wallet)
        return Block("0" * 64, [initial_tx]), first_wallet
    
    def recv_transaction(self, transaction: Transaction, sign: str):
        """
            Checks:
                if a transaction and signature matches
                if a user has enough money to make the transaction
            Put transaction into mempool if it is valid.
        """
        if not verify(transaction.to_sign(), sign, transaction.payer.public_key):
            print("Invalid signature, block rejected.")
            return False
        
        if (transaction.payer != "coinbase" and 
            (self.get_effective_balance(transaction.payer) < transaction.amount)):
            print("Not enough money, block rejected.")
            return False
        
        self.mempool.append((transaction, sign))
        print("Transaction added to mempool")
        return True

    def mine_block(self, miner: Wallet):
        """
            Iterates over nonce values until it produces a hash starting with
            X number of 0s. Once mined, calls add_block to append to the chain.
        """
        if len(self.mempool) <= 0:
            print("No transactions to mine")
            return None
        
        reward_tx = Transaction(self.reward, self.coinbase, miner)
        transactions = [reward_tx] + [tx for tx, _ in self.mempool]

        prev_hash = self.chain[-1].hash
        nonce = 0
        while True:
            block = Block(prev_hash, transactions, nonce)
            if block.hash.startswith("0000"):
                break
            nonce += 1
        
        self.add_block(block)
        return block

    def add_block(self, block: Block):
        """
            Appends a block to the blockchain and removes the transactions
            in the block from the mempool.
        """
        self.chain.append(block)
        for tx in block.transactions:
            self.update_balances(tx)

        # keep transactions that were not in the block
        self.mempool = [(tx, sign) for (tx, sign) in self.mempool if tx not in block.transactions]
        print("Block mined and added to chain.")
    
    def update_balances(self, transaction: Transaction):
        """
            Updates the balance dictionary for affected Wallets.
            Also responsible for adding new users to balances.
        """
        payer = transaction.payer
        payee = transaction.payee
        amount = transaction.amount
        
        # Don't care about coinbase's balance. Effectively infinite.
        if payer.name != "coinbase":
            if payer.public_key not in self.balances:
                self.balances[payer.public_key] = [payer.name, 0]
            self.balances[payer.public_key][1] -= amount
        
        if payee.public_key not in self.balances:
            self.balances[payee.public_key] = [payee.name, 0]
        self.balances[payee.public_key][1] += amount

    def get_balance(self, payer: Wallet) -> float: # balance without mempool
        """
            Returns the balance of a Wallet.
        """
        return self.balances.get(payer.public_key, ["", 0])[1]
    
    def get_effective_balance(self, payer: Wallet) -> float: #balance with mempool
        """
            Calculates balance of Wallets according to mempool transactions.
            Mainly to prevent double spending and spamming transactions before
            the next block has been created.
        """
        balance = self.get_balance(payer)
        for tx, _ in self.mempool:
            if tx.payer and tx.payer.public_key == payer.public_key:
                balance -= tx.amount
            elif tx.payee and tx.payee.public_key == payer.public_key:
                balance += tx.amount
        return balance

    def print_balances(self):
        """
            Prints out balances of all Wallets
        """
        for public_key, balance_arr in self.balances.items():
            print("(" + balance_arr[0] + ", " + public_key[:10] + ")" + " has " + str(balance_arr[1]))
        print()

    def print_chain(self, start_time: float = 0):
        """
            Prints out the blockchain.
        """
        print("\n=== Blockchain ===")
        for idx, block in enumerate(self.chain):
            print(f"Block #{idx}")
            print(f"  Hash:      {block.hash}")
            print(f"  Prev Hash: {block.prev_hash}")
            print(f"  Transactions:")
            for tx in block.transactions:
                print(f"     TX:     {tx.amount} from {tx.payer.name} to {tx.payee.name}")
            print(f"  Nonce:     {block.nonce}")
            print(f"  Time:      {block.timestamp - start_time:.2f}")
            print()


