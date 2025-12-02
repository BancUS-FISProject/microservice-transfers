"""
Pytest configuration and fixtures for the transfers microservice tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.transfers.app import create_app
from src.transfers.core import extensions as ext


@pytest.fixture
async def app():
    """
    Create and configure a test instance of the Quart app.
    Mocks the database connection to avoid requiring a real MongoDB instance.
    """
    # Mock the database connection before creating the app
    with patch.object(ext, 'init_db_client', new_callable=AsyncMock):
        with patch.object(ext, 'db', MagicMock()):
            app = create_app()
            app.config['TESTING'] = True
            
            # Mock the startup process
            async with app.app_context():
                yield app


@pytest.fixture
async def client(app):
    """
    Create a test client for the app.
    This allows making HTTP requests to the app without running a server.
    """
    return app.test_client()
