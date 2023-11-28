from brownie import (
    accounts,
    config,
    MainContract,
    network,
    exceptions,
    MainLib,
    Contract,
    DataContract,
)
import os
from decimal import Decimal, getcontext
import pytest
import math
import matplotlib.pyplot as plt
import numpy as np


def roundation(nubmer: float, decimals: int):
    return int(nubmer * 10**decimals) / 10**decimals


def deploy_contract():
    account = get_account()
    accounts[1].transfer(account, "100 ether")
    MainLib.deploy({"from": account})
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
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    data_contract.throwData(data, {"from": account})


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


def createRandomGame(account, main_contract):
    koeficient_A = (
        int((1.5 * math.sqrt(2) * math.sqrt(-math.log(random.random()))) * 100000)
    ) / 100000
    koeficient_B = (
        int((1.5 * math.sqrt(2) * math.sqrt(-math.log(random.random()))) * 100000)
    ) / 100000
    bank_fee = int((random.random() * 10000)) / 100000
    bank_deposit = (random.random() * random.randint(1, 100)) * 10 ** random.randint(
        17, 19
    )
    print(bank_fee, koeficient_A, koeficient_B)
    dataID = random.randint(0, main_contract.getLastDataID())
    if main_contract.getIsDataRelevant(dataID):
        main_contract.createGame(
            bank_fee,
            koeficient_A,
            koeficient_B,
            dataID,
            {"from": account, "value": bank_deposit},
        )
        return main_contract.getLastGameID() - 1
    else:
        with pytest.raises(exceptions.VirtualMachineError):
            main_contract.createGame(
                bank_fee,
                koeficient_A,
                koeficient_B,
                dataID,
                {"from": account, "value": bank_deposit},
            )
            return 0


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


def claimBet(gameID: int, main_contract, account):
    main_contract.claimBet(gameID, {"from": account})


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


def generate_probability():
    sum = 0
    for i in range(12):
        sum += random.random()
    sum = 0.173 * (sum - 6) + 0.5
    if 0 < sum < 1:
        return sum
    else:
        return generate_probability()


def generate_coefficients():
    prob = generate_probability()
    sigm = (prob * prob - prob) / (-2.5)
    m = prob * prob * 0.12 - 0.12 * prob + 1
    sum_A = 0
    for i in range(12):
        sum_A += random.random()
    coef_A = int((sigm * (sum_A - 6) + m / prob) * 10000) / 10000

    sum_B = 0
    for i in range(12):
        sum_B += random.random()
    coef_B = int((sigm * (sum_B - 6) + m / (1 - prob)) * 10000) / 10000
    if coef_A > 50 or coef_A < 1 or coef_B > 50 or coef_B < 1:
        print(coef_A, coef_B, sigm, prob)
    return coef_A, coef_B


def draw_graph(num_of_dotes):
    x_acs = []
    y_acs = []
    for i in range(num_of_dotes):
        x, y = generate_coefficients()
        x_acs.append(x)
        y_acs.append(y)
    x_func = np.linspace(1.1, 10, 100)
    y_func = x_func / (x_func - 1)
    plt.plot(x_func, y_func, label="График y=1/x")
    plt.plot(x_acs, y_acs, "o", markersize=1)
    plt.xlabel("Coeffisients A")
    plt.ylabel("Coefficients B")
    plt.title("Game coefficients")
    plt.axis("equal")
    plt.show()
