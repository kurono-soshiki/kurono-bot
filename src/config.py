from dotenv import load_dotenv

load_dotenv()

import os
# import sys
# sys.path.append(os.getcwd())
import logging

logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# GitHub integration settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ORG = os.getenv('GITHUB_ORG')
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

# Discord settings
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
DISCORD_CATEGORY_ID = os.getenv('DISCORD_CATEGORY_ID')

# Webhook server settings
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8080))