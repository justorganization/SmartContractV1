from brownie import accounts, config, MainContract, network
import os
from decimal import Decimal, getcontext


def deploy_contract():
    account = get_account()
    main_contract = MainContract.deploy({"from": account})
    return main_contract


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def throwData(data: str, main_contract, account):
    main_contract.throwData(data, {"from": account})


def createGame(
    gameFee: float, coefA: float, coefB: float, gameData: int, main_contract, account
):
    game_fee = gameFee * 10**18
    coef_A = coefA * 10**9
    coef_B = coefB * 10**9
    print(game_fee, coef_A, coef_B)
    main_contract.createGame(game_fee, coef_A, coef_B, gameData, {"from": account})


import random
import string


def generate_random_string():
    length = random.randint(20, 100)

    random_string = "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(length)
    )

    return random_string
