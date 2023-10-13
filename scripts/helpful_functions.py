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


def createGame(
    gameFee: float, coefA: float, coefB: float, gameData: int, main_contract
):
    getcontext().prec = 18
    game_fee = Decimal(gameFee) * 10**18
    getcontext().prec = 9
    coef_A = Decimal(coefA) * 10**9
    coef_B = Decimal(coefB) * 10**9
    main_contract.createGame(game_fee, coef_A, coef_B, gameData)
