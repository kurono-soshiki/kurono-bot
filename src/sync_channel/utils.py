"""
設定の検証とヘルパー関数
"""

import logging
import config

logger = logging.getLogger(__name__)

def validate_config() -> bool:
    """設定の妥当性をチェック"""
    missing_configs = []
    
    if not config.DISCORD_TOKEN:
        missing_configs.append("DISCORD_TOKEN")
    
    if not config.GITHUB_TOKEN:
        missing_configs.append("GITHUB_TOKEN")
    
    if not config.GITHUB_ORGANIZATION:
        missing_configs.append("GITHUB_ORGANIZATION")
    
    if config.DISCORD_GUILD_ID == 0:
        missing_configs.append("DISCORD_GUILD_ID")
    
    if config.DISCORD_CATEGORY_ID == 0:
        missing_configs.append("DISCORD_CATEGORY_ID")
    
    if missing_configs:
        logger.error(f"以下の設定が不足しています: {', '.join(missing_configs)}")
        return False
    
    return True

def get_channel_name_from_repo(repo_name: str) -> str:
    """リポジトリ名からDiscordチャンネル名を生成"""
    return repo_name.lower().replace('_', '-').replace(' ', '-')

def format_repo_description(description: str, max_length: int = 100) -> str:
    """リポジトリの説明文を整形"""
    if not description:
        return "説明なし"
    
    if len(description) <= max_length:
        return description
    
    return description[:max_length - 3] + "..."
