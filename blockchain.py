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
class Transaction:
    """
    Transaction packages one transaction instance, containing
    info on the payer, payee, and the amount exchanged.

    to_message() converts the transaction into a string, which
    is then used in the hashing of the block.

    __str__() is simply for logging purposes
    """
    def __init__(self, amount: float, payer: str, payee: str):
        self.amount = amount
        self.payer = payer
        self.payee = payee

    def to_message(self):
        return f"{self.amount}:{self.payer}->{self.payee}"
    
    def __str__(self):
        return json.dumps(self.__dict__) #returns entire transaction as str object

class Block:
    """
    A block. Contains previous block's hash, the current transaction,
    the nonce (to produce a hash with x no. of 0s), and the timestamp
    of the transaction for ordering.

    Note, with this current design, its one transaction per block, which
    will need to be changed since this makes mining for a reward basically
    impossible (either you contain the reward, or the transaction, not both)

    hash() combines all of the block's data and returns the hash based on it.
    """
    def __init__(self, prev_hash: str, transaction, nonce=0):
        self.prev_hash = prev_hash
        self.transaction = transaction
        self.nonce = nonce
        self.timestamp = time.time()

    @property
    def hash(self):
        # turn block object into singular json entity
        block_data = {
            'prev_hash': self.prev_hash,
            'transaction': self.transaction.__dict__,
            'nonce': self.nonce,
            'timestamp': self.timestamp
        }
        # Hash on entire json object. Sort_keys so order of keys is consistent
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Chain:
    """
    A chain of blocks, only one should technically exist.

    __init__() initializes the very first 'genesis' block, giving
    100 coins to a fake user. The 'previous block' for the genesis
    block just has a hash of 64 0s.

    last_block() simply returns the previous block for convenience

    mine_block() solves for the nonce to produce x no. of 0s in the 
    hash and returns the block with that nonce once its done.

    add_block() verifies the signature/public key of the block, mines
    it, and appends it to the block chain.
    """
    def __init__(self):
        self.chain = [self.create_first_block()]

    def create_first_block(self):
        initial_tx = Transaction(100, "genesis", "sunny")
        return Block("0" * 64, initial_tx) 

    def last_block(self):
        return self.chain[-1]

    def mine_block(self, transaction):
        prev_hash = self.last_block().hash
        nonce = 0

        print("Mining...")
        while True:
            block = Block(prev_hash, transaction, nonce)
            if block.hash.startswith("00000"):  # at least four 0s
                print(f"Mined block: {block.hash} with nonce {nonce}")
                break
            nonce += 1
        
        return block

    def add_block(self, transaction, payer_public_key, sign):
        if not verify(transaction.to_message(), sign, payer_public_key):
            print("Invalid signature, block rejected.")
            return False
        
        block = self.mine_block(transaction)

        # Step 3: Add block to chain
        self.chain.append(block)
        print("Block added to chain.")
        return True
        
class Wallet:
    """
    Essentially identifies a user. Contains their public/private key, as well
    as their name.

    sign() creates a signature using the transaction and returns it as a str

    send_money() creates a transaction, gets the signature for that transaction,
    and adds a block to the blockchain containing that transaction.
    """
    def __init__(self, name):
        self.name = name
        self._sk = SigningKey.generate(curve=SECP256k1) # secret/private key
        self._vk = self._sk.verifying_key # verifying/pulbic key

        self.private_key = self._sk.to_string().hex()
        self.public_key = self._vk.to_string().hex()

    def sign(self, transaction):
        message = transaction.to_message()
        message_bytes = message.encode()
        raw_sign = self._sk.sign(message_bytes)
        return base64.b64encode(raw_sign).decode()

    def send_money(self, amount: float, payee_public_key: str, payee_name: str, chain):
        print(self.name + " sends " + str(amount) +  " to " + payee_name + "\n")
        transaction = Transaction(amount, self.public_key, payee_public_key)
        sign = self.sign(transaction)
        chain.add_block(transaction, self.public_key, sign)