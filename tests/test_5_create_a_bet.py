from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_prepare(account, main_contract):
    createGame(0.03, 1.8, 2.3, 0, main_contract, account, 10**19)


def test_create_a_bet_1(account, main_contract):
    first_id = main_contract.getLastGameID() - 1
    makeABet(first_id, True, main_contract, account)


def test_create_a_bet_2(account, main_contract):
    first_id = main_contract.getLastGameID() - 1
    makeABet(first_id, True, main_contract, account)
    assert main_contract.getDeposit(first_id, account, True) == 10**9


def test_create_a_bet_3(account, main_contract):
    first_id = main_contract.getLastGameID() - 1
    total_amount_1 = main_contract.getTotalAmmount(first_id)
    makeABet(first_id, True, main_contract, account)
    total_amount_2 = main_contract.getTotalAmmount(first_id)
    assert total_amount_1 + 10**9 == total_amount_2
