"""
synk_channel モジュールのテスト
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import discord
from src.sync_channel.sync_channel import SyncChannel
from sync_channel.utils import validate_config, get_channel_name_from_repo, format_repo_description


class TestSyncChannel:
    
    @pytest.fixture
    def mock_client(self):
        """Discordクライアントのモック"""
        client = Mock(spec=discord.Client)
        return client
    
    @pytest.fixture
    def sync_channel(self, mock_client):
        """SyncChannelインスタンス"""
        with patch('synk_channel.synk_channel.validate_config', return_value=True):
            with patch('synk_channel.synk_channel.config.GITHUB_TOKEN', 'mock_token'):
                with patch('synk_channel.synk_channel.config.GITHUB_ORGANIZATION', 'test-org'):
                    with patch('synk_channel.synk_channel.config.DISCORD_GUILD_ID', 123456):
                        with patch('synk_channel.synk_channel.config.DISCORD_CATEGORY_ID', 789012):
                            return SyncChannel(mock_client)
    
    @pytest.mark.asyncio
    async def test_get_github_repositories(self, sync_channel):
        """GitHubリポジトリ取得のテスト"""
        # GitHubクライアントのモック
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.description = "Test repository"
        mock_repo.html_url = "https://github.com/test-org/test-repo"
        mock_repo.created_at = "2023-01-01"
        mock_repo.updated_at = "2023-12-31"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.private = False
        mock_repo.archived = False
        
        mock_org = Mock()
        mock_org.get_repos.return_value = [mock_repo]
        
        with patch.object(sync_channel.github, 'get_organization', return_value=mock_org):
            repos = await sync_channel.get_github_repositories()
            
            assert len(repos) == 1
            assert repos[0]['name'] == 'test-repo'
            assert repos[0]['description'] == 'Test repository'
            assert repos[0]['language'] == 'Python'
    
    @pytest.mark.asyncio
    async def test_get_discord_channels(self, sync_channel, mock_client):
        """Discordチャンネル取得のテスト"""
        # ギルドとカテゴリのモック
        mock_channel = Mock(spec=discord.TextChannel)
        mock_channel.name = "test-channel"
        
        mock_category = Mock(spec=discord.CategoryChannel)
        mock_category.channels = [mock_channel]
        
        mock_guild = Mock()
        mock_guild.get_channel.return_value = mock_category
        
        mock_client.get_guild.return_value = mock_guild
        
        channels = await sync_channel.get_discord_channels()
        
        assert len(channels) == 1
        assert channels[0].name == "test-channel"


class TestUtils:
    
    def test_get_channel_name_from_repo(self):
        """リポジトリ名からチャンネル名への変換テスト"""
        assert get_channel_name_from_repo("Test_Repo") == "test-repo"
        assert get_channel_name_from_repo("My Project") == "my-project"
        assert get_channel_name_from_repo("simple-repo") == "simple-repo"
    
    def test_format_repo_description(self):
        """リポジトリ説明文の整形テスト"""
        assert format_repo_description("") == "説明なし"
        assert format_repo_description(None) == "説明なし"
        assert format_repo_description("短い説明") == "短い説明"
        
        long_desc = "これは非常に長い説明文です。" * 10
        formatted = format_repo_description(long_desc, 50)
        assert len(formatted) <= 50
        assert formatted.endswith("...")
    
    @patch('synk_channel.utils.config.DISCORD_TOKEN', 'token')
    @patch('synk_channel.utils.config.GITHUB_TOKEN', 'token')
    @patch('synk_channel.utils.config.GITHUB_ORGANIZATION', 'org')
    @patch('synk_channel.utils.config.DISCORD_GUILD_ID', 123)
    @patch('synk_channel.utils.config.DISCORD_CATEGORY_ID', 456)
    def test_validate_config_success(self):
        """設定検証の成功テスト"""
        assert validate_config() == True
    
    @patch('synk_channel.utils.config.DISCORD_TOKEN', '')
    def test_validate_config_failure(self):
        """設定検証の失敗テスト"""
        assert validate_config() == False


@pytest.mark.asyncio
async def test_setup():
    """モジュールセットアップのテスト"""
    mock_tree = Mock(spec=discord.app_commands.CommandTree)
    mock_client = Mock(spec=discord.Client)
    
    from src.sync_channel.sync_channel import setup
    
    # セットアップが正常に実行されることを確認
    await setup(mock_tree, mock_client)
    
    # コマンドが登録されたことを確認
    assert mock_tree.command.call_count >= 2  # sync-repos, list-repos
