from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random


def test_deploy(account, main_contract):
    assert account == main_contract.whichOwner()
