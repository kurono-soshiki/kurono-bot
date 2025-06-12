# filepath: /Users/ytm/kurono-bot/scripts/test_bot_startup.py
#!/usr/bin/env python3
"""
Bot startup test script - check if modules load properly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
import discord

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_module_imports():
    """モジュールのインポートテスト"""
    print("=== Testing Module Imports ===")
    
    try:
        # comment_connectorモジュールのインポート
        from comment_connecter import comment_connecter
        print("✅ comment_connecter module imported successfully")
        
        from synk_channel import synk_channel  
        print("✅ synk_channel module imported successfully")
        
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    return True

async def test_comment_connector_setup():
    """Comment Connectorセットアップのテスト"""
    print("\n=== Testing Comment Connector Setup ===")
    
    try:
        # モッククライアントとツリーを作成
        mock_client = MagicMock()
        mock_client.user = MagicMock()
        mock_client.user.id = 123456789
        
        mock_tree = MagicMock()
        mock_tree.command = MagicMock(return_value=lambda f: f)
        
        # comment_connectorのセットアップ
        from comment_connecter import comment_connecter
        
        # setup関数を呼び出し（WebHookサーバー起動は無効化）
        await comment_connecter.setup(mock_tree, mock_client)
        
        print("✅ Comment Connector setup completed successfully")
        
        # グローバルインスタンスが作成されているかチェック
        assert comment_connecter.comment_connector is not None
        print("✅ Global comment_connector instance created")
        
        # 基本的なメソッドが利用できるかチェック
        connector = comment_connecter.comment_connector
        assert hasattr(connector, 'user_mappings')
        assert hasattr(connector, 'channel_mappings') 
        assert hasattr(connector, 'thread_mappings')
        print("✅ Comment Connector instance has required attributes")
        
    except Exception as e:
        print(f"❌ Comment Connector setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_webhook_payload_processing():
    """WebHookペイロード処理のテスト（モック）"""
    print("\n=== Testing WebHook Payload Processing ===")
    
    try:
        from comment_connecter import comment_connecter
        
        # モックデータ作成
        sample_issue_payload = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue for testing purposes",
                "html_url": "https://github.com/kurono-soshiki/test-repo/issues/1",
                "user": {"login": "test_user"}
            },
            "repository": {
                "name": "test-repo",
                "html_url": "https://github.com/kurono-soshiki/test-repo"
            }
        }
        
        # コネクターインスタンス取得
        connector = comment_connecter.comment_connector
        if connector is None:
            print("❌ Comment connector not initialized")
            return False
        
        # モックチャンネルを設定
        mock_channel = MagicMock()
        mock_message = MagicMock()
        mock_thread = MagicMock()
        mock_thread.id = 987654321
        
        mock_channel.send = AsyncMock(return_value=mock_message)
        mock_message.create_thread = AsyncMock(return_value=mock_thread)
        
        # チャンネルマッピングを設定
        connector.channel_mappings["test-repo"] = 123456789
        connector.client.get_channel = MagicMock(return_value=mock_channel)
        
        # issue作成イベントの処理テスト
        await connector.handle_issue_event(sample_issue_payload)
        
        # モックが呼ばれたかチェック
        connector.client.get_channel.assert_called_with(123456789)
        mock_channel.send.assert_called_once()
        mock_message.create_thread.assert_called_once()
        
        print("✅ Issue event processing test passed")
        
        # スレッドマッピングが作成されたかチェック
        issue_url = sample_issue_payload["issue"]["html_url"]
        assert issue_url in connector.thread_mappings
        print("✅ Thread mapping created successfully")
        
    except Exception as e:
        print(f"❌ WebHook payload processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_discord_to_github_conversion():
    """Discord → GitHub変換のテスト"""
    print("\n=== Testing Discord to GitHub Conversion ===")
    
    try:
        from comment_connecter import comment_connecter
        
        connector = comment_connecter.comment_connector
        if connector is None:
            print("❌ Comment connector not initialized")
            return False
        
        # ユーザーマッピングを設定
        connector.user_mappings["github_user"] = "123456789"
        
        # GitHub → Discord変換テスト
        discord_mention = connector.convert_github_mention("github_user")
        assert discord_mention == "<@123456789>"
        print("✅ GitHub to Discord mention conversion works")
        
        # Discord → GitHub変換テスト  
        github_mention = connector.convert_discord_mention("123456789")
        assert github_mention == "@github_user"
        print("✅ Discord to GitHub mention conversion works")
        
        # 存在しないユーザーのテスト
        unknown_discord = connector.convert_github_mention("unknown_user")
        assert unknown_discord == "@unknown_user"
        print("✅ Unknown user handling works correctly")
        
    except Exception as e:
        print(f"❌ Discord to GitHub conversion test failed: {e}")
        return False
    
    return True

async def main():
    """メインテスト関数"""
    print("=== Bot Startup and Integration Tests ===\n")
    
    success = True
    
    # 各テストを実行
    if not await test_module_imports():
        success = False
    
    if not await test_comment_connector_setup():
        success = False
    
    if not await test_webhook_payload_processing():
        success = False
    
    if not await test_discord_to_github_conversion():
        success = False
    
    print(f"\n=== Test Results ===")
    if success:
        print("🎉 All tests passed successfully!")
        print("\nComment Connector module is ready to use.")
        print("Next steps:")
        print("1. Set up your .env file with GitHub token")
        print("2. Configure GitHub webhooks")
        print("3. Run the bot with: poetry run python src/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
