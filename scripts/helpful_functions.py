from brownie import accounts, config, MainContract, network
import os
from decimal import Decimal, getcontext


def roundation(nubmer: float, decimals: int):
    return int(nubmer * 10**decimals) / 10**decimals


def deploy_contract():
    account = get_account()
    accounts[1].transfer(account, "100 ether")

    main_contract = MainContract.deploy({"from": account})
    return main_contract


def get_random_account():
    return accounts[random.randint(2, 9)]


def get_account():
    if network.show_active() == "development":
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["from_key"])


def throwData(data: str, main_contract, account):
    main_contract.throwData(data, {"from": account})


def createGame(
    gameFee: float,
    coefA: float,
    coefB: float,
    gameData: int,
    main_contract,
    account,
    value=10**9,
):
    game_fee = gameFee * 10**18
    coef_A = coefA * 10**9
    coef_B = coefB * 10**9
    main_contract.createGame(
        game_fee, coef_A, coef_B, gameData, {"from": account, "value": value}
    )


def addGameLiquidity(gameID: int, main_contract, account, value=10**9):
    main_contract.addGameLiquidity(gameID, {"from": account, "value": value})


def addBetLiquidity(gameID: int, isA: bool, main_contract, account, value=10**9):
    main_contract.addLiquidityToBet(gameID, isA, {"from": account, "value": value})


def makeABet(
    gameID: int,
    isA: bool,
    main_contract,
    account,
    value=10**9,
):
    main_contract.makeABet(gameID, isA, {"from": account, "value": value})


def makeABet_safely(
    gameID: int,
    isA: bool,
    main_contract,
    account,
    value=10**9,
):
    main_contract.makeABet(gameID, isA, {"from": account, "value": value})


def claimWinnings(gameID: int, main_contract, account):
    main_contract.claimWinnings(gameID, {"from": account})


import random
import string


def generate_random_string():
    length = random.randint(20, 100)

    random_string = "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(length)
    )

    return random_string


def main():
    for i in range(9):
        print(accounts.add(initial_balance="10 ether").balance())
