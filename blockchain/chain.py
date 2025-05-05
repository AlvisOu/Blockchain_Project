from blockchain.wallet import Wallet
from blockchain.transaction import Transaction
from blockchain.block import Block
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
        self.coinbase_public_key = '0x0'
        self.balances = {} # dict[Wallet.public_key(str), balance(float)]
        self.reward = 50 # reward for mining

        genesis_block, self.genesis_wallet = self.create_first_block()
        self.chain = [genesis_block]
        self.mempool: list[tuple[Transaction, str]] = [] # List of (tx, signature)
        self.update_balances(genesis_block.transactions[0])
        
    def create_first_block(self):
        first_wallet_public_key = '0x1'
        initial_tx = Transaction(100, self.coinbase, first_wallet_public_key)
        return Block("0" * 64, [initial_tx], genesis=True), first_wallet_public_key
    
    def recv_transaction(self, transaction: Transaction, sign: str, receiving: bool):
        """
            Checks:
                if a transaction and signature matches
                if a user has enough money to make the transaction
            Put transaction into mempool if it is valid.
        """
        if not verify(transaction.to_sign(), sign, transaction.payer.public_key):
            status = "Invalid signature, transaction rejected."
            print(status)
            return False, status
        
        if (transaction.payer != "coinbase" and 
            (self.get_effective_balance(transaction.payer) < transaction.amount) and not receiving):
            status = "Not enough money, transaction rejected."
            print(status)
            return False, status
        
        if (transaction.payee_public_key == '0x0') and not receiving:
            status = "Cannot give money to coinbase, transaction rejected."
            print(status)
            return False, status
        
        self.mempool.append((transaction, sign))
        status = "Transaction added to mempool"
        print(status)
        return True, status

    def mine_block(self, miner: Wallet):
        """
            Iterates over nonce values until it produces a hash starting with
            X number of 0s. Once mined, calls add_block to append to the chain.
        """
        reward_tx = Transaction(self.reward, self.coinbase, miner.public_key)
        transactions = [reward_tx] + [tx for tx, _ in self.mempool]

        prev_hash = self.chain[-1].hash
        nonce = 0
        while True:
            block = Block(prev_hash, transactions, nonce)
            if self.chain[-1].hash != prev_hash: # other peer won
                return False
            if block.hash.startswith("0000"):
                break
            nonce += 1
        
        print(f"{miner.name} Block mined!")
        return block

    def add_block(self, block: Block):
        """
            Appends a block to the blockchain and removes the transactions
            in the block from the mempool.
        """
        self.chain.append(block)
        for tx in block.transactions:
            self.update_balances(tx)
        
        block_transactions = [tx.to_dict() for tx in block.transactions]

        # keep transactions that were not in the block
        self.mempool = [(tx, sign) for (tx, sign) in self.mempool if tx.to_dict() not in block_transactions]
        
        print("Block added.")

    def update_balances(self, transaction: Transaction):
        """
            Updates the balance dictionary for affected Wallets.
            Also responsible for adding new users to balances.
        """
        payer = transaction.payer
        payee_public_key = transaction.payee_public_key
        amount = transaction.amount
        
        # Don't care about coinbase's balance. Effectively infinite.
        if payer.name != "coinbase":
            if payer.public_key not in self.balances:
                self.balances[payer.public_key] = 0
            self.balances[payer.public_key] -= amount
        
        if payee_public_key not in self.balances:
            self.balances[payee_public_key] = 0
        self.balances[payee_public_key] += amount

    def get_balance(self, payer: Wallet) -> float: # balance without mempool
        """
            Returns the balance of a Wallet.
        """
        return self.balances.get(payer.public_key, 0)
    
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
            elif tx.payee_public_key == payer.public_key:
                balance += tx.amount
        return balance

    def print_balances(self):
        """
            Prints out balances of all Wallets
        """
        for public_key, balance in self.balances.items():
            print(public_key[:8]  + " has " + str(balance))

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
                print(f"     TX:     {tx.amount} from {tx.payer.name} to {tx.payee_public_key[:8]}")
            print(f"  Nonce:     {block.nonce}")
            print(f"  Time:      {block.timestamp - start_time:.2f}")
            print()