from scripts.helpful_functions import *
from brownie import network, MainContract
import pytest


@pytest.fixture
def account():
    return get_account()


@pytest.fixture(scope="module")
def main_contract():
    return deploy_contract()


def test_deploy(account, main_contract):
    assert account == main_contract.whichOwner()


def test_throwing_data_1(account, main_contract):
    data = "Some information about the game"
    first_id = main_contract.getLastDataID()
    main_contract.throwData(data, {"from": account})
    second_id = main_contract.getLastDataID()
    assert main_contract.getGamesData(first_id) == data and first_id == second_id - 1


def test_throwing_data_2(account, main_contract):
    first_string = generate_random_string()
    second_sctring = generate_random_string()
    third_string = generate_random_string()
    main_contract.throwData(first_string, {"from": account})
    main_contract.throwData(second_sctring, {"from": account})
    main_contract.throwData(third_string, {"from": account})
    assert (
        main_contract.getGamesData(1) == first_string
        and main_contract.getGamesData(2) == second_sctring
        and main_contract.getGamesData(3) == third_string
    )


def test_create_game_1(account, main_contract):
    first_id = main_contract.getLastGameID()
    createGame(0.1, 1.4, 1.6, 1, main_contract, account)
    second_id = main_contract.getLastGameID()
    assert first_id == second_id - 1


def test_create_game_2(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.1
    coef_A = 1.4
    coef_B = 1.6
    data_ID = 1
    createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
    bank_fee_2 = main_contract.getBankFee(first_id) / 10**18
    coefs = main_contract.getCoeficients(first_id)
    data_ID_2 = main_contract.getGameData(first_id)
    coef_A_2 = coefs[0] / 10**9
    coef_B_2 = coefs[1] / 10**9
    assert (
        coef_A == coef_A_2
        and coef_B == coef_B_2
        and data_ID == data_ID_2
        and bank_fee == bank_fee_2
    )
