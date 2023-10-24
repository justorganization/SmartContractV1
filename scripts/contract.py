from scripts.helpful_functions import *
from brownie import network, MainContract, exceptions
import pytest
import random
import math


class Contract:
    def __init__(
        self,
        bank_fee,
        account,
        total_amount,
        A_team_coef,
        B_team_coef,
        main_contract,
    ):
        """
        Sets the main characteristics of pool
        :param account: Address of user who create a poll
        :param total_amount: amount of pooled eth by creator
        :param A_team_coef: setted by creator coeficient for team A winning
        :param B_team_coef: setted by creator coeficient for team B winning
        """
        throwData("ss", main_contract, account)
        createGame(
            bank_fee,
            A_team_coef,
            B_team_coef,
            main_contract.getLastDataID() - 1,
            main_contract,
            account,
            total_amount,
        )
        self.account = account
        self.total_amount = total_amount
        self.A_team_coef = A_team_coef
        self.B_team_coef = B_team_coef
        # setting the pool capacity with special formula
        self.A_capacity = self.total_amount / (self.A_team_coef - 1)
        self.B_capacity = self.total_amount / (self.B_team_coef - 1)
        # creating dicts for holding users and their bets
        self.A_dict = {}
        self.B_dict = {}
        self.game_id = main_contract.getLastGameID() - 1
        self.contract = main_contract
        self.A_expectations = {}
        self.B_expectations = {}
        self.Cancel_expectations = {}
        self.bank_fee = bank_fee
        self.is_finished = False
        self.is_canceled = False

    def make_a_bet_for_team_A(self, account, value):
        if value > self.A_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                makeABet(self.game_id, True, self.contract, account, value=value)
        else:
            makeABet(self.game_id, True, self.contract, account, value=value)
            self.A_dict[account] = value
            self.total_amount += value
            self.B_capacity += value / (self.B_team_coef - 1)
            self.A_capacity -= value
            self.A_expectations[account] = (
                value * self.A_team_coef * (1 - self.bank_fee - 0.001)
            )
            self.Cancel_expectations[account] = self.Cancel_expectations.get(
                account, 0
            ) + value * (1 - self.bank_fee - 0.001)

    def make_a_bet_for_team_A(self, account, value):
        if value > self.B_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                makeABet(self.game_id, False, self.contract, account, value=value)
        else:
            makeABet(self.game_id, False, self.contract, account, value=value)
            self.B_dict[account] = value
            self.total_amount += value
            self.A_capacity += value / (self.A_team_coef - 1)
            self.B_capacity -= value
            self.B_expectations[account] = (
                value * self.B_team_coef * (1 - self.bank_fee - 0.001)
            )
            self.Cancel_expectations[account] = self.Cancel_expectations.get(
                account, 0
            ) + value * (1 - self.bank_fee - 0.001)

    def end_game(self, winner_team, is_canceled):
        self.contract.endGame(self.game_id, winner_team, is_canceled)
        self.winner = winner_team
        self.is_canceled = is_canceled

    def end_a_game(self, team_winner):
        if team_winner == "A":
            for i in self.A_dict.keys():
                winning = self.A_dict[i] * self.A_team_coef
                print(self.pay_to_winner(i, winning))
                self.total_amount -= winning

        if team_winner == "B":
            for i in self.B_dict.keys():
                winning = self.B_dict[i] * self.B_team_coef
                print(self.pay_to_winner(i, winning))
                self.total_amount -= winning

        return f"Bank gets {self.total_amount}"


my_bet = Contract("bank", 10, 1.5, 1.7)

print(my_bet.make_a_bet_for_team_A("Sasha", 100))
print(my_bet.make_a_bet_for_team_A("Omer", 4))
print(my_bet.make_a_bet_for_team_B("Yulia", 10))
print(my_bet.make_a_bet_for_team_B("Lew", 7))


print(my_bet.end_a_game("A"))
