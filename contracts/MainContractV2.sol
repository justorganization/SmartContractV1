// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

contract MainContract {
    mapping(uint128 => string) public gamesData;
    mapping(uint64 => uint128) public game;
    mapping(uint64 => address) public bankAddress;
    mapping(uint64 => uint256) public totalAmount;
    mapping(uint64 => uint256) public bankFee;
    mapping(uint64 => uint256) public bankDeposit;
    mapping(uint64 => bool) public finished;
    mapping(uint64 => uint256[2]) public coeficients;
    mapping(uint64 => uint256[2]) public capacities;
    mapping(uint64 => mapping(address => uint256)) public usersA;
    mapping(uint64 => mapping(address => uint256)) public usersB;

    uint256 ownersFee;
    address owner;
    uint64 lastGameID;

    constructor() public {
        owner = msg.sender;
        lastGameID = 0;
    }

    function whichOwner() public view returns (address) {
        return owner;
    }

    function createGame(
        uint256 gameFee,
        uint256 coefA,
        uint256 coefB,
        uint128 gameData
    ) public payable {
        game[lastGameID] = gameData;
        bankAddress[lastGameID] = msg.sender;
        totalAmount[lastGameID] = msg.value;
        bankFee[lastGameID] = gameFee;
        finished[lastGameID] = false;
        bankDeposit[lastGameID] = msg.value;
        coeficients[lastGameID] = [coefA, coefB];
        capacities[lastGameID] = [
            msg.value / ((coefA - 10 ** 9)),
            msg.value / ((coefB - 10 ** 9))
        ];
    }

    function makeABet(
        uint64 gameID,
        uint256 bettedAmount,
        bool isA
    ) public payable {
        if (isA) {
            require(msg.value < capacities[gameID][0]);
        } else {
            require(msg.value < capacities[gameID][1]);
        }
        totalAmount[gameID] = totalAmount[gameID] + bettedAmount;
        if (isA) {
            capacities[gameID] = [
                capacities[gameID][0] - (msg.value * (10 ** 18)),
                totalAmount[gameID] /
                    ((coeficients[gameID][1] - 10 ** 9) / 10 ** 9)
            ];
            usersA[gameID][msg.sender] = msg.value;
        } else {
            capacities[gameID] = [
                totalAmount[gameID] /
                    ((coeficients[gameID][0] - 10 ** 9) / 10 ** 9),
                capacities[gameID][1] - (msg.value * (10 ** 18))
            ];
            usersA[gameID][msg.sender] = msg.value;
        }
    }

    function endGame(uint64 gameId) public {
        finished[gameId] = true;
    }
}
