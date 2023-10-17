from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


@pytest.fixture
def bets(main_contract):
    account = get_account()
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    bets_A = {}
    bets_B = {}
    for i in range(random.randint(20, 50)):
        account = get_random_account()
        value = random.randint(1, 9) ** random.randint(15, 18)
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
    with pytest.raises(exceptions.VirtualMachineError):
        claimWinnings(gameID, main_contract, account)
    with pytest.raises(exceptions.VirtualMachineError):
        MainContract.closeGame(gameID)
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
    with pytest.raises(exceptions.VirtualMachineError):
        MainContract.closeGame(gameID, {"from": get_random_account()})


def test_claim_winnings_A(main_contract, bets):
    bets_A, bets_B = bets
    gameID = main_contract.getLastGameID() - 1
    main_contract.endGame(gameID, True)
    for account in bets_A.keys():
        first = account.balance()
        claimWinnings(gameID, main_contract, account)
        second = account.balance()
        value = bets_A[account]
        bets_A[account] = 0
        coeficients = main_contract.getCoeficients(gameID)
        bank_fee = main_contract.getBankFee(gameID)
        winning = value * (coeficients[0] / 10**9) * (1 - bank_fee / 10**18 - 0.001)
        assert math.isclose(second - winning, first, abs_tol=10**5)
        with pytest.raises(exceptions.VirtualMachineError):
            claimWinnings(gameID, main_contract, account)


def test_claim_winnings_B(main_contract, bets):
    bets_A, bets_B = bets
    gameID = main_contract.getLastGameID() - 1
    main_contract.endGame(gameID, False)
    for account in bets_B.keys():
        first = account.balance()
        claimWinnings(gameID, main_contract, account)
        second = account.balance()
        value = bets_B[account]
        bets_B[account] = 0
        coeficients = main_contract.getCoeficients(gameID)
        bank_fee = main_contract.getBankFee(gameID)
        winning = value * (coeficients[1] / 10**9) * (1 - bank_fee / 10**18 - 0.001)
        assert math.isclose(second - winning, first, abs_tol=10**5)
        with pytest.raises(exceptions.VirtualMachineError):
            claimWinnings(gameID, main_contract, account)


def test_close_game(main_contract, bets):
    bets_A, bets_B = bets
    gameID = main_contract.getLastGameID() - 1

    if random.randint(0, 1):
        isA = True
        bets_T = bets_A
    else:
        isA = False
        bets_T = bets_B
    main_contract.endGame(gameID, isA)
    ran_accs = []
    for i in range(random.randint(2, 4)):
        if (bets_T.keys()) != 0:
            account = random.choice(list(bets_T.keys()))
            del bets_T[account]
            claimWinnings(gameID, main_contract, account)
            ran_accs.append(account)

    accs_balances_1 = []
    for i in ran_accs:
        accs_balances_1.append(i.balance())
    main_contract.endGame(gameID, isA)
    MainContract.closeGame(gameID, {"from": get_account()})
    accs_balances_2 = []
    for i in ran_accs:
        accs_balances_2.append(i.balance())
    assert accs_balances_1 == accs_balances_2
