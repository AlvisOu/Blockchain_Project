from blockchain import Chain, Wallet
import time

if __name__ == "__main__":
    start_time = time.time()
    # Create blockchain instance
    chain = Chain()

    # Create two wallets
    sunny = Wallet("Sunny")
    alvis = Wallet("Alvis")
    sky = Wallet("Sky")
    john = Wallet("John")

    # sunny sends alvis 20 bucks
    # alvis sends sky 10 bucks
    # john sends sky 30 bucks
    # sky sends sunny 40 bucks

    # genesis_wallet only exists in context of chain
    chain.genesis_wallet.send_money(20, sunny, chain)
    chain.mine_block(john)
    chain.print_balances()

    sunny.send_money(10, sky, chain)
    sunny.send_money(10, john, chain)
    chain.print_balances()
    john.send_money(50, sunny, chain)
    sunny.send_money(10, sky, chain)
    chain.mine_block(sky)

    # sunny.send_money(20, alvis, chain)
    # alvis.send_money(10, sky, chain)
    # john.send_money(30, sky, chain)
    # sky.send_money(40, sunny, chain)

    chain.print_chain(start_time)
    chain.print_balances()