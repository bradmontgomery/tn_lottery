"""Shared test fixtures for the TN Lottery test suite."""

import pytest
from click.testing import CliRunner
from tn_lottery.lottery import Lottery
from tn_lottery.cli import cli


@pytest.fixture
def lottery():
    """Provide a Lottery instance."""
    return Lottery()


@pytest.fixture
def cli_runner():
    """Provide a CLI test runner."""
    return CliRunner()


@pytest.fixture
def known_powerball_draw():
    """Known winning draw for deterministic testing."""
    return ([5, 10, 15, 20, 25], 10)


@pytest.fixture
def known_powerball_player():
    """Known player draw for deterministic testing."""
    return ([5, 10, 15, 20, 25], 10)


@pytest.fixture
def mock_db(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test_lottery.db"
    return str(db_path)
