// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0 <0.9.0;

library MainLib {
    function calculateCapacities(
        uint256 value,
        uint128 coefA,
        uint128 coefB
    ) external pure returns (uint256[2] memory) {
        uint256 capA = (value / (coefA - 10 ** 9)) * 10 ** 9;
        uint256 capB = (value / (coefB - 10 ** 9)) * 10 ** 9;
        return [capA, capB];
    }

    function calculateAddLCapacities(
        uint256 value,
        uint128 coefA,
        uint128 coefB,
        uint256 capacitieA,
        uint256 capacitieB
    ) external pure returns (uint256[2] memory) {
        uint256 capA = capacitieA + (value / (coefA - 10 ** 9)) * 10 ** 9;
        uint256 capB = capacitieB + (value / (coefB - 10 ** 9)) * 10 ** 9;
        return [capA, capB];
    }

    function calculateMakeBetCapacities(
        uint256 value,
        uint128 coefA,
        uint128 coefB,
        uint256 capacitieA,
        uint256 capacitieB,
        bool isA
    ) external pure returns (uint256[2] memory) {
        uint256 capA;
        uint256 capB;
        if (isA) {
            capA = capacitieA - value;
            capB = capacitieB + ((value / (coefB - 10 ** 9)) * 10 ** 9);
        } else {
            capA = capacitieA + ((value / (coefA - 10 ** 9)) * 10 ** 9);
            capB = capacitieB - value;
        }
        return [capA, capB];
    }
}
