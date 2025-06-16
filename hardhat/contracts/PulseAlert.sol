// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

interface Verifier {
    function verifyProof(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[1] memory input
    ) external view returns (bool);
}

contract PulseAlert {
    Verifier public verifier;

    constructor(address _verifier) {
        verifier = Verifier(_verifier);
    }

    event AlertVerified(uint256 result);

    function submitProof(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[1] memory input
    ) public {
        require(verifier.verifyProof(a, b, c, input), "Invalid proof");
        emit AlertVerified(input[0]);
    }
}
