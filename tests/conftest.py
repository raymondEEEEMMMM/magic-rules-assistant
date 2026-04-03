# tests/conftest.py
# pytest configuration for handling starlette/anyio event loop issues

import pytest


def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio test")


# Disable asyncio mode to avoid event loop issues with starlette TestClient
pytest_plugins = []

