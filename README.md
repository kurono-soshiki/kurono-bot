# kurono-bot
github organisationのためのbot

## Features

- **Repository Channel Management**: Automatically creates Discord channels when repositories are created in a GitHub organization
- **Webhook Integration**: Receives GitHub webhooks for real-time repository events
- **Manual Sync**: Sync existing repositories when the bot is first enabled
- **Modular Architecture**: Easy to add new bot features

## Setup

1. Copy the environment template:
```bash
cp .env.sample .env
```

2. Edit `.env` and set your configuration values:
```bash
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_CATEGORY_ID=your_discord_category_id

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_ORG=your-github-organization
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Optional
GEMINI_API_KEY=your_gemini_api_key_here
WEBHOOK_PORT=8080
```

3. Install dependencies with Poetry:
```bash
poetry install
```

4. Run the bot:
```bash
poetry run python src/main.py
```

### GitHub Webhook Setup

To enable automatic channel creation, configure a GitHub webhook:

1. Go to your GitHub organization settings → Webhooks
2. Add a new webhook with:
   - **Payload URL**: `http://your-server:8080/webhook`
   - **Content type**: `application/json`
   - **Secret**: The same value as `GITHUB_WEBHOOK_SECRET` in your `.env`
   - **Events**: Select "Repositories"

### Discord Bot Setup

1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot and copy the token to `DISCORD_TOKEN`
3. Add the bot to your server with the "Manage Channels" permission
4. Find your Discord server ID and the category ID where you want channels created

## Docker Deployment

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Project Structure

- `src/main.py` - Main bot entry point
- `src/config.py` - Configuration loading from environment variables
- `pyproject.toml` - Poetry project configuration and dependencies
- `Dockerfile` - Container build configuration  
- `docker-compose.yaml` - Multi-service deployment with VoiceVox

## Adding Modules

To add bot modules, import them in `src/main.py` and call their setup functions:

```python
from your_module import your_module as module_bot
module_bot.setup(tree, client)
```
