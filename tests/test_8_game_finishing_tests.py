from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


@pytest.fixture(scope="module")
def bets(main_contract):
    account = get_account()
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    bets_A = {}
    bets_B = {}
    for i in range(random.randint(20, 50)):
        account = get_random_account()
        value = random.randint(1, 9) * random.randint(15, 18)
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
                else:
                    makeABet(gameID, isA, main_contract, account, value)
                    bets_A[account] = value
        else:
            if value < capacities[1]:
                if main_contract.getDeposit(gameID, account, False) > 0:
                    addBetLiquidity(gameID, isA, main_contract, account, value)
                    bets_B[account] += value
                else:
                    makeABet(gameID, isA, main_contract, account, value)
                    bets_B[account] = value
    return bets_A, bets_B


def test_finishing_game(account, main_contract):
    gameID = main_contract.getLastGameID() - 1
    main_contract.endGame(gameID, True)
    with pytest.raises(exceptions.VirtualMachineError):
        makeABet(gameID, True, main_contract, account, 10**15)
    with pytest.raises(exceptions.VirtualMachineError):
        addBetLiquidity(gameID, True, main_contract, account, 10**15)
    with pytest.raises(exceptions.VirtualMachineError):
        makeABet(gameID, False, main_contract, account, 10**15)
    with pytest.raises(exceptions.VirtualMachineError):
        addBetLiquidity(gameID, False, main_contract, account, 10**15)
    with pytest.raises(exceptions.VirtualMachineError):
        addGameLiquidity(gameID, main_contract, account, 10**17)


def test_claime_winnings(main_contract, bets):
    gameID = main_contract.getLastGameID() - 1
    account = get_random_account()
    bets_A, bets_B = bets
    while account not in bets_A.keys():
        account = get_random_account()
    main_contract.endGame(gameID, True)
    print(main_contract.getDeposit(gameID, account, True))
    first = account.balance()
    claimWinnings(gameID, main_contract, account)
    second = account.balance()
    value = bets_A[account]
    coeficients = main_contract.getCoeficients(gameID)
    bank_fee = main_contract.getBankFee(gameID)
    winning = value * (coeficients[0] / 10**9) * (1 - bank_fee / 10**18 - 0.001)
    assert second - winning == first
