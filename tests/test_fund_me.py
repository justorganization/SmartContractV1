from scripts.helpful_functions import *
from brownie import network, MainContract


def test_deploy():
    account = get_account()
    main_contract = deploy_contract()
    assert account == main_contract.whichOwner()


def test_throwing_data():
    account = get_account()
    main_contract = deploy_contract()
    data = "Some information about the game"
    first_id = main_contract.getLastDataID()
    main_contract.throwData(data, {"from": account})
    second_id = main_contract.getLastDataID()
    assert main_contract.getGamesData(first_id) == data and first_id == second_id - 1
