import time
import hashlib
import json

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
            timestamp: when the block was made.
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