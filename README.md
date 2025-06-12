# kurono-bot
github organisationのためのbot

## Setup

1. Copy the environment template:
```bash
cp .env.sample .env
```

2. Edit `.env` and set your configuration:
```bash
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_ORGANIZATION=your-organization-name
DISCORD_GUILD_ID=123456789012345678
DISCORD_CATEGORY_ID=123456789012345678
```

3. Install dependencies with Poetry:
```bash
poetry install
```

4. Run the bot:
```bash
poetry run python src/main.py
```

## Docker Deployment

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Modules

### synk_channel
GitHubのorganizationリポジトリとDiscordチャンネルを同期するモジュール

**機能:**
- GitHubリポジトリの自動検出
- 対応するDiscordチャンネルの作成・更新
- スラッシュコマンド (`/sync-repos`, `/list-repos`)
- 定期実行スクリプト

**詳細:** [src/synk_channel/README.md](src/synk_channel/README.md)

## Project Structure

- `src/main.py` - Main bot entry point
- `src/config.py` - Configuration loading from environment variables
- `src/synk_channel/` - GitHub repository sync module
- `scripts/sync_repositories.py` - Scheduled sync script
- `pyproject.toml` - Poetry project configuration and dependencies
- `Dockerfile` - Container build configuration  
- `docker-compose.yaml` - Multi-service deployment with VoiceVox

## Adding Modules

To add bot modules, import them in `src/main.py` and call their setup functions:

```python
from your_module import your_module as module_bot
module_bot.setup(tree, client)
```
