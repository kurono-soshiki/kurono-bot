# kurono-bot
github organisationのためのbot

## Setup

1. Copy the environment template:
```bash
cp .env.sample .env
```

2. Edit `.env` and set your Discord bot token:
```bash
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
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

## Project Structure

- `src/main.py` - Main bot entry point
- `src/config.py` - Configuration loading from environment variables
- `src/ytdl_wrapper.py` - YouTube audio downloading utility
- `pyproject.toml` - Poetry project configuration and dependencies
- `Dockerfile` - Container build configuration  
- `docker-compose.yaml` - Multi-service deployment with VoiceVox

## Adding Modules

To add bot modules, import them in `src/main.py` and call their setup functions:

```python
from your_module import your_module as module_bot
module_bot.setup(tree, client)
```
