import pytest


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def user(accounts):
    return accounts[1]


@pytest.fixture
def hello_world_contract(project, owner):
    return owner.deploy(project.HelloWorld)


def test_greet(hello_world_contract):
    """Test that contract deploys with correct initial greet"""
    assert hello_world_contract.greet() == "Hello, World!"
