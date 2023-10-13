from brownie import accounts, config, MainContract, network
import os
from scripts.helpful_functions import *


def deploy_simple_storage():
    account = get_account()
    main_contract = MainContract.deploy({"from": account})
    throwData("sasas", main_contract, account)
    throwData("sasa1s", main_contract, account)
    throwData("sasa2s", main_contract, account)
    createGame(0.1, 1.4, 1.6, 0, main_contract, account)
    print(main_contract.getCoeficients(0), main_contract.getBankFee(0))


def main():
    deploy_simple_storage()
