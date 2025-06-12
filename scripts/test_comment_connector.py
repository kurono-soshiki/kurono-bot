#!/usr/bin/env python3
# filepath: /Users/ytm/kurono-bot/scripts/test_comment_connector.py
"""
Comment Connector module test script
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
import json
from unittest.mock import MagicMock
import discord
from comment_connecter.comment_connecter import CommentConnector
from comment_connecter.utils import PersistentStorage, extract_repo_and_issue_from_url

def test_url_parsing():
    """GitHub URL解析のテスト"""
    print("Testing GitHub URL parsing...")
    
    test_cases = [
        ("https://github.com/kurono-soshiki/test-repo/issues/123", ("test-repo", 123, "issues")),
        ("https://github.com/kurono-soshiki/test-repo/pull/456", ("test-repo", 456, "pull")),
    ]
    
    for url, expected in test_cases:
        try:
            result = extract_repo_and_issue_from_url(url)
            assert result == expected, f"Expected {expected}, got {result}"
            print(f"✅ {url} -> {result}")
        except Exception as e:
            print(f"❌ {url} -> Error: {e}")

def test_persistent_storage():
    """永続化ストレージのテスト"""
    print("\nTesting persistent storage...")
    
    # テスト用の一時ファイル
    test_file = "test_storage.json"
    
    try:
        storage = PersistentStorage(test_file)
        
        # ユーザーマッピングのテスト
        storage.set_user_mapping("github_user", "discord_123")
        mappings = storage.get_user_mappings()
        assert mappings["github_user"] == "discord_123"
        print("✅ User mapping test passed")
        
        # チャンネルマッピングのテスト
        storage.set_channel_mapping("test-repo", 123456789)
        channel_mappings = storage.get_channel_mappings()
        assert channel_mappings["test-repo"] == 123456789
        print("✅ Channel mapping test passed")
        
        # スレッドマッピングのテスト
        storage.set_thread_mapping("https://github.com/test/repo/issues/1", 987654321)
        thread_mappings = storage.get_thread_mappings()
        assert thread_mappings["https://github.com/test/repo/issues/1"] == 987654321
        print("✅ Thread mapping test passed")
        
    finally:
        # テストファイルを削除
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """メインテスト関数"""
    print("=== Comment Connector Module Tests ===")
    
    # 基本機能のテスト
    test_url_parsing()
    test_persistent_storage()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()