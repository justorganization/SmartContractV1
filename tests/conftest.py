from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random


@pytest.fixture
def account(scope="module"):
    return get_account()


@pytest.fixture(scope="package")
def main_contract():
    return deploy_contract()
