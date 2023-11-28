from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions, Contract, DataContract
import pytest
import random


def test_throwing_data_1(account, main_contract):
    data = "Some information about the game"
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    first_id = data_contract.getLastDataID({"from": account})
    data_contract.throwData(data, {"from": account})
    second_id = data_contract.getLastDataID({"from": account})
    assert data_contract.gamesData(first_id) == data and first_id == second_id - 1


def test_throwing_data_2(account, main_contract):
    first_string = generate_random_string()
    second_sctring = generate_random_string()
    third_string = generate_random_string()
    dataContract = main_contract.dataContract()
    data_contract = Contract.from_abi("DataContract", dataContract, DataContract.abi)
    data_contract.throwData(first_string, {"from": account})
    data_contract.throwData(second_sctring, {"from": account})
    data_contract.throwData(third_string, {"from": account})
    assert (
        data_contract.gamesData(1) == first_string
        and data_contract.gamesData(2) == second_sctring
        and data_contract.gamesData(3) == third_string
    )
