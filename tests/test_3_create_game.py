from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions, DataContract, Contract
import pytest
import random
import math


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
    data_ID_2 = main_contract.game(first_id)
    coef_A_2 = coefs[0] / 10**9
    coef_B_2 = coefs[1] / 10**9
    assert (
        coef_A == coef_A_2
        and coef_B == coef_B_2
        and data_ID == data_ID_2
        and bank_fee == bank_fee_2
    )


def test_create_game_3(account, main_contract):
    first_id = main_contract.getLastGameID()
    bank_fee = 0.1
    coef_A = 1.4
    coef_B = 1.6
    data_ID = 1
    value = 10**18
    createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account, value)
    bank_fee_2 = main_contract.getBankFee(first_id) / 10**18
    coefs = main_contract.getCoeficients(first_id)
    data_ID_2 = main_contract.game(first_id)
    coef_A_2 = coefs[0] / 10**9
    coef_B_2 = coefs[1] / 10**9
    value_2 = main_contract.getTotalAmmount(first_id)
    value_3 = main_contract.getBankDeposit(first_id)
    assert (
        coef_A == coef_A_2
        and coef_B == coef_B_2
        and data_ID == data_ID_2
        and bank_fee == bank_fee_2
        and value_2 == value
        and value_3 == value
    )


def test_create_game_4(account, main_contract):
    first_id = main_contract.getLastGameID()
    value = 10**19

    bank_fee = 0.1
    coef_A = 1.4
    coef_B = 1.6
    data_ID = 1

    cap_A = (int((value / (coef_A - 1)) / 10**9)) * 10**9
    cap_B = (int((value / (coef_B - 1)) / 10**9)) * 10**9

    createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account, value)
    capacities = main_contract.getCapacities(first_id)
    bank_fee_2 = main_contract.getBankFee(first_id) / 10**18
    coefs = main_contract.getCoeficients(first_id)
    data_ID_2 = main_contract.game(first_id)
    coef_A_2 = coefs[0] / 10**9
    coef_B_2 = coefs[1] / 10**9
    value_2 = main_contract.getTotalAmmount(first_id)
    value_3 = main_contract.getBankDeposit(first_id)
    assert (
        coef_A == coef_A_2
        and coef_B == coef_B_2
        and data_ID == data_ID_2
        and bank_fee == bank_fee_2
        and value_2 == value
        and value_3 == value
        and cap_A == capacities[0]
        and cap_B == capacities[1]
    )
