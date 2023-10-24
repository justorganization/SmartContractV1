from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_general(main_contract):
    koeficient_A = (int((random.random() * random.randint(1, 100)) * 100000)) / 100000
    koeficient_B = (int((random.random() * random.randint(1, 100)) * 100000)) / 100000
    bank_fee = int((random.random() * 10000)) / 100000
    bank_deposit = (random.random() * random.randint(1, 100)) * 10 ** random.randint(
        17, 19
    )
    bank_initial_balance = accounts[0].balance()
    accounts_initial_balances = []
    for i in range(11):
        accounts_initial_balances.append(accounts[i].balance())
