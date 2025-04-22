from blockchain import Transaction, Block, Chain, Wallet, verify

if __name__ == "__main__":
    # Create blockchain instance
    chain = Chain()

    # Create two wallets
    alice = Wallet("Alice")
    bob = Wallet("Bob")

    # Alice sends Bob 10 coins
    print("\nAlice sending 10 coins to Bob...\n")
    alice.send_money(10, bob.public_key, bob.name, chain)

    # Print entire chain
    print("\n=== Blockchain ===")
    for idx, block in enumerate(chain.chain):
        print(f"Block #{idx}")
        print(f"  Hash:      {block.hash}")
        print(f"  Prev Hash: {block.prev_hash}")
        print(f"  TX:        {block.transaction.amount} from {block.transaction.payer[:10]}... to {block.transaction.payee[:10]}...")
        print(f"  Nonce:     {block.nonce}")
        print(f"  Time:      {block.timestamp}")
        print()
