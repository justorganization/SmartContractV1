from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random


def test_create_game_resistance_fee(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.3
    coef_A = 1.4
    coef_B = 1.6
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_coefA_1(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 1
    coef_B = 1.6
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_coefA_2(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 0.2
    coef_B = 1.6
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_coefB_1(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 1.8
    coef_B = 1
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_coefB_2(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 1.8
    coef_B = 0.3
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_data(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 1.8
    coef_B = 1
    data_ID = 1000
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_general_1(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.2
    coef_A = 1
    coef_B = 1
    data_ID = 1
    with pytest.raises(exceptions.VirtualMachineError):
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)


def test_create_game_resistance_general_2(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.05
    coef_A = 10 * random.random()
    coef_B = 10 * random.random()
    data_ID = random.randint(0, 11)
    if (
        bank_fee > 0.1
        or coef_A <= 1
        or coef_B <= 1
        or data_ID >= main_contract.getLastDataID()
    ):
        with pytest.raises(exceptions.VirtualMachineError):
            createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
    else:
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
        bank_fee_2 = main_contract.getBankFee(first_id) / 10**18
        coefs = main_contract.getCoeficients(first_id)
        data_ID_2 = main_contract.getGameData(first_id)
        coef_A_2 = coefs[0] / 10**9
        coef_B_2 = coefs[1] / 10**9
        assert (
            roundation(coef_A, 9) == coef_A_2
            and roundation(coef_B, 9) == coef_B_2
            and data_ID == data_ID_2
            and bank_fee == bank_fee_2
        )


@pytest.mark.parametrize("i", range(5))
def test_create_game_resistance_2_repeated(account, main_contract, i):
    test_create_game_resistance_general_2(account, main_contract)


def test_create_game_resistance_general_3(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.02
    coef_A = random.randint(0, 100) * random.random()
    coef_B = random.randint(0, 100) * random.random()
    data_ID = random.randint(0, 10)
    if (
        bank_fee > 0.1
        or coef_A <= 1
        or coef_B <= 1
        or data_ID >= main_contract.getLastDataID()
    ):
        with pytest.raises(exceptions.VirtualMachineError):
            createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
    else:
        createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
        bank_fee_2 = main_contract.getBankFee(first_id) / 10**18
        coefs = main_contract.getCoeficients(first_id)
        data_ID_2 = main_contract.getGameData(first_id)
        coef_A_2 = coefs[0] / 10**9
        coef_B_2 = coefs[1] / 10**9
        assert (
            roundation(coef_A, 9) == coef_A_2
            and roundation(coef_B, 9) == coef_B_2
            and data_ID == data_ID_2
            and bank_fee == bank_fee_2
        )


@pytest.mark.parametrize("i", range(5))
def test_create_game_resistance_3_repeated(account, main_contract, i):
    test_create_game_resistance_general_3(account, main_contract)
