from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


def test_finishing_game(account, main_contract):
    gameID = main_contract.getLastGameID() - 1
    main_contract.endGame(gameID, True)
    with pytest.raises(exceptions.VirtualMachineError):
        makeABet(gameID, True, main_contract, account, 10**15)
