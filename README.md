# kurono-bot
github organisationのためのbot

## Setup

1. 環境変数テンプレートをコピー:
```bash
cp .env.sample .env
```

2. `.env` を編集し、各種トークンや設定を記入:
```bash
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_ORGANIZATION=your-organization-name
DISCORD_GUILD_ID=123456789012345678
DISCORD_CATEGORY_ID=123456789012345678
```

## Docker デプロイ（Compose v2系対応）

ビルドと起動:
```bash
docker compose up --build
```

### WebHook受信のためのポート公開

```yaml
services:
  bot:
    # ...既存の設定...
    ports:
      - "8035:8000"  # ← 例: ホスト8035→コンテナ8000
```
`.env` で `WEBHOOK_PORT` を指定している場合は、
`"8035:8000"` の「右側」を `.env` の `WEBHOOK_PORT` に合わせてください。

### GitHub WebHook設定例

- Payload URL: `http://<サーバのIPまたはドメイン>:8000/webhook/github`
- Content type: `application/json`
- Events: Send me everything

## Modules

### synk_channel
GitHubのorganizationリポジトリとDiscordチャンネルを同期するモジュール

**機能:**
- GitHubリポジトリの自動検出
- 対応するDiscordチャンネルの作成・更新
- スラッシュコマンド (`/sync-repos`, `/list-repos`)
- 定期実行スクリプト

**詳細:** [src/synk_channel/README.md](src/synk_channel/README.md)

### comment_connecter
GitHubのissue/PRとDiscordチャンネルのコメントを双方向同期するモジュール

**機能:**
- GitHub webhook受信とDiscord通知
- Discord→GitHubへのコメント投稿
- ユーザー・チャンネルの紐づけ管理
- 自動スレッド作成

## Discord コマンド

### Repository Sync Commands
- `/sync-repos` - GitHubリポジトリとDiscordチャンネルを手動同期（管理者のみ）
- `/list-repos` - Organization内のリポジトリ一覧を表示

### Comment Connector Commands
- `/link_user <github_username> [discord_user]` - GitHubユーザーとDiscordユーザーを紐づけ
- `/link_channel <repo_name> [channel]` - GitHubリポジトリとDiscordチャンネルを紐づけ
- `/auto_link` - チャンネル名とリポジトリ名に基づいて自動で紐づけ
- `/connector_status` - Comment Connectorの設定状況を確認
- `/unlink_user <github_username>` - GitHubユーザーとDiscordユーザーの紐づけを解除
- `/unlink_channel <repo_name>` - GitHubリポジトリとDiscordチャンネルの紐づけを解除

### 使用方法
1. `/sync-repos` でDiscordチャンネルを作成
2. `/auto_link` でチャンネルとリポジトリを一括紐づけ
3. GitHubのorganization設定でwebhookを設定
4. GitHub上のissue/PRの作成・コメントがDiscordに自動通知される
5. Discordスレッド内でbotをメンション(@bot)してコメントすると、GitHubにコメントが投稿される

## Project Structure

- `src/main.py` - Main bot entry point
- `src/config.py` - Configuration loading from environment variables
- `src/synk_channel/` - GitHub repository sync module
- `scripts/sync_repositories.py` - Scheduled sync script
- `pyproject.toml` - Poetry project configuration and dependencies
- `Dockerfile` - Container build configuration  
- `docker-compose.yaml` - Multi-service deployment with VoiceVox

## Adding Modules

新しいモジュールを追加する場合は、`src/main.py` にインポートし、setup関数を呼び出してください:

```python
from your_module import your_module as module_bot
module_bot.setup(tree, client)
```

---

### 注意
- v2系では `docker compose`（スペースあり）コマンドを使用してください。
- v1系の `docker-compose`（ハイフンあり）は非推奨です。
- 詳細は[公式ドキュメント](https://docs.docker.com/compose/)を参照してください。
