from dotenv import load_dotenv

load_dotenv()

import os
# import sys
# sys.path.append(os.getcwd())
import logging

logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ORGANIZATION = os.getenv('GITHUB_ORGANIZATION', 'kurono-soshiki')
DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID', '0'))
DISCORD_CATEGORY_ID = int(os.getenv('DISCORD_CATEGORY_ID', '0'))
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8000'))
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')