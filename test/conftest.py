"""
Pytest configuration and fixtures for the transfers microservice tests.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.transfers.app import create_app
from src.transfers.core import extensions as ext


@pytest.fixture
async def app():
    """
    Create and configure a test instance of the Quart app.
    Mocks the database connection to avoid requiring a real MongoDB instance.
    """
    # Mock Redis
    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock()
    mock_redis.close = AsyncMock()
    
    # Mock psutil
    mock_vm = MagicMock()
    mock_vm.percent = 30.0
    
    # Mock asyncio.create_task to avoid background tasks in tests
    mock_task = MagicMock()
    mock_task.cancel = MagicMock()
    
    # Mock the database connection before creating the app
    with patch.object(ext, 'init_db_client', new_callable=AsyncMock), \
         patch.object(ext, 'close_db_client', new_callable=AsyncMock), \
         patch.object(ext, 'db', MagicMock()), \
         patch('redis.asyncio.Redis', return_value=mock_redis), \
         patch('psutil.cpu_percent', return_value=10.0), \
         patch('psutil.virtual_memory', return_value=mock_vm), \
         patch('asyncio.create_task', return_value=mock_task):
        
        app = create_app()
        
        # Initialize feature toggles and throttling for tests
        from src.transfers.core.feature_toggles import init_feature_manager
        from src.transfers.core.throttling import init_throttling_manager, ThrottleConfig
        
        init_feature_manager(None)
        init_throttling_manager(ThrottleConfig(
            cpu_warning=80,
            cpu_critical=90,
            memory_warning=80,
            memory_critical=90,
            max_concurrent_requests=100,
            warning_concurrent_requests=80
        ))
        
        async with app.app_context():
            yield app


@pytest.fixture
async def client(app):
    """
    Create a test client for the app.
    This allows making HTTP requests to the app without running a server.
    """
    return app.test_client()
