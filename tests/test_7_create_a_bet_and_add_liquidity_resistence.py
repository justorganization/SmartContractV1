from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_prepare(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**18)


def test_make_bet_resistance_1(main_contract):
    first_id = main_contract.getLastGameID() - 1
    for i in range(50):
        account = get_random_account()
        value = int(random.random() * 10**8) * 10**10
        if random.randint(0, 1):
            isA = True
        else:
            isA = False
        capacities = main_contract.getCapacities(first_id)
        if isA:
            if value < capacities[0]:
                if main_contract.getDeposit(first_id, account, True) > 0:
                    first_bet = main_contract.getDeposit(first_id, account, True)
                    addBetLiquidity(first_id, isA, main_contract, account, value)
                    second_bet = main_contract.getDeposit(first_id, account, True)
                    assert account in main_contract.getUsersAlist(first_id)
                    assert first_bet + value == second_bet
                    with pytest.raises(exceptions.VirtualMachineError):
                        makeABet(first_id, isA, main_contract, account, value)
                else:
                    with pytest.raises(exceptions.VirtualMachineError):
                        addBetLiquidity(first_id, isA, main_contract, account, value)
                    makeABet(first_id, isA, main_contract, account, value)
                    first_bet = main_contract.getDeposit(first_id, account, True)
                    assert account in main_contract.getUsersAlist(first_id)
                    assert first_bet == value

            else:
                with pytest.raises(exceptions.VirtualMachineError):
                    makeABet(first_id, isA, main_contract, account, value)
        else:
            if value < capacities[1]:
                if main_contract.getDeposit(first_id, account, False) > 0:
                    first_bet = main_contract.getDeposit(first_id, account, False)
                    addBetLiquidity(first_id, isA, main_contract, account, value)
                    second_bet = main_contract.getDeposit(first_id, account, False)
                    assert account in main_contract.getUsersBlist(first_id)
                    assert first_bet + value == second_bet
                    with pytest.raises(exceptions.VirtualMachineError):
                        makeABet(first_id, isA, main_contract, account, value)
                else:
                    with pytest.raises(exceptions.VirtualMachineError):
                        addBetLiquidity(first_id, isA, main_contract, account, value)
                    makeABet(first_id, isA, main_contract, account, value)
                    first_bet = main_contract.getDeposit(first_id, account, False)
                    assert account in main_contract.getUsersBlist(first_id)
                    assert first_bet == value

            else:
                with pytest.raises(exceptions.VirtualMachineError):
                    makeABet(first_id, isA, main_contract, account, value)
