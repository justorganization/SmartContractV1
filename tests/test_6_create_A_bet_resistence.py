from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_prepare(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**18)


def test_make_resistance(account, main_contract):
    first_id = main_contract.getLastGameID() - 1
    for i in range(100):
        value = int(random.random() * 10**8) * 10**10
        if random.randint(0, 1):
            isA = True
        else:
            isA = False
        capacities = main_contract.getCapacities(first_id)
        if isA:
            if value < capacities[0]:
                makeABet(first_id, isA, main_contract, account, value)
            else:
                with pytest.raises(exceptions.VirtualMachineError):
                    makeABet(first_id, isA, main_contract, account, value)
        else:
            if value < capacities[1]:
                makeABet(first_id, isA, main_contract, account, value)
            else:
                with pytest.raises(exceptions.VirtualMachineError):
                    makeABet(first_id, isA, main_contract, account, value)
