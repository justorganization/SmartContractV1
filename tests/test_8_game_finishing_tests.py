from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_finishing_game(account, main_contract):
    throwData("sss", main_contract, account)
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    dataID = data_contract.getLastDataID() - 1
    createGame(0.03, 1.8, 1.7, dataID, main_contract, account, 10**18)
    gameID = main_contract.getLastGameID() - 1
    with pytest.raises(exceptions.VirtualMachineError):
        claimWinnings(gameID, main_contract, account)
    with pytest.raises(exceptions.VirtualMachineError):
        main_contract.closeGame(gameID)
    data_contract.endGames(dataID, True, False, {"from": get_account()})
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


def test_claim_winnings_A(main_contract, bets):
    bets_A, bets_B, x = bets
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    gameID = main_contract.getLastGameID() - 1
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, True, False, {"from": get_account()})
    for account in bets_A.keys():
        first = account.balance()
        first_total_amount = main_contract.getTotalAmmount(gameID)
        claimWinnings(gameID, main_contract, account)
        second_total_amount = main_contract.getTotalAmmount(gameID)
        second = account.balance()
        value = bets_A[account]
        bets_A[account] = 0
        coeficients = main_contract.getCoeficients(gameID)
        bank_fee = main_contract.getBankFee(gameID)
        capacities = main_contract.getCapacities(gameID)
        winning = value * (coeficients[0] / 10**9) * (1 - bank_fee / 10**18 - 0.001)

        assert math.isclose(second - winning, first, abs_tol=10**5) and math.isclose(
            first_total_amount - second_total_amount, winning, abs_tol=10**5
        )
        with pytest.raises(exceptions.VirtualMachineError):
            claimWinnings(gameID, main_contract, account)


def test_claim_winnings_B(main_contract, bets):
    bets_A, bets_B, x = bets
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    gameID = main_contract.getLastGameID() - 1
    coeficients = main_contract.getCoeficients(gameID)
    bank_fee = main_contract.getBankFee(gameID)
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, False, False, {"from": get_account()})
    for account in bets_B.keys():
        first = account.balance()
        first_total_amount = main_contract.getTotalAmmount(gameID)
        claimWinnings(gameID, main_contract, account)
        second_total_amount = main_contract.getTotalAmmount(gameID)
        second = account.balance()
        value = bets_B[account]
        bets_B[account] = 0

        winning = value * (coeficients[1] / 10**9) * (1 - bank_fee / 10**18 - 0.001)
        capacities = main_contract.getCapacities(gameID)
        assert math.isclose(second - winning, first, abs_tol=10**5) and math.isclose(
            first_total_amount - second_total_amount, winning, abs_tol=10**5
        )
        with pytest.raises(exceptions.VirtualMachineError):
            claimWinnings(gameID, main_contract, account)


def test_close_game(main_contract, bets):
    # preparation
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    bets_A, bets_B, file_name = bets

    total_amount = 10**18

    for i in bets_A.values():
        total_amount += i
    for i in bets_B.values():
        total_amount += i
    gameID = main_contract.getLastGameID() - 1
    assert total_amount == main_contract.getTotalAmmount(gameID)
    owners_raise = total_amount / 1000
    coeficients = main_contract.getCoeficients(gameID)
    bank_fee = main_contract.getBankFee(gameID)
    if random.randint(0, 1):
        isA = True
        bets_T = bets_A
    else:
        isA = False
        bets_T = bets_B
    with open(file_name, "a") as file:
        file.write(f"\nTotal Amount:{main_contract.getTotalAmmount(gameID)/10**18}")
        for i in bets_T.values():
            file.write(f"|{i/10**18}|")
    dataID = data_contract.getLastDataID() - 1
    data_contract.endGames(dataID, isA, False, {"from": get_account()})

    # random accounts claim winnings
    ran_accs = []
    balances_1 = []
    for i in range(random.randint(2, 4)):
        if (len(bets_T.keys())) != 0:
            account = random.choice(list(bets_T.keys()))
            fir = account.balance()
            claimWinnings(gameID, main_contract, account)
            with open(file_name, "a") as file:
                file.write(
                    f"\nTotal Amount:{main_contract.getTotalAmmount(gameID)/10**18}||Winning: {(account.balance()-fir)/10**18}|| Team {isA}"
                )
            total_amount -= account.balance() - fir
            balances_1.append(account.balance())
            del bets_T[account]
            ran_accs.append(account)

    # End game and collecting accounts data
    balances_not_claimed_1 = []
    _bets = []
    x = bets_T.keys()
    for i in x:
        balances_not_claimed_1.append(i.balance())
        _bets.append(bets_T[i])
    # Closing game, collecting balances data, calculating winnings, comparing calculated winnings with expected
    start_value_1 = get_account().balance()
    with open(file_name, "a") as file:
        file.write(
            f"\nTotal Amount before close:{main_contract.getTotalAmmount(gameID)/10**18}"
        )
    main_contract.closeGame(gameID, {"from": get_account()})
    start_value_2 = get_account().balance()
    print(start_value_1 / 10**18, start_value_2 / 10**18)
    with open(file_name, "a") as file:
        file.write(
            f"\nTotal Amount after close:{main_contract.getTotalAmmount(gameID)/10**18}"
        )
        for i in bets_T.values():
            file.write(f"|{i/10**18}|")
    balances_not_claimed_2 = []
    for i in x:
        balances_not_claimed_2.append(i.balance())

    for i in range(len(balances_not_claimed_1)):
        first = balances_not_claimed_1[i]
        second = balances_not_claimed_2[i]
        value = _bets[i]
        if isA:
            s = 0
        else:
            s = 1
        winning = value * (coeficients[s] / 10**9) * (1 - bank_fee / 10**18 - 0.001)
        total_amount -= winning
        assert math.isclose(second - first, winning, abs_tol=10**5)
    total_amount -= owners_raise
    # Trying to claim winnings after closing game
    for i in bets_T.keys():
        with pytest.raises(exceptions.VirtualMachineError):
            claimWinnings(gameID, main_contract, i)
    # Collecting and comparing data about accounts which claimed before close
    accs_balances_2 = []
    for i in ran_accs:
        accs_balances_2.append(i.balance())

    assert balances_1 == accs_balances_2

    assert math.isclose(
        start_value_1 + total_amount, get_account().balance(), abs_tol=10
    )
