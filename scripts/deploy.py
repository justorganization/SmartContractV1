from brownie import accounts, config, MainContract, network
import os
from scripts.helpful_functions import *


def deploy_simple_storage():
    account = get_account()
    main_contract = MainContract.deploy({"from": account})
    throwData("sasas", main_contract, account)
    throwData("sasa1s", main_contract, account)
    throwData("sasa2s", main_contract, account)
    first_id = main_contract.getLastGameID()

    bank_fee = random.random()
    coef_A = 10 * random.random()
    coef_B = 10 * random.random()
    data_ID = 10 * random.randint(0, 10)

    if bank_fee > 0.1 or coef_A > 1 or coef_B > 1 or data_ID >= first_id:
        try:
            createGame(bank_fee, coef_A, coef_B, data_ID, main_contract, account)
        except:
            print("error")
    else:
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
    print(bank_fee, coef_A, coef_B, data_ID)


def main():
    print((10 * random.random()).toFixed(9))
