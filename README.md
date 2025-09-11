# Ape Solidity Starter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Linter and Format check](https://github.com/giunio-prc/ape-solidity-starter/actions/workflows/linter-check.yaml/badge.svg)](https://github.com/giunio-prc/ape-solidity-starter/actions/workflows/linter-check.yaml)
[![Python Unit Tests](https://github.com/giunio-prc/ape-solidity-starter/actions/workflows/pytest-run.yaml/badge.svg)](https://github.com/giunio-prc/ape-solidity-starter/actions/workflows/pytest-run.yaml)

A modern Solidity development environment using the [Ape Framework](https://github.com/ApeWorX/ape) with Python tooling for smart contract development, testing, and deployment.

## Features

- **Ape Framework**: Python-based smart contract development framework
- **Solidity 0.8.30**: Latest Solidity version with modern features
- **Python Testing**: Comprehensive testing with pytest and Ape fixtures
- **Code Quality**: Pre-commit hooks with Ruff formatting and type checking
- **CI/CD**: GitHub Actions for automated testing and linting
- **Modern Tooling**: UV for fast Python package management

## Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (Python package manager)
- Node.js (for any additional tooling)

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
uv sync
```

### 2. Compile Contracts

```bash
uv run ape compile
```

### 3. Run Tests

```bash
# Run tests on default network
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_HelloWord.py::test_greet
```

## Project Structure

```
├── contracts/           # Solidity smart contracts
│   └── HelloWorld.sol  # Example contract
├── tests/              # Python test files
│   └── test_HelloWord.py
├── .github/            # GitHub Actions workflows
│   └── workflows/
├── ape-config.yaml     # Ape framework configuration
├── pyproject.toml      # Python project configuration
└── README.md
```

## Development

### Code Formatting and Linting

```bash
# Format Python code
uv run ruff format

# Lint Python code
uv run ruff check --fix

# Type check Python code
uv run ty check
```

### Pre-commit Hooks

Install pre-commit hooks to automatically format and check code:

```bash
uv run pre-commit install
```

Run all hooks manually
```bash
uv run pre-commit run --all-files
```

### Testing

The project uses pytest with Ape's testing framework:

```python
# Example test structure
@pytest.fixture
def owner(accounts):
    return accounts[0]

@pytest.fixture
def hello_world_contract(project, owner):
    return owner.deploy(project.HelloWorld)

def test_greet(hello_world_contract):
    assert hello_world_contract.greet() == "Hello, World!"
```

## Configuration

### Ape Configuration (`ape-config.yaml`)

- **Solidity Version**: 0.8.30
- **Output Extras**: ABI files generated
- **Network Support**: Local development networks

### Python Configuration (`pyproject.toml`)

- **Dependencies**: ape-solidity for Solidity compilation
- **Dev Tools**: ruff (linting/formatting), ty (type checking), pre-commit
- **Python Version**: 3.12+

## CI/CD

The project includes GitHub Actions workflows:

- **Linter Check**: Runs ruff formatting and type checking
- **Unit Tests**: Executes pytest test suite
- **Multi-version Testing**: Tests against Python 3.12 and 3.13

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Resources

- [Ape Documentation](https://docs.apeworx.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Pytest Documentation](https://docs.pytest.org/)
