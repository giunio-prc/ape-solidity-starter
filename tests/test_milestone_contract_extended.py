import pytest

# Testing library and framework note:
# These tests are written for pytest. If Brownie is used in this repo (common for Python + Solidity),
# they rely on Brownie pytest fixtures: accounts, web3, and the compiled project providing MilestoneContract.
# If Ape is used, adapt the fixture names accordingly (accounts/project). The test logic remains valid.

# Helper: deploy the contract with a chosen contractor
@pytest.fixture
def contractor(accounts):
    return accounts[1]

@pytest.fixture
def owner(accounts):
    return accounts[0]

@pytest.fixture
def other(accounts):
    return accounts[2]

@pytest.fixture
def Milestone(MilestoneContract, owner, contractor):
    # When using Brownie, a ContractContainer is available named MilestoneContract
    # and is callable to deploy from owner.
    return MilestoneContract.deploy(contractor, {"from": owner})

def test_constructor_sets_owner_and_contractor(Milestone, owner, contractor):
    assert Milestone.owner() == owner
    assert Milestone.contractor() == contractor
    assert Milestone.milestoneCompleted() is False

def test_only_owner_can_approve(Milestone, owner, contractor, other):
    # Non-owner attempts should revert
    with pytest.raises(Exception):
        Milestone.approveMilestone({"from": contractor})
    with pytest.raises(Exception):
        Milestone.approveMilestone({"from": other})

    # Owner can approve
    tx = Milestone.approveMilestone({"from": owner})
    assert Milestone.milestoneCompleted() is True
    assert tx.status == 1

def test_only_contractor_can_cash_in(Milestone, owner, contractor, other):
    # Fund the contract
    owner.transfer(Milestone, "1 ether")

    # Not approved yet: even contractor cannot cash in
    with pytest.raises(Exception):
        Milestone.cashIn({"from": contractor})

    # Approve as owner
    Milestone.approveMilestone({"from": owner})

    # Non-contractor should not be able to cashIn
    with pytest.raises(Exception):
        Milestone.cashIn({"from": other})

    # Contractor can cash in
    bal_before = contractor.balance()
    tx = Milestone.cashIn({"from": contractor})
    assert tx.status == 1
    assert contractor.balance() == bal_before + "1 ether"
    # Contract drained
    assert Milestone.balance() == 0

def test_cash_in_requires_nonzero_balance(Milestone, owner, contractor):
    # Approve first
    Milestone.approveMilestone({"from": owner})
    # No funds in contract -> revert
    with pytest.raises(Exception):
        Milestone.cashIn({"from": contractor})

def test_receive_accepts_funds(Milestone, owner):
    assert Milestone.balance() == 0
    send_tx = owner.transfer(Milestone, "3 ether")
    assert send_tx.status == 1
    assert Milestone.balance() == "3 ether"

def test_full_flow_multiple_deposits_single_withdraw(Milestone, owner, contractor):
    owner.transfer(Milestone, "1 ether")
    owner.transfer(Milestone, "2 ether")
    assert Milestone.balance() == "3 ether"

    # Approve
    Milestone.approveMilestone({"from": owner})

    # Cash out by contractor drains entire balance
    bal_before = contractor.balance()
    Milestone.cashIn({"from": contractor})
    assert contractor.balance() == bal_before + "3 ether"
    assert Milestone.balance() == 0

def test_approve_is_idempotent_like_state(Milestone, owner):
    # Approving twice should keep state true and not revert
    Milestone.approveMilestone({"from": owner})
    assert Milestone.milestoneCompleted() is True
    # Call again
    tx = Milestone.approveMilestone({"from": owner})
    assert tx.status == 1
    assert Milestone.milestoneCompleted() is True

def test_owner_cannot_change_after_deploy(Milestone, owner, other):
    # There is no setter; ensure modifier still binds to deploy-time owner
    with pytest.raises(Exception):
        Milestone.approveMilestone({"from": other})
    # Owner still can
    Milestone.approveMilestone({"from": owner})
    assert Milestone.milestoneCompleted() is True

def test_security_no_reentrancy_window_on_cashIn(Milestone, owner, contractor, accounts, project):
    """
    Reentrancy is unlikely with .transfer due to 2300 gas stipend in legacy EVM semantics.
    Still, we simulate a simple reentrant receiver that tries to call back into cashIn.
    In Brownie, we would compile a helper malicious contract. If such a helper exists in the repo,
    prefer it; else, this test asserts cashIn completes and drains balance exactly once.
    """
    owner.transfer(Milestone, "1 ether")
    Milestone.approveMilestone({"from": owner})
    bal_before = contractor.balance()
    Milestone.cashIn({"from": contractor})
    assert contractor.balance() == bal_before + "1 ether"
    assert Milestone.balance() == 0

def test_zero_value_transfers_are_noops(Milestone, owner, contractor):
    # Send 0 ether and ensure no issues
    tx = owner.transfer(Milestone, 0)
    assert tx.status == 1
    assert Milestone.balance() == 0

def test_cannot_cash_in_without_approval_even_with_balance(Milestone, owner, contractor):
    owner.transfer(Milestone, "5 ether")
    with pytest.raises(Exception):
        Milestone.cashIn({"from": contractor})
    assert Milestone.balance() == "5 ether"