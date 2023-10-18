from brownie import accounts, config, MainContract, network
import os
from scripts.helpful_functions import *


def deploy_simple_storage():
    account = get_account()
    main_contract = MainContract.deploy({"from": account})
    throwData("Suzik", main_contract, account)

    bank_fee = random.random()
    coef_A = 1.5
    coef_B = 1.8
    data_ID = 0
    createGame(0.01, coef_A, coef_B, 0, main_contract, account, 10**17)
    main_contract.endGame(0, True)
    main_contract.closeGame(0)


def main():
    deploy_simple_storage()
