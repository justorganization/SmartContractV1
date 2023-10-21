from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import datetime
import os
import shutil


@pytest.fixture
def account():
    return get_account()


@pytest.fixture(scope="package")
def main_contract():
    return deploy_contract()


@pytest.fixture
def bets(main_contract):
    shutil.rmtree("logs")
    os.mkdir("logs")
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"logs/file_{formatted_datetime}.txt"

    account = get_account()
    createGame(0.03, 1.8, 1.7, 0, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    capacities = main_contract.getCapacities(gameID)
    with open(file_name, "w") as file:
        file.write(
            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}"
        )

    bets_A = {}
    bets_B = {}
    for i in range(random.randint(20, 50)):
        account = get_random_account()
        value = random.randint(1, 9) * 10 ** random.randint(15, 18)
        if random.randint(0, 1):
            isA = True
        else:
            isA = False
        capacities = main_contract.getCapacities(gameID)
        if isA:
            if value < capacities[0]:
                if main_contract.getDeposit(gameID, account, True) > 0:
                    addBetLiquidity(gameID, isA, main_contract, account, value)
                    bets_A[account] += value
                    with open(file_name, "a") as file:
                        file.write(
                            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Betted amount:{value/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}||Function type: AddBetLiquidity|| Team A"
                        )
                else:
                    makeABet(gameID, isA, main_contract, account, value)
                    bets_A[account] = value
                    with open(file_name, "a") as file:
                        file.write(
                            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Betted amount:{value/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}||Function type: CreateBet|| Team A"
                        )
        else:
            if value < capacities[1]:
                if main_contract.getDeposit(gameID, account, False) > 0:
                    addBetLiquidity(gameID, isA, main_contract, account, value)
                    bets_B[account] += value
                    with open(file_name, "a") as file:
                        file.write(
                            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Betted amount:{value/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}||Function type: AddBetLiquidity|| Team B"
                        )
                else:
                    makeABet(gameID, isA, main_contract, account, value)
                    bets_B[account] = value
                    with open(file_name, "a") as file:
                        file.write(
                            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Betted amount:{value/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}||Function type: CreateBet|| Team B"
                        )
    with open(file_name, "a") as file:
        tot_A = 0
        for i in bets_A.keys():
            tot_A += bets_A[i]
        tot_B = 0
        for i in bets_B.keys():
            tot_B += bets_B[i]
        file.write(
            f"\nCapacities:{capacities[0]/10**18},{capacities[1]/10**18}||Betted amount A:{tot_A/10**18}, B: {tot_B/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}"
        )
    return bets_A, bets_B, file_name
