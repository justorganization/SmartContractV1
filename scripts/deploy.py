from brownie import accounts, config, MainContract, network
import os


def deploy_simple_storage():
    account = accounts[0]
    main_contract = MainContract.deploy({"from": account})
    main_contract.createGame(100, 2000000000, 2000000000, 0, {"from": account})

    


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_simple_storage()