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
            # Mock the startup process
            mock_vm = MagicMock()
            mock_vm.percent = 30.0
            
            with patch('src.transfers.app.init_feature_manager') as mock_init_fm, \
                 patch('src.transfers.app.init_throttling_manager') as mock_init_tm, \
                 patch('src.transfers.app.redis.Redis', MagicMock()), \
                 patch('psutil.cpu_percent', return_value=10.0), \
                 patch('psutil.virtual_memory', return_value=mock_vm):
                 
                # Initialize them manually for the test context
                from src.transfers.core.feature_toggles import init_feature_manager
                init_feature_manager(None)
                
                from src.transfers.core.throttling import init_throttling_manager, ThrottleConfig
                init_throttling_manager(ThrottleConfig(cpu_warning=80, cpu_critical=90, memory_warning=80, memory_critical=90, max_concurrent_requests=100, warning_concurrent_requests=80))

                async with app.app_context():
                    yield app


@pytest.fixture
async def client(app):
    """
    Create a test client for the app.
    This allows making HTTP requests to the app without running a server.
    """
    return app.test_client()
