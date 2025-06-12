import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PersistentStorage:
    """設定データの永続化クラス"""
    
    def __init__(self, storage_file: str = "comment_connector_data.json"):
        self.storage_file = storage_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """データファイルから設定を読み込み"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data from {self.storage_file}: {e}")
        
        return {
            "user_mappings": {},
            "channel_mappings": {},
            "thread_mappings": {}
        }
    
    def save_data(self):
        """データファイルに設定を保存"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving data to {self.storage_file}: {e}")
    
    def get_user_mappings(self) -> Dict[str, str]:
        """ユーザー紐づけ情報を取得"""
        return self.data.get("user_mappings", {})
    
    def set_user_mapping(self, github_username: str, discord_user_id: str):
        """ユーザー紐づけ情報を設定"""
        self.data["user_mappings"][github_username] = discord_user_id
        self.save_data()
    
    def get_channel_mappings(self) -> Dict[str, int]:
        """チャンネル紐づけ情報を取得"""
        return self.data.get("channel_mappings", {})
    
    def set_channel_mapping(self, repo_name: str, channel_id: int):
        """チャンネル紐づけ情報を設定"""
        self.data["channel_mappings"][repo_name] = channel_id
        self.save_data()
    
    def get_thread_mappings(self) -> Dict[str, int]:
        """スレッド紐づけ情報を取得"""
        return self.data.get("thread_mappings", {})
    
    def set_thread_mapping(self, github_url: str, thread_id: int):
        """スレッド紐づけ情報を設定"""
        self.data["thread_mappings"][github_url] = thread_id
        self.save_data()
    
    def remove_thread_mapping(self, github_url: str):
        """スレッド紐づけ情報を削除"""
        if github_url in self.data.get("thread_mappings", {}):
            del self.data["thread_mappings"][github_url]
            self.save_data()

def extract_repo_and_issue_from_url(github_url: str) -> tuple[str, int, str]:
    """
    GitHub URLからリポジトリ名、issue/PR番号、タイプを抽出
    
    Args:
        github_url: GitHub URL (e.g., https://github.com/org/repo/issues/123)
    
    Returns:
        tuple: (repo_name, issue_number, type) where type is 'issues' or 'pull'
    """
    try:
        parts = github_url.split('/')
        repo_name = parts[4]  # github.com/org/repo/issues/123
        issue_type = parts[5]  # 'issues' or 'pull'
        issue_number = int(parts[6])
        return repo_name, issue_number, issue_type
    except (IndexError, ValueError) as e:
        logger.error(f"Error parsing GitHub URL {github_url}: {e}")
        raise ValueError(f"Invalid GitHub URL format: {github_url}")

def format_github_content(content: str, max_length: int = 1000) -> str:
    """
    GitHubコンテンツをDiscord表示用にフォーマット
    
    Args:
        content: 元のコンテンツ
        max_length: 最大文字数
    
    Returns:
        str: フォーマット済みコンテンツ
    """
    if not content:
        return "*(No description provided)*"
    
    # Markdownの一部をDiscord用に変換
    content = content.replace('```', '`​`​`')  # コードブロックの競合を避ける
    
    if len(content) > max_length:
        return content[:max_length-3] + "..."
    
    return content

def create_github_embed(title: str, description: str, url: str, color: int, 
                       fields: list = None, author: str = None) -> dict:
    """
    GitHub通知用のEmbed辞書を作成
    
    Args:
        title: Embedタイトル
        description: Embed説明
        url: GitHub URL
        color: Embedカラー
        fields: 追加フィールドのリスト
        author: 作成者名
    
    Returns:
        dict: Discord Embed用辞書
    """
    embed_data = {
        "title": title,
        "description": format_github_content(description),
        "url": url,
        "color": color,
        "timestamp": None  # 現在時刻で設定される
    }
    
    fields_list = []
    if author:
        fields_list.append({
            "name": "Author",
            "value": author,
            "inline": True
        })
    
    if fields:
        fields_list.extend(fields)
    
    if fields_list:
        embed_data["fields"] = fields_list
    
    return embed_data
