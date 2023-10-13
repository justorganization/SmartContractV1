from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random


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
