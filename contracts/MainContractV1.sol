// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

contract MainContract {
    mapping(uint128 => string) public gamesData;
    mapping(uint64 => uint128) public game;
    mapping(uint64 => address) public bankAddress;
    mapping(uint64 => uint256) public totalAmount;
    mapping(uint64 => uint128) public bankFee;
    mapping(uint64 => uint256) public bankDeposit;
    mapping(uint64 => bool) public finished;
    mapping(uint64 => uint128[2]) public coeficients;
    mapping(uint64 => uint256[2]) public capacities;
    mapping(uint64 => mapping(address => uint256)) public usersA;
    mapping(uint64 => mapping(address => uint256)) public usersB;
    mapping(uint64 => bool) public isAWinner;

    uint256 ownersFee;
    address owner;
    uint64 lastGameID;
    uint128 lastDataID;

    constructor() public {
        owner = msg.sender;
        lastGameID = 0;
        lastDataID = 0;
    }

    function throwData(string memory data) public {
        gamesData[lastDataID] = data;
        lastDataID = lastDataID + 1;
    }

    function whichOwner() public view returns (address) {
        return owner;
    }

    modifier validData(
        uint128 gameFee,
        uint128 coefA,
        uint128 coefB,
        uint128 gameData
    ) {
        require(gameFee < 100000000000000001, "Fee must be less than 10%");
        require(1000000000 < coefA, "Coeficient must be grater than 1");
        require(
            coefA < 1000000000000000000,
            "Coeficient must be less than 1000000000"
        );
        require(1000000000 < coefB, "Coeficient must be grater than 1");
        require(
            coefB < 1000000000000000000,
            "Coeficient must be less than 1000000000"
        );
        require(gameData < lastDataID, "Incorrect data");
        _;
    }

    function createGame(
        uint128 gameFee,
        uint128 coefA,
        uint128 coefB,
        uint128 gameData
    ) public payable validData(gameFee, coefA, coefB, gameData) {
        game[lastGameID] = gameData;
        bankAddress[lastGameID] = msg.sender;
        totalAmount[lastGameID] = msg.value;
        bankFee[lastGameID] = gameFee;
        finished[lastGameID] = false;
        bankDeposit[lastGameID] = msg.value;
        coeficients[lastGameID] = [coefA, coefB];
        capacities[lastGameID] = [
            (msg.value / (coefA - 10 ** 9)) * 10 ** 9,
            (msg.value / (coefB - 10 ** 9)) * 10 ** 9
        ];
        lastGameID = lastGameID + 1;
    }

    function makeABet(
        uint64 gameID,
        bool isA
    ) public payable onlyGameNotFinished(gameID) {
        if (isA) {
            require(msg.value < capacities[gameID][0]);
        } else {
            require(msg.value < capacities[gameID][1]);
        }
        totalAmount[gameID] = totalAmount[gameID] + msg.value;
        if (isA) {
            capacities[gameID] = [
                capacities[gameID][0] - (msg.value * (10 ** 18)),
                (totalAmount[gameID] / (coeficients[gameID][1] - 10 ** 9)) *
                    10 ** 9
            ];
            usersA[gameID][msg.sender] = msg.value;
        } else {
            capacities[gameID] = [
                (totalAmount[gameID] / (coeficients[gameID][0] - 10 ** 9)) *
                    10 ** 9,
                capacities[gameID][1] - (msg.value * (10 ** 18))
            ];
            usersA[gameID][msg.sender] = msg.value;
        }
    }

    modifier onlyGameFinished(uint64 gameID) {
        require(finished[gameID], "Game is not finished");
        _;
    }
    modifier onlyGameNotFinished(uint64 gameID) {
        require(!finished[gameID], "Game is finished");
        _;
    }

    function endGame(uint64 gameID, bool isA) public {
        finished[gameID] = true;
        isAWinner[gameID] = isA;
    }

    function keyExists(
        uint64 gameID,
        address key,
        bool isA
    ) public view returns (bool) {
        if (isA) {
            return usersA[gameID][key] != 0;
        } else {
            return usersB[gameID][key] != 0;
        }
    }

    function claimeWinnings(
        uint64 gameID
    ) public payable onlyGameFinished(gameID) {
        require(keyExists(gameID, msg.sender, isAWinner[gameID]));
        if (isAWinner[gameID]) {
            address payable winner = payable(msg.sender);
            winner.transfer(
                (usersA[gameID][msg.sender] * coeficients[gameID][0]) / 10 ** 9
            );
        } else {
            address payable winner = payable(msg.sender);
            winner.transfer(
                (usersB[gameID][msg.sender] * coeficients[gameID][1]) / 10 ** 9
            );
        }
    }

    //getters
    function getOwner() public view returns (address) {
        return owner;
    }

    function getLastGameID() public view returns (uint64) {
        return lastGameID;
    }

    function getLastDataID() public view returns (uint128) {
        return lastDataID;
    }

    function getGamesData(uint64 gameID) public view returns (string memory) {
        return gamesData[gameID];
    }

    function getGameData(uint64 gameID) public view returns (uint128) {
        return game[gameID];
    }

    function getBankAddress(uint64 gameID) public view returns (address) {
        return bankAddress[gameID];
    }

    function getTotalAmmount(uint64 gameID) public view returns (uint256) {
        return totalAmount[gameID];
    }

    function getBankFee(uint64 gameID) public view returns (uint128) {
        return bankFee[gameID];
    }

    function getBankDeposit(uint64 gameID) public view returns (uint256) {
        return bankDeposit[gameID];
    }

    function getIsGameFinished(uint64 gameID) public view returns (bool) {
        return finished[gameID];
    }

    function getCoeficients(
        uint64 gameID
    ) public view returns (uint128[2] memory) {
        return coeficients[gameID];
    }

    function getCapacities(
        uint64 gameID
    ) public view returns (uint256[2] memory) {
        return capacities[gameID];
    }

    function getDeposit(
        uint64 gameID,
        address user,
        bool isA
    ) public view returns (uint256) {
        if (isA) {
            return usersA[gameID][user];
        } else {
            return usersB[gameID][user];
        }
    }

    function getIsAWinner(uint64 gameID) public view returns (bool) {
        return isAWinner[gameID];
    }
}
