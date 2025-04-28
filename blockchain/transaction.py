from __future__ import annotations
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from blockchain.wallet import Wallet

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
            timestamp: when the transaction was created
        """
        self.amount = amount
        self.payer = payer
        self.payee = payee
        self.timestamp = time.time()

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
        return f"{self.amount}:{self.payer.public_key}->{self.payee.public_key}:{self.timestamp}"