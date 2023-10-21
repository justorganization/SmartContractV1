from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_cancel_game(account, main_contract):
    createGame(0.03, 1.8, 1.7, 0, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    with pytest.raises(exceptions.VirtualMachineError):
        claimWinnings(gameID, main_contract, account)
    with pytest.raises(exceptions.VirtualMachineError):
        main_contract.closeGame(gameID)
    main_contract.endGame(gameID, True, True, {"from": get_account()})
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
        main_contract.closeGame(gameID, {"from": get_random_account()})


def test_claim_bets(main_contract, bets):
    bets_A, bets_B, x = bets
    bets_B_keys = bets_B.keys()
    _bets = {}
    for i in bets_A.keys():
        _bets[i] = bets_A[i]
        if i in bets_B_keys:
            _bets[i] += bets_B[i]
    gameID = main_contract.getLastGameID() - 1
    main_contract.endGame(gameID, True, True, {"from": get_account()})
    for account in _bets.keys():
        first = account.balance()
        first_total_amount = main_contract.getTotalAmmount(gameID)
        claimBet(gameID, main_contract, account)
        second_total_amount = main_contract.getTotalAmmount(gameID)
        second = account.balance()
        value = _bets[account]
        _bets[account] = 0
        bank_fee = main_contract.getBankFee(gameID)
        winning = value * (1 - bank_fee / 10**18 - 0.001)

        assert math.isclose(second - winning, first, abs_tol=10**5) and math.isclose(
            first_total_amount - second_total_amount, winning, abs_tol=10**5
        )
        with pytest.raises(exceptions.VirtualMachineError):
            claimBet(gameID, main_contract, account)


def test_close_canceled_game(main_contract, bets):
    bets_A, bets_B, file_name = bets

    total_amount = 10**18

    for i in bets_A.values():
        total_amount += i
    for i in bets_B.values():
        total_amount += i

    bets_B_keys = bets_B.keys()
    _bets = {}
    for i in bets_A.keys():
        _bets[i] = bets_A[i]
        if i in bets_B_keys:
            _bets[i] += bets_B[i]

    gameID = main_contract.getLastGameID() - 1
    assert total_amount == main_contract.getTotalAmmount(gameID)
    owners_raise = total_amount / 1000
    bank_fee = main_contract.getBankFee(gameID)
    main_contract.endGame(gameID, True, True, {"from": get_account()})
    # random accounts claim winnings
    ran_accs = []
    balances_1 = []
    for i in range(random.randint(2, 4)):
        if (len(_bets.keys())) != 0:
            account = random.choice(list(_bets.keys()))
            fir = account.balance()
            claimBet(gameID, main_contract, account)
            total_amount -= account.balance() - fir
            balances_1.append(account.balance())
            del _bets[account]
            ran_accs.append(account)

    # End game and collecting accounts data
    balances_not_claimed_1 = []
    _1_bets = []
    x = _bets.keys()
    for i in x:
        balances_not_claimed_1.append(i.balance())
        _1_bets.append(_bets[i])
    # Closing game, collecting balances data, calculating winnings, comparing calculated winnings with expected
    start_value_1 = get_account().balance()
    main_contract.closeCanceledGame(gameID, {"from": get_account()})
    start_value_2 = get_account().balance()

    balances_not_claimed_2 = []
    for i in x:
        balances_not_claimed_2.append(i.balance())

    for i in range(len(balances_not_claimed_1)):
        first = balances_not_claimed_1[i]
        second = balances_not_claimed_2[i]
        value = _1_bets[i]

        winning = value * (1 - bank_fee / 10**18 - 0.001)
        total_amount -= winning
        assert math.isclose(second - first, winning, abs_tol=10**5)
    total_amount -= owners_raise
    # Trying to claim winnings after closing game
    for i in _bets.keys():
        with pytest.raises(exceptions.VirtualMachineError):
            claimBet(gameID, main_contract, i)
    # Collecting and comparing data about accounts which claimed before close
    accs_balances_2 = []
    for i in ran_accs:
        accs_balances_2.append(i.balance())

    assert balances_1 == accs_balances_2

    assert math.isclose(
        start_value_1 + total_amount, get_account().balance(), abs_tol=10
    )
