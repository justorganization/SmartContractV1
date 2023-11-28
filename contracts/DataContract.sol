// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;
import "./MainLib.sol";

contract DataContract {
    mapping(uint128 => string) public gamesData;
    mapping(uint128 => bool) public dataRelevance;
    mapping(uint128 => uint64[]) public dataToGame;
    mapping(uint64 => bool) public isAWinner;
    mapping(uint64 => bool) public finished;
    mapping(uint64 => bool) public isGameCanceled;
    uint128 public lastDataID;
    address public owner;

    constructor(address _owner) public {
        owner = _owner;
        lastDataID = 0;
    }

    function throwData(string memory data) public onlyOwner {
        gamesData[lastDataID] = data;
        dataRelevance[lastDataID] = true;
        lastDataID = lastDataID + 1;
    }

    function endGames(
        uint128 dataID,
        bool isA,
        bool isCanceled
    ) public onlyOwner {
        dataRelevance[dataID] = false;
        for (uint32 i = 0; i < dataToGame[dataID].length; i++) {
            uint64 gameID = dataToGame[dataID][i];
            finished[gameID] = true;
            isAWinner[gameID] = isA;
            isGameCanceled[gameID] = isCanceled;
        }
    }

    function addDataToGame(uint128 dataID, uint64 gameID) public {
        dataToGame[dataID].push(gameID);
    }

    function getLastDataID() public view returns (uint128) {
        return (lastDataID);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
}
