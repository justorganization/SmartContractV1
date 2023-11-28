from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_cancel_game(account, main_contract):
    throwData("piskodaw", main_contract, account)
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    dataID = data_contract.getLastDataID() - 1
    createGame(0.03, 1.8, 1.7, dataID, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    with pytest.raises(exceptions.VirtualMachineError):
        claimWinnings(gameID, main_contract, account)
    with pytest.raises(exceptions.VirtualMachineError):
        main_contract.closeGame(gameID)
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, True, True, {"from": get_account()})
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

    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    _bets = {}
    for key, value in bets_A.items():
        _bets[key] = _bets.get(key, 0) + value

    for key, value in bets_B.items():
        _bets[key] = _bets.get(key, 0) + value

    gameID = main_contract.getLastGameID() - 1
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, True, True, {"from": get_account()})
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


def test_close_canceled_game(main_contract, bets):
    start_value_1 = get_account().balance()
    total_amount = 10**18
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    bets_A, bets_B, file_name = bets

    _bets = {}
    for key, value in bets_A.items():
        _bets[key] = _bets.get(key, 0) + value

    for key, value in bets_B.items():
        _bets[key] = _bets.get(key, 0) + value

    for value in _bets.values():
        total_amount += value
    gameID = main_contract.getLastGameID() - 1
    assert total_amount == main_contract.getTotalAmmount(gameID)
    owners_raise = total_amount / 1000
    bank_fee = main_contract.getBankFee(gameID)
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, True, True, {"from": get_account()})
    total_amount_0 = main_contract.getTotalAmmount(gameID)
    # random accounts claim winnings
    ran_accs = []
    balances_1 = []
    for i in range(random.randint(2, 4)):
        if (len(_bets.keys())) != 0:
            account = random.choice(list(_bets.keys()))
            fir = account.balance()
            claimBet(gameID, main_contract, account)
            total_amount -= account.balance() - fir
            with open(file_name, "a") as file:
                tot_A = 0
                for j in accounts:
                    tot_A += main_contract.getDeposit(gameID, j, True)
                tot_B = 0
                for j in accounts:
                    tot_B += main_contract.getDeposit(gameID, j, False)
                file.write(
                    f"\nClaimBet close: Betted amount A:{tot_A/10**18}, B: {tot_B/10**18}||Total Amount(contract):{main_contract.getTotalAmmount(gameID)/10**18}, Total Amount(simulating):{total_amount/ 10**18}, winning: {(account.balance() - fir)/10**18}"
                )
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

    total_amount_1 = main_contract.getTotalAmmount(gameID)
    with open(file_name, "a") as file:
        tot_A = 0
        for i in accounts:
            tot_A += main_contract.getDeposit(gameID, i, True)
        tot_B = 0
        for i in accounts:
            tot_B += main_contract.getDeposit(gameID, i, False)
        file.write(
            f"\nBefore close: Betted amount A:{tot_A/10**18}, B: {tot_B/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}"
        )
    main_contract.closeCanceledGame(gameID, {"from": get_account()})
    with open(file_name, "a") as file:
        tot_A = 0
        for i in accounts:
            tot_A += main_contract.getDeposit(gameID, i, True)
        tot_B = 0
        for i in accounts:
            tot_B += main_contract.getDeposit(gameID, i, False)
        file.write(
            f"\nAfter close: Betted amount A:{tot_A/10**18}, B: {tot_B/10**18}||Total Amount:{main_contract.getTotalAmmount(gameID)/10**18}"
        )
    total_amount_2 = main_contract.getTotalAmmount(gameID)
    with open(file_name, "a") as file:
        file.write(
            f"Total amount before claim: {total_amount_0 / 10**18}, after claim:{total_amount_1 / 10**18}, after close:{total_amount_2 / 10**18}"
        )
    start_value_2 = get_account().balance()

    balances_not_claimed_2 = []
    for i in x:
        balances_not_claimed_2.append(i.balance())

    for i in range(len(balances_not_claimed_1)):
        first = balances_not_claimed_1[i]
        second = balances_not_claimed_2[i]
        value = list(_bets.values())[i]

        winning = value * (1 - bank_fee / 10**18 - 0.001)
        total_amount -= winning
        with open(file_name, "a") as file:
            tot_A = 0
            for j in accounts:
                tot_A += main_contract.getDeposit(gameID, j, True)
            tot_B = 0
            for j in accounts:
                tot_B += main_contract.getDeposit(gameID, j, False)
            file.write(
                f"\nSimulating winnings: Betted amount A:{tot_A/10**18}, B: {tot_B/10**18}||Total Amount(contract):{main_contract.getTotalAmmount(gameID)/10**18}, Total Amount(simulating):{total_amount/ 10**18}, winning: {winning/10**18}"
            )
        assert math.isclose(second - first, winning, abs_tol=10**5)
    total_amount -= owners_raise
    print(owners_raise)
    # Collecting and comparing data about accounts which claimed before close
    accs_balances_2 = []
    for i in ran_accs:
        accs_balances_2.append(i.balance())

    assert balances_1 == accs_balances_2

    assert math.isclose(
        start_value_1 + total_amount, get_account().balance(), abs_tol=10
    )
