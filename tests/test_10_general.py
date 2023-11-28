from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


# def test_general(main_contract):
#    throwData("Some data", main_contract, accounts[0])
#    accounts_initial_balances = []
#    for i in range(11):
#        accounts_initial_balances.append(accounts[i].balance())
