from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_general(main_contract):
    koeficient_A = (int((random.random() * random.randint(1, 100)) * 100000)) / 100000
