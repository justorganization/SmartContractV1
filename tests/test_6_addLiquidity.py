from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random


def test_prepare(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    makeABet(gameID, True, main_contract, account, 10**16)
    makeABet(gameID, False, main_contract, account, 10**16)


def test_create_bet_second_time(account, main_contract):
    gameID = main_contract.getLastGameID() - 1
    with pytest.raises(exceptions.VirtualMachineError):
        makeABet(gameID, True, main_contract, account, 10**9)
    with pytest.raises(exceptions.VirtualMachineError):
        makeABet(gameID, False, main_contract, account, 10**9)


def test_add_liquidity(account, main_contract):
    gameID = main_contract.getLastGameID() - 1
    first = main_contract.getDeposit(gameID, account, True)
    value = random.randint(1, 5) * random.randint(16, 18)
    addBetLiquidity(gameID, True, main_contract, account, value)
    second = main_contract.getDeposit(gameID, account, True)
    assert first + value == second


def test_add_liquidity_2(account, main_contract):
    gameID = main_contract.getLastGameID() - 1
    value = random.randint(1, 5) * random.randint(16, 18)
    coeficients = main_contract.getCoeficients(gameID)
    capacities_1 = main_contract.getCapacities(gameID)
    addBetLiquidity(gameID, True, main_contract, account, value)
    cap_A = capacities_1[0] - value
    total_amount = main_contract.getTotalAmmount(gameID)
    cap_B = int(total_amount / (coeficients[1] - 10**9)) * 10**9
    capacities = main_contract.getCapacities(gameID)
    assert cap_B == capacities[1] and cap_A == capacities[0]
