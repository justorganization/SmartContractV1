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
        data,
    ):
        """
        Sets the main characteristics of pool
        :param account: Address of user who create a poll
        :param total_amount: amount of pooled eth by creator
        :param A_team_coef: setted by creator coeficient for team A winning
        :param B_team_coef: setted by creator coeficient for team B winning
        """
        createGame(
            bank_fee,
            A_team_coef,
            B_team_coef,
            data,
            main_contract,
            account,
            total_amount,
        )
        self.bank_account = account
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
        self.game_data = data

    def add_game_liquidity(self, account, value):
        if self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                addGameLiquidity(self.game_id, self.contract, account, value)
        elif account == self.bank_account:
            addGameLiquidity(self.game_id, self.contract, account, value)
            self.total_amount += value
            self.A_capacity = self.total_amount / (self.A_team_coef - 1)
            self.B_capacity = self.total_amount / (self.B_team_coef - 1)
        else:
            with pytest.raises(exceptions.VirtualMachineError):
                addGameLiquidity(self.game_id, self.contract, account, value)

    def make_a_bet_for_team_A(self, account, value):
        if value > self.A_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                makeABet(self.game_id, True, self.contract, account, value=value)
        elif self.is_finished:
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

    def make_a_bet_for_team_B(self, account, value):
        if value > self.B_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                makeABet(self.game_id, False, self.contract, account, value=value)
        elif self.is_finished:
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

    def add_liquidity_to_bet_A(self, account, value):
        if value > self.A_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                addBetLiquidity(self.game_id, True, self.contract, account, value=value)
        elif self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                addBetLiquidity(self.game_id, True, self.contract, account, value=value)
        else:
            addBetLiquidity(self.game_id, True, self.contract, account, value=value)
            self.A_dict[account] += value
            self.total_amount += value
            self.B_capacity += value / (self.B_team_coef - 1)
            self.A_capacity -= value
            self.A_expectations[account] += (
                value * self.A_team_coef * (1 - self.bank_fee - 0.001)
            )
            self.Cancel_expectations[account] += value * (1 - self.bank_fee - 0.001)

    def add_liquidity_to_bet_B(self, account, value):
        if value > self.B_capacity:
            with pytest.raises(exceptions.VirtualMachineError):
                addBetLiquidity(
                    self.game_id, False, self.contract, account, value=value
                )
        elif self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                addBetLiquidity(
                    self.game_id, False, self.contract, account, value=value
                )
        else:
            addBetLiquidity(self.game_id, False, self.contract, account, value=value)
            self.B_dict[account] += value
            self.total_amount += value
            self.A_capacity += value / (self.A_team_coef - 1)
            self.B_capacity -= value
            self.B_expectations[account] += (
                value * self.B_team_coef * (1 - self.bank_fee - 0.001)
            )
            self.Cancel_expectations[account] += value * (1 - self.bank_fee - 0.001)

    def end_game(self, winner_team, is_canceled):
        self.contract.endGame(self.game_id, winner_team, is_canceled)
        self.winner = winner_team
        self.is_canceled = is_canceled
        self.is_finished = True
        self.creator_expactation = self.total_amount / 1000
        if not is_canceled:
            self.bank_expectation = self.total_amount
            if winner_team:
                for i in self.A_expectations.keys():
                    if self.A_dict[i] != 0:
                        self.bank_expectation -= self.A_expectations[i]
            else:
                for i in self.B_expectations.keys():
                    if self.B_dict[i] != 0:
                        self.bank_expectation -= self.B_expectations[i]

    def claim_winnings(self, account):
        if not self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                claimWinnings(self.game_id, self.contract, account)
        elif self.is_canceled:
            with pytest.raises(exceptions.VirtualMachineError):
                claimWinnings(self.game_id, self.contract, account)
        else:
            if self.winner:
                if self.A_dict[account] != 0:
                    claimWinnings(self.game_id, self.contract, account)
                    self.A_dict[account] = 0
                else:
                    with pytest.raises(exceptions.VirtualMachineError):
                        claimWinnings(self.game_id, self.contract, account)
            else:
                if self.B_dict[account] != 0:
                    claimWinnings(self.game_id, self.contract, account)
                    self.B_dict[account] = 0
                else:
                    with pytest.raises(exceptions.VirtualMachineError):
                        claimWinnings(self.game_id, self.contract, account)

    def close_game(self, account):
        if not self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeGame(self.game_id, {"from": account})
        elif self.is_canceled:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeGame(self.game_id, {"from": account})
        elif self.bank_account != account:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeGame(self.game_id, {"from": account})
        else:
            self.contract.closeGame(self.game_id, {"from": account})
            if self.winner:
                for acc in self.A_dict.keys():
                    if self.A_dict[acc] != 0:
                        self.A_dict[acc] = 0
                    else:
                        with pytest.raises(exceptions.VirtualMachineError):
                            claimWinnings(self.game_id, self.contract, acc)
            else:
                for acc in self.B_dict.keys():
                    if self.B_dict[acc] != 0:
                        self.B_dict[acc] = 0
                    else:
                        with pytest.raises(exceptions.VirtualMachineError):
                            claimWinnings(self.game_id, self.contract, acc)

    def claim_bet(self, account):
        if not self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                claimBet(self.game_id, self.contract, account)
        elif not self.is_canceled:
            with pytest.raises(exceptions.VirtualMachineError):
                claimBet(self.game_id, self.contract, account)
        else:
            claimBet(self.game_id, self.contract, account)
            self.A_dict[account] = 0
            self.B_dict[account] = 0

    def close_canceled_game(self, account):
        if not self.is_finished:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeCanceledGame(self.game_id, {"from": account})
        elif not self.is_canceled:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeCanceledGame(self.game_id, {"from": account})
        elif self.bank_account != account:
            with pytest.raises(exceptions.VirtualMachineError):
                self.contract.closeCanceledGame(self.game_id, {"from": account})
        else:
            self.contract.closeCanceledGame(self.game_id, {"from": account})

            for i in self.A_dict.keys():
                self.A_dict[i] = 0
            for i in self.B_dict.keys():
                self.B_dict[i] = 0
