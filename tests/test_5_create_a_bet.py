from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_create_a_bet_1(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**17)
    first_id = main_contract.getLastGameID() - 1
    makeABet(first_id, True, main_contract, account)


def test_create_a_bet_2(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**17)
    first_id = main_contract.getLastGameID() - 1
    makeABet(first_id, True, main_contract, account)
    assert main_contract.getDeposit(first_id, account, True) == 10**9
    assert account in main_contract.getUsersAlist(first_id)


def test_create_a_bet_3(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**17)
    first_id = main_contract.getLastGameID() - 1
    total_amount_1 = main_contract.getTotalAmmount(first_id)
    makeABet(first_id, True, main_contract, account)
    total_amount_2 = main_contract.getTotalAmmount(first_id)
    assert total_amount_1 + 10**9 == total_amount_2


def test_create_a_bet_4(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**17)
    first_id = main_contract.getLastGameID() - 1
    value = 10**17
    coeficients = main_contract.getCoeficients(first_id)
    capacities_1 = main_contract.getCapacities(first_id)
    makeABet(first_id, True, main_contract, account, value)
    cap_A = capacities_1[0] - value
    total_amount = main_contract.getTotalAmmount(first_id)
    cap_B = int(total_amount / (coeficients[1] - 10**9)) * 10**9
    capacities = main_contract.getCapacities(first_id)
    assert cap_B == capacities[1] and cap_A == capacities[0]


def test_create_a_bet_5(account, main_contract):
    createGame(0.03, 1.8, 1.9, 0, main_contract, account, 10**17)
    first_id = main_contract.getLastGameID() - 1

    coeficients = main_contract.getCoeficients(first_id)
    value = 10**17
    capacities_1 = main_contract.getCapacities(first_id)
    makeABet(first_id, False, main_contract, account, value)
    cap_B = capacities_1[1] - value
    total_amount = main_contract.getTotalAmmount(first_id)
    cap_A = int(total_amount / (coeficients[0] - 10**9)) * 10**9
    capacities = main_contract.getCapacities(first_id)
    assert cap_B == capacities[1] and cap_A == capacities[0]


def test_create_a_bet_6(account, main_contract):
    with pytest.raises(exceptions.VirtualMachineError):
        value = 10**19
        first_id = main_contract.getLastGameID() - 1
        makeABet(first_id, False, main_contract, account, value)


def test_create_a_bet_7(account, main_contract):
    with pytest.raises(exceptions.VirtualMachineError):
        value = 10**19
        first_id = main_contract.getLastGameID() - 1
        makeABet(first_id, True, main_contract, account, value)
