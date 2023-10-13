from brownie import accounts, config, MainContract, network
import os
from scripts.helpful_functions import *


def deploy_simple_storage():
    account = get_account()
    main_contract = MainContract.deploy({"from": account})
    x = main_contract.getOwner()
    data = "Some information about the game"
    first_id = main_contract.getLastDataID()
    main_contract.throwData(data, {"from": account})
    second_id = main_contract.getLastDataID()
    print(first_id, second_id)
    print(main_contract.getGamesData(first_id))


def main():
    deploy_simple_storage()
