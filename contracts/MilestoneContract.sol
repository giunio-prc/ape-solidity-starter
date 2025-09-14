// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;


contract MilestoneContract {
    address payable public contractor;
    address public owner;
    bool public milestoneCompleted;

    constructor(address payable _contractor) {
        owner = msg.sender;
        contractor = _contractor;
        milestoneCompleted = false;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function.");
        _;
    }

    modifier onlyContractor() {
        require(msg.sender == contractor, "Only the contractor can call this function.");
        _;
    }

    function approveMilestone() external onlyOwner() {
        milestoneCompleted = true;
    }

    function cashIn() external onlyContractor() {
        require(milestoneCompleted, "Milestone has not been approved yet.");
        require(address(this).balance > 0, "No funds available for withdrawal.");
        contractor.transfer(address(this).balance);
    }

    // Fallback function to receive payments
    receive() external payable {}

}
