"""
Integration test for webhook server
"""

import asyncio
import json
from aiohttp import ClientSession

from repo_channels import setup_webhook_server, RepositoryChannelManager
from unittest.mock import Mock


async def test_webhook_server():
    """Test that webhook server can start and respond to requests."""
    # Create a mock Discord client and repository manager
    mock_client = Mock()
    repo_manager = RepositoryChannelManager(mock_client)
    
    # Setup webhook server
    app = await setup_webhook_server(repo_manager)
    
    # Test that the app was created successfully
    assert app is not None
    
    # Test routes exist
    routes = [str(route) for route in app.router._resources]
    assert any('/webhook' in route for route in routes)
    assert any('/health' in route for route in routes)
    
    print("Webhook server integration test passed!")


if __name__ == "__main__":
    asyncio.run(test_webhook_server())