# Synk Channel モジュール

GitHubのorganizationに作成されたリポジトリの情報を取得し、Discordのチャンネルと同期させるモジュール

## 機能

### 基本機能
- GitHubのorganizationに作成されたリポジトリの情報を取得
- Discordのチャンネルと同期させる
    - 指定されたDiscordサーバーのカテゴリ内にリポジトリと同名のチャンネルを生成します
    - 取得できなかったリポジトリは、同期の対象外となる、チャンネルは削除されない
    - すでに存在するチャンネルは、リポジトリの情報を更新します

### 同期タイミング
- 手動での同期（Discordスラッシュコマンド）
- 定期的な同期（cronなどで定期的に実行）

## セットアップ

### 1. 環境変数の設定

`.env`ファイルに以下を設定してください：

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# GitHub Organization名
GITHUB_ORGANIZATION=your-organization-name

# Discord Guild ID（サーバーID）
DISCORD_GUILD_ID=123456789012345678

# Discord Category ID（カテゴリID）
DISCORD_CATEGORY_ID=123456789012345678
```

### 2. GitHub Personal Access Tokenの取得

1. GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. "Generate new token (classic)" をクリック
3. 以下のスコープを選択：
   - `repo` (プライベートリポジトリにアクセスする場合)
   - `public_repo` (パブリックリポジトリのみの場合)
   - `read:org` (organization情報の読み取り)

### 3. Discord設定

1. Botに以下の権限を付与：
   - `Send Messages`
   - `Manage Channels`
   - `View Channels`
   - `Use Slash Commands`

2. 同期先のカテゴリIDを取得：
   - Discordの開発者モードを有効化
   - カテゴリを右クリック > "IDをコピー"

## 使用方法

### スラッシュコマンド

#### `/sync-repos`
GitHubリポジトリとDiscordチャンネルを手動で同期します。

- **権限**: 管理者権限が必要
- **実行結果**: 作成・更新されたチャンネル数とエラー数を表示

#### `/list-repos`
GitHubリポジトリの一覧を表示します。

- **権限**: 全ユーザー
- **実行結果**: 最大20個のリポジトリ情報を表示（名前、説明、言語、スター数など）

### 定期実行

cronで定期的に同期を実行する場合：

```bash
# 毎日午前9時に実行
0 9 * * * cd /path/to/kurono-bot && python scripts/sync_repositories.py >> logs/sync.log 2>&1

# 毎時0分に実行
0 * * * * cd /path/to/kurono-bot && python scripts/sync_repositories.py >> logs/sync.log 2>&1
```

手動で同期スクリプトを実行：

```bash
cd /path/to/kurono-bot
python scripts/sync_repositories.py
```

## ファイル構成

```
synk_channel/
├── __init__.py           # モジュール初期化
├── synk_channel.py       # メインロジック
├── utils.py              # ユーティリティ関数
├── test_synk_channel.py  # テストファイル
└── README.md             # このファイル
```

## ログファイル

同期処理のログは以下に保存されます：

- `logs/sync_repositories.log` - 詳細なログ
- `logs/sync_stats.log` - 統計情報（CSV形式）

統計ファイルの形式：
```csv
timestamp,created,updated,errors,duration
2023-12-31T09:00:00,5,10,0,15.42
```

## トラブルシューティング

### よくあるエラー

1. **"GitHub token not found"**
   - `.env`ファイルに`GITHUB_TOKEN`が設定されているか確認
   - トークンの権限が適切か確認

2. **"Guild not found"**
   - `DISCORD_GUILD_ID`が正しいか確認
   - BotがそのサーバーにJoinしているか確認

3. **"Category not found"**
   - `DISCORD_CATEGORY_ID`が正しいか確認
   - Botにそのカテゴリへのアクセス権限があるか確認

4. **"Permission denied"**
   - Botの権限設定を確認
   - 特に「チャンネルの管理」権限が必要

### デバッグ

詳細なログを確認するには：

```bash
# 同期スクリプトの実行ログを確認
tail -f logs/sync_repositories.log

# 統計情報を確認
cat logs/sync_stats.log
```

## API制限について

- GitHub API: 認証済みリクエストは1時間あたり5,000回
- Discord API: レート制限あり（自動的に調整）

大量のリポジトリがある場合は、同期間隔を調整してください。

## テスト

```bash
# テスト実行
poetry run pytest src/synk_channel/test_synk_channel.py -v

# カバレッジ付きテスト
poetry run pytest src/synk_channel/test_synk_channel.py --cov=synk_channel
```

