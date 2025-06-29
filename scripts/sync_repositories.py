#!/usr/bin/env python3
"""
GitHub リポジトリ同期の定期実行スクリプト

このスクリプトは cron などで定期実行することで、
GitHubリポジトリとDiscordチャンネルの自動同期を行います。

使用例:
    python scripts/sync_repositories.py

cron設定例（毎日午前9時に実行）:
    0 9 * * * cd /path/to/kurono-bot && python scripts/sync_repositories.py >> logs/sync.log 2>&1
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import discord
import config
from synk_channel.synk_channel import SyncChannel

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/sync_repositories.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class SyncBot:
    """同期専用のシンプルなBot"""
    
    def __init__(self):
        self.intents = discord.Intents.default()
        self.client = discord.Client(intents=self.intents)
        self.sync_channel = None
        
        @self.client.event
        async def on_ready():
            logger.info(f'Bot logged in as {self.client.user}')
            
            # 同期実行
            self.sync_channel = SyncChannel(self.client)
            await self.perform_sync()
            
            # 同期完了後にBotを終了
            await self.client.close()
    
    async def perform_sync(self):
        """同期処理を実行"""
        try:
            logger.info("GitHubリポジトリとDiscordチャンネルの同期を開始します")
            start_time = datetime.now()
            
            stats = await self.sync_channel.sync_repositories()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"同期完了 - "
                f"作成: {stats['created']}, "
                f"更新: {stats['updated']}, "
                f"エラー: {stats['errors']}, "
                f"実行時間: {duration:.2f}秒"
            )
            
            # 統計情報をファイルに保存
            await self.save_sync_stats(stats, duration)
            
        except Exception as e:
            logger.error(f"同期処理中にエラーが発生しました: {e}", exc_info=True)
    
    async def save_sync_stats(self, stats: dict, duration: float):
        """同期統計をファイルに保存"""
        try:
            os.makedirs('logs', exist_ok=True)
            
            with open('logs/sync_stats.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(
                    f"{timestamp},{stats['created']},{stats['updated']},{stats['errors']},{duration:.2f}\n"
                )
        except Exception as e:
            logger.error(f"統計保存中にエラー: {e}")
    
    def run(self):
        """Botを実行"""
        if not config.DISCORD_TOKEN:
            logger.error("DISCORD_TOKEN が設定されていません")
            return False
        
        try:
            self.client.run(config.DISCORD_TOKEN, log_handler=None)
            return True
        except Exception as e:
            logger.error(f"Bot実行中にエラー: {e}")
            return False

def main():
    """メイン関数"""
    logger.info("=== GitHub Repository Sync Script Started ===")
    
    # 設定の検証
    from synk_channel.utils import validate_config
    if not validate_config():
        logger.error("設定が不完全です。.envファイルを確認してください。")
        return 1
    
    # 同期Bot実行
    bot = SyncBot()
    success = bot.run()
    
    if success:
        logger.info("=== Sync Script Completed Successfully ===")
        return 0
    else:
        logger.error("=== Sync Script Failed ===")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
