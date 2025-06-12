"""
synk_channel - GitHubリポジトリとDiscordチャンネルの同期モジュール

このモジュールは、GitHubのorganizationに作成されたリポジトリの情報を取得し、
Discordのチャンネルと同期させる機能を提供します。

使用方法:
1. .envファイルに必要な環境変数を設定
2. `/sync-repos` コマンドで手動同期
3. `/list-repos` コマンドでリポジトリ一覧表示
"""

from .sync_channel import SyncChannel, setup

__all__ = ['SyncChannel', 'setup']
