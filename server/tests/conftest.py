"""Shared test fixtures for Lumina server tests."""

import pytest
from fastapi.testclient import TestClient

from lumina.main import app


@pytest.fixture
def client():
    return TestClient(app)
