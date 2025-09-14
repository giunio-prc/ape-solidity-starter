import pytest
import ape
from ape import reverts


@pytest.fixture
def client(accounts):
    return accounts[0]


@pytest.fixture
def contractor(accounts):
    return accounts[1]


@pytest.fixture
def other_user(accounts):
    return accounts[2]


@pytest.fixture
def milestone_contract(project, client, contractor):
    return client.deploy(project.MilestoneContract, contractor.address)


def test_contract_deployment(milestone_contract, client, contractor):
    """Test that contract deploys with correct initial state"""
    assert milestone_contract.owner() == client.address
    assert milestone_contract.contractor() == contractor.address
    assert not milestone_contract.milestoneCompleted()


def test_receive_payment(milestone_contract, client):
    """Test that contract can receive ETH payments"""
    initial_balance = milestone_contract.balance
    payment_amount = "1 ether"

    client.transfer(milestone_contract.address, payment_amount)

    assert milestone_contract.balance == initial_balance + ape.convert(
        payment_amount, int
    )


def test_approve_milestone_by_client(milestone_contract, client):
    """Test that client can approve milestone"""
    milestone_contract.approveMilestone(sender=client)
    assert milestone_contract.milestoneCompleted()


def test_approve_milestone_by_non_client_fails(
    milestone_contract, contractor, other_user
):
    """Test that non-client cannot approve milestone"""
    with reverts("Only the owner can call this function."):
        milestone_contract.approveMilestone(sender=contractor)

    with reverts("Only the owner can call this function."):
        milestone_contract.approveMilestone(sender=other_user)


def test_cash_in_success(milestone_contract, client, contractor):
    """Test successful cash in after milestone approval"""
    # Fund the contract
    payment_amount = "2 ether"
    client.transfer(milestone_contract.address, payment_amount)

    # Approve milestone
    milestone_contract.approveMilestone(sender=client)

    # Record contractor balance before cash in
    contractor_balance_before = contractor.balance

    # Cash in
    receipt = milestone_contract.cashIn(sender=contractor)
    gas_used = receipt.gas_used * receipt.gas_price

    # Verify funds transferred (account for gas costs)
    assert milestone_contract.balance == 0
    expected_balance = (
        contractor_balance_before + ape.convert(payment_amount, int) - gas_used
    )
    assert contractor.balance == expected_balance


def test_cash_in_fails_without_approval(milestone_contract, client, contractor):
    """Test that cash in fails if milestone not approved"""
    # Fund the contract
    client.transfer(milestone_contract.address, "1 ether")

    # Try to cash in without approval
    with reverts("Milestone has not been approved yet."):
        milestone_contract.cashIn(sender=contractor)


def test_cash_in_fails_with_no_funds(milestone_contract, client, contractor):
    """Test that cash in fails if no funds available"""
    # Approve milestone but don't fund contract
    milestone_contract.approveMilestone(sender=client)

    # Try to cash in with no funds
    with reverts("No funds available for withdrawal."):
        milestone_contract.cashIn(sender=contractor)


def test_cash_in_by_non_contractor_fails(milestone_contract, client, other_user):
    """Test that non-contractor cannot cash in"""
    # Fund and approve
    client.transfer(milestone_contract.address, "1 ether")
    milestone_contract.approveMilestone(sender=client)

    # Try to cash in as non-contractor
    with reverts("Only the contractor can call this function."):
        milestone_contract.cashIn(sender=client)

    with reverts("Only the contractor can call this function."):
        milestone_contract.cashIn(sender=other_user)


def test_multiple_payments_before_approval(milestone_contract, client, contractor):
    """Test that multiple payments accumulate before milestone approval"""
    # Make multiple payments
    client.transfer(milestone_contract.address, "1 ether")
    client.transfer(milestone_contract.address, "0.5 ether")
    client.transfer(milestone_contract.address, "0.3 ether")

    expected_total = ape.convert("1.8 ether", int)
    assert milestone_contract.balance == expected_total

    # Approve and cash in
    milestone_contract.approveMilestone(sender=client)
    contractor_balance_before = contractor.balance

    receipt = milestone_contract.cashIn(sender=contractor)
    gas_used = receipt.gas_used * receipt.gas_price

    expected_final_balance = contractor_balance_before + expected_total - gas_used
    assert contractor.balance == expected_final_balance


def test_milestone_cannot_be_unapproved(milestone_contract, client):
    """Test that milestone approval is permanent (no rollback function)"""
    # Approve milestone
    milestone_contract.approveMilestone(sender=client)
    assert milestone_contract.milestoneCompleted()

    # Contract has no function to unapprove milestone
    # This test documents the intended behavior
