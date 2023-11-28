// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;
import "./MainLib.sol";
import "./DataContract.sol";

contract MainContract {
    mapping(uint64 => uint128) public game;
    mapping(uint64 => address) public bankAddress;
    mapping(uint64 => uint256) public totalAmount;
    mapping(uint64 => uint128) public bankFee;
    mapping(uint64 => uint256) public bankDeposit;
    mapping(uint64 => uint128[2]) public coeficients;
    mapping(uint64 => uint256[2]) public capacities;
    mapping(uint64 => mapping(address => uint256)) public usersA;
    mapping(uint64 => mapping(address => uint256)) public usersB;
    mapping(uint64 => address[]) usersAlist;
    mapping(uint64 => address[]) usersBlist;
    mapping(uint64 => bool) raised;

    mapping(uint64 => uint256) ownersRaise;
    uint256 ownersFee = 1000000000000000;
    uint256 ownersPool;
    address owner;
    uint64 lastGameID;
    DataContract public dataContract;

    constructor() public {
        owner = msg.sender;
        lastGameID = 0;
        dataContract = new DataContract(owner);
    }

    function createGame(
        uint128 gameFee,
        uint128 coefA,
        uint128 coefB,
        uint128 gameData
    ) public payable validData(gameFee, coefA, coefB, gameData) {
        require(dataContract.dataRelevance(gameData));
        game[lastGameID] = gameData;
        bankAddress[lastGameID] = msg.sender;
        totalAmount[lastGameID] = msg.value;
        bankFee[lastGameID] = gameFee;
        bankDeposit[lastGameID] = msg.value;
        coeficients[lastGameID] = [coefA, coefB];
        capacities[lastGameID] = MainLib.calculateCapacities(
            msg.value,
            coefA,
            coefB
        );
        dataContract.addDataToGame(gameData, lastGameID);
        raised[lastGameID] = false;
        lastGameID = lastGameID + 1;
    }

    function addGameLiquidity(
        uint64 gameID
    ) public payable onlyGameNotFinished(gameID) onlyBank(gameID) {
        totalAmount[gameID] = totalAmount[gameID] + msg.value;

        capacities[gameID] = MainLib.calculateAddLCapacities(
            msg.value,
            coeficients[gameID][0],
            coeficients[gameID][1],
            capacities[gameID][0],
            capacities[gameID][1]
        );
        bankDeposit[gameID] += msg.value;
    }

    function makeABet(
        uint64 gameID,
        bool isA
    ) public payable onlyGameNotFinished(gameID) hasntBet(gameID, isA) {
        if (isA) {
            require(msg.value < capacities[gameID][0]);
        } else {
            require(msg.value < capacities[gameID][1]);
        }

        totalAmount[gameID] += msg.value;
        if (isA) {
            usersA[gameID][msg.sender] = msg.value;
            usersAlist[gameID].push(msg.sender);
        } else {
            usersB[gameID][msg.sender] = msg.value;
            usersBlist[gameID].push(msg.sender);
        }
        capacities[gameID] = MainLib.calculateMakeBetCapacities(
            msg.value,
            coeficients[gameID][0],
            coeficients[gameID][1],
            capacities[gameID][0],
            capacities[gameID][1],
            isA
        );
    }

    function addLiquidityToBet(
        uint64 gameID,
        bool isA
    ) public payable onlyGameNotFinished(gameID) {
        if (isA) {
            require(msg.value < capacities[gameID][0]);
            require(usersA[gameID][msg.sender] != 0);
            usersA[gameID][msg.sender] += msg.value;
        } else {
            require(msg.value < capacities[gameID][1]);
            require(usersB[gameID][msg.sender] != 0);
            usersB[gameID][msg.sender] += msg.value;
        }
        capacities[gameID] = MainLib.calculateMakeBetCapacities(
            msg.value,
            coeficients[gameID][0],
            coeficients[gameID][1],
            capacities[gameID][0],
            capacities[gameID][1],
            isA
        );
        totalAmount[gameID] += msg.value;
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

    function claimWinnings(
        uint64 gameID
    ) public onlyGameFinished(gameID) gameNotCanceled(gameID) {
        require(keyExists(gameID, msg.sender, dataContract.isAWinner(gameID)));
        if (!raised[gameID]) {
            ownersRaise[gameID] = totalAmount[gameID] / 1000;
            raised[gameID] = true;
        }
        uint256 winning;
        if (dataContract.isAWinner(gameID)) {
            address payable winner = payable(msg.sender);
            winning =
                (((usersA[gameID][msg.sender] * coeficients[gameID][0]) /
                    10 ** 9) * (10 ** 18 - bankFee[gameID] - ownersFee)) /
                10 ** 18;
            totalAmount[gameID] -= winning;
            winner.transfer(winning);
            usersA[gameID][msg.sender] = 0;
        } else {
            address payable winner = payable(msg.sender);
            winning =
                (((usersB[gameID][msg.sender] * coeficients[gameID][1]) /
                    10 ** 9) * (10 ** 18 - bankFee[gameID] - ownersFee)) /
                10 ** 18;
            totalAmount[gameID] -= winning;
            winner.transfer(winning);
            usersB[gameID][msg.sender] = 0;
        }
    }

    function claimBet(
        uint64 gameID
    ) public onlyGameFinished(gameID) gameCanceled(gameID) {
        if (!raised[gameID]) {
            ownersRaise[gameID] = totalAmount[gameID] / 1000;
            raised[gameID] = true;
        }
        address payable winner = payable(msg.sender);
        if (usersA[gameID][msg.sender] != 0) {
            uint256 bet = (usersA[gameID][msg.sender] *
                (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
            totalAmount[gameID] -= bet;
            winner.transfer(bet);
            usersA[gameID][msg.sender] = 0;
        }
        if (usersB[gameID][msg.sender] != 0) {
            uint256 bet = (usersB[gameID][msg.sender] *
                (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
            totalAmount[gameID] -= bet;
            winner.transfer(bet);
            usersB[gameID][msg.sender] = 0;
        }
    }

    function closeCanceledGame(
        uint64 gameID
    ) public onlyGameFinished(gameID) onlyBank(gameID) gameCanceled(gameID) {
        if (!raised[gameID]) {
            ownersRaise[gameID] = totalAmount[gameID] / 1000;
            raised[gameID] = true;
        }

        for (uint32 i = 0; i < usersAlist[gameID].length; i++) {
            if (usersA[gameID][usersAlist[gameID][i]] != 0) {
                address payable winner = payable(usersAlist[gameID][i]);
                uint256 winning = (usersA[gameID][winner] *
                    (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
                winner.transfer(winning);
                totalAmount[gameID] -= winning;
                usersA[gameID][usersAlist[gameID][i]] = 0;
            }
        }
        for (uint32 i = 0; i < usersBlist[gameID].length; i++) {
            if (usersB[gameID][usersBlist[gameID][i]] != 0) {
                address payable winner = payable(usersBlist[gameID][i]);
                uint256 winning = (usersB[gameID][winner] *
                    (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
                winner.transfer(winning);
                totalAmount[gameID] -= winning;
                usersB[gameID][usersBlist[gameID][i]] = 0;
            }
        }
        address payable bank = payable(msg.sender);
        uint256 bankIncome = totalAmount[gameID] - ownersRaise[gameID];
        bank.transfer(bankIncome);
        totalAmount[gameID] -= bankIncome;
        ownersPool += totalAmount[gameID];
    }

    function closeGame(
        uint64 gameID
    ) public onlyGameFinished(gameID) onlyBank(gameID) gameNotCanceled(gameID) {
        if (!raised[gameID]) {
            ownersRaise[gameID] = totalAmount[gameID] / 1000;
            raised[gameID] = true;
        }
        if (dataContract.isAWinner(gameID)) {
            for (uint32 i = 0; i < usersAlist[gameID].length; i++) {
                if (usersA[gameID][usersAlist[gameID][i]] != 0) {
                    address payable winner = payable(usersAlist[gameID][i]);
                    uint256 winning = (((usersA[gameID][winner] *
                        coeficients[gameID][0]) / 10 ** 9) *
                        (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
                    winner.transfer(winning);
                    totalAmount[gameID] -= winning;
                    usersA[gameID][usersAlist[gameID][i]] = 0;
                }
            }
        } else {
            for (uint32 i = 0; i < usersBlist[gameID].length; i++) {
                if (usersB[gameID][usersBlist[gameID][i]] != 0) {
                    address payable winner = payable(usersBlist[gameID][i]);
                    uint256 winning = (((usersB[gameID][winner] *
                        coeficients[gameID][1]) / 10 ** 9) *
                        (10 ** 18 - bankFee[gameID] - ownersFee)) / 10 ** 18;
                    winner.transfer(winning);
                    totalAmount[gameID] -= winning;
                    usersB[gameID][usersBlist[gameID][i]] = 0;
                }
            }
        }
        address payable bank = payable(msg.sender);
        uint256 bankIncome = totalAmount[gameID] - ownersRaise[gameID];
        bank.transfer(bankIncome);
        totalAmount[gameID] -= bankIncome;
        ownersPool += totalAmount[gameID];
    }

    function withdrawOwnersFees() public payable onlyOwner {
        payable(owner).transfer(ownersPool);
    }

    // modifiers

    modifier hasntBet(uint64 gameID, bool isA) {
        if (isA) {
            require(usersA[gameID][msg.sender] == 0);
        } else {
            require(usersB[gameID][msg.sender] == 0);
        }
        _;
    }

    modifier onlyGameFinished(uint64 gameID) {
        require(dataContract.finished(gameID), "Game is not finished");
        _;
    }
    modifier onlyGameNotFinished(uint64 gameID) {
        require(!dataContract.finished(gameID), "Game is finished");
        _;
    }

    modifier onlyBank(uint64 gameID) {
        require(bankAddress[gameID] == msg.sender);
        _;
    }

    modifier gameNotCanceled(uint64 gameID) {
        require(!dataContract.isGameCanceled(gameID));
        _;
    }
    modifier gameCanceled(uint64 gameID) {
        require(dataContract.isGameCanceled(gameID));
        _;
    }
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
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
        require(gameData < dataContract.lastDataID(), "Incorrect data");
        require(dataContract.dataRelevance(gameData));
        _;
    }

    //getters
    function getOwner() public view returns (address) {
        return owner;
    }

    function getLastGameID() public view returns (uint64) {
        return lastGameID;
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

    function getUsersAlist(
        uint64 gameID
    ) public view returns (address[] memory) {
        return usersAlist[gameID];
    }

    function getUsersBlist(
        uint64 gameID
    ) public view returns (address[] memory) {
        return usersBlist[gameID];
    }

    function getDataCAddress() public view returns (address) {
        return (address(dataContract));
    }

    function getGamesData(uint64 gameID) public view returns (uint128) {
        return (game[gameID]);
    }
}
