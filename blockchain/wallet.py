from __future__ import annotations
from typing import TYPE_CHECKING
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from blockchain.transaction import Transaction

if TYPE_CHECKING:
    from blockchain.chain import Chain

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

    def send_money(self, amount: float, payee_public_key: str, chain: "Chain"):
        """
            Adds a transaction to the mempool along with its signature.
        """
        print(self.name + " sends " + str(amount) +  " to " + payee_public_key)
        transaction = Transaction(amount, self, payee_public_key)
        sign = self.sign(transaction)
        chain.recv_transaction(transaction, sign)
