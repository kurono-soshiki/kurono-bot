"""
Tests for repository channel manager
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from repo_channels import RepositoryChannelManager


@pytest.mark.asyncio
async def test_repository_channel_manager_init():
    """Test that RepositoryChannelManager can be initialized."""
    mock_client = Mock()
    manager = RepositoryChannelManager(mock_client)
    
    assert manager.discord_client == mock_client
    assert manager.guild is None
    assert manager.category is None


@pytest.mark.asyncio
async def test_channel_name_sanitization():
    """Test that repository names are properly sanitized for Discord channel names."""
    mock_client = Mock()
    manager = RepositoryChannelManager(mock_client)
    
    # Mock guild and category
    mock_guild = Mock()
    mock_category = Mock()
    mock_category.channels = []  # Empty list of channels
    manager.guild = mock_guild
    manager.category = mock_category
    
    # Mock the channel creation
    mock_channel = AsyncMock()
    mock_guild.create_text_channel = AsyncMock(return_value=mock_channel)
    mock_channel.send = AsyncMock()
    
    # Test channel creation with various repository names
    test_cases = [
        ("Test Repository", "test-repository"),
        ("my_awesome_repo", "my-awesome-repo"),
        ("UPPERCASE_REPO", "uppercase-repo"),
        ("Mixed-Case_Repo", "mixed-case-repo"),
    ]
    
    for repo_name, expected_channel_name in test_cases:
        # Reset mock
        mock_guild.create_text_channel.reset_mock()
        
        await manager.create_channel_for_repository(repo_name, "https://github.com/test/repo")
        
        # Verify the channel was created with the expected name
        mock_guild.create_text_channel.assert_called_once()
        call_args = mock_guild.create_text_channel.call_args
        assert call_args[1]['name'] == expected_channel_name


@pytest.mark.asyncio
async def test_webhook_signature_verification():
    """Test webhook signature verification."""
    mock_client = Mock()
    manager = RepositoryChannelManager(mock_client)
    
    # Test with no secret configured
    with patch('repo_channels.config.GITHUB_WEBHOOK_SECRET', None):
        assert manager.verify_webhook_signature(b"test", "signature") is True
    
    # Test with secret configured
    with patch('repo_channels.config.GITHUB_WEBHOOK_SECRET', 'secret'):
        # Valid signature
        import hmac
        import hashlib
        payload = b"test payload"
        expected_sig = hmac.new(b'secret', payload, hashlib.sha256).hexdigest()
        assert manager.verify_webhook_signature(payload, f"sha256={expected_sig}") is True
        
        # Invalid signature
        assert manager.verify_webhook_signature(payload, "sha256=invalid") is False


if __name__ == "__main__":
    pytest.main([__file__])