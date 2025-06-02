"""
Repository Channel Manager

Handles automatic creation of Discord channels for GitHub repositories.
"""

import asyncio
import hashlib
import hmac
import json
import logging
from typing import Optional, List

import discord
from aiohttp import web, ClientSession
from github import Github

import config

logger = logging.getLogger(__name__)


class RepositoryChannelManager:
    """Manages Discord channels for GitHub repositories."""
    
    def __init__(self, discord_client: discord.Client):
        self.discord_client = discord_client
        self.github_client = None
        self.guild = None
        self.category = None
        
        # Initialize GitHub client if token is available
        if config.GITHUB_TOKEN:
            self.github_client = Github(config.GITHUB_TOKEN)
    
    async def setup(self):
        """Initialize Discord guild and category."""
        if not config.DISCORD_GUILD_ID or not config.DISCORD_CATEGORY_ID:
            logger.warning("Discord guild ID or category ID not configured")
            return
            
        try:
            self.guild = self.discord_client.get_guild(int(config.DISCORD_GUILD_ID))
            if not self.guild:
                logger.error(f"Could not find guild with ID {config.DISCORD_GUILD_ID}")
                return
                
            self.category = self.guild.get_channel(int(config.DISCORD_CATEGORY_ID))
            if not self.category or not isinstance(self.category, discord.CategoryChannel):
                logger.error(f"Could not find category with ID {config.DISCORD_CATEGORY_ID}")
                return
                
            logger.info(f"Repository channel manager initialized for guild {self.guild.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup repository channel manager: {e}")
    
    async def create_channel_for_repository(self, repo_name: str, repo_url: str) -> Optional[discord.TextChannel]:
        """Create a Discord channel for a GitHub repository."""
        if not self.guild or not self.category:
            logger.error("Guild or category not initialized")
            return None
            
        # Sanitize channel name (Discord channel names must be lowercase and contain no spaces)
        channel_name = repo_name.lower().replace(' ', '-').replace('_', '-')
        
        # Check if channel already exists
        existing_channel = discord.utils.get(self.category.channels, name=channel_name)
        if existing_channel:
            logger.info(f"Channel #{channel_name} already exists")
            return existing_channel
            
        try:
            # Create the channel
            channel = await self.guild.create_text_channel(
                name=channel_name,
                category=self.category,
                topic=f"Repository: {repo_url}"
            )
            
            # Send welcome message
            embed = discord.Embed(
                title="🎉 Repository Channel Created",
                description=f"This channel was automatically created for the repository **{repo_name}**",
                color=0x00ff00,
                url=repo_url
            )
            embed.add_field(name="Repository", value=f"[{repo_name}]({repo_url})", inline=False)
            embed.set_footer(text="Powered by kurono-bot")
            
            await channel.send(embed=embed)
            
            logger.info(f"Created channel #{channel_name} for repository {repo_name}")
            return channel
            
        except Exception as e:
            logger.error(f"Failed to create channel for repository {repo_name}: {e}")
            return None
    
    async def sync_existing_repositories(self):
        """Sync channels for all existing repositories in the organization."""
        if not self.github_client or not config.GITHUB_ORG:
            logger.warning("GitHub client or organization not configured")
            return
            
        try:
            org = self.github_client.get_organization(config.GITHUB_ORG)
            repos = org.get_repos()
            
            logger.info(f"Syncing channels for existing repositories in {config.GITHUB_ORG}")
            
            for repo in repos:
                if not repo.private:  # Only handle public repos for now
                    await self.create_channel_for_repository(repo.name, repo.html_url)
                    # Add a small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
            logger.info("Repository sync completed")
            
        except Exception as e:
            logger.error(f"Failed to sync existing repositories: {e}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not config.GITHUB_WEBHOOK_SECRET:
            logger.warning("GitHub webhook secret not configured")
            return True  # Allow requests if no secret is set
            
        expected_signature = hmac.new(
            config.GITHUB_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Handle GitHub webhook requests."""
        try:
            # Verify signature
            signature = request.headers.get('X-Hub-Signature-256', '')
            payload = await request.read()
            
            if not self.verify_webhook_signature(payload, signature):
                logger.warning("Invalid webhook signature")
                return web.Response(status=401)
            
            # Parse event
            event_type = request.headers.get('X-GitHub-Event')
            data = json.loads(payload.decode())
            
            if event_type == 'repository':
                await self._handle_repository_event(data)
            
            return web.Response(status=200)
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return web.Response(status=500)
    
    async def _handle_repository_event(self, data: dict):
        """Handle repository creation/deletion events."""
        action = data.get('action')
        repository = data.get('repository', {})
        
        if action == 'created':
            repo_name = repository.get('name')
            repo_url = repository.get('html_url')
            
            if repo_name and repo_url:
                logger.info(f"Repository created: {repo_name}")
                await self.create_channel_for_repository(repo_name, repo_url)
        
        elif action == 'deleted':
            # Optionally handle repository deletion
            repo_name = repository.get('name')
            logger.info(f"Repository deleted: {repo_name}")
            # Note: We might want to archive or delete the channel


async def setup_webhook_server(repo_manager: RepositoryChannelManager) -> web.Application:
    """Setup the webhook server."""
    app = web.Application()
    app.router.add_post('/webhook', repo_manager.handle_webhook)
    
    # Health check endpoint
    async def health_check(request):
        return web.Response(text="OK")
    
    app.router.add_get('/health', health_check)
    
    return app


def setup(tree: discord.app_commands.CommandTree, client: discord.Client):
    """Setup the repository channel manager module."""
    repo_manager = RepositoryChannelManager(client)
    webhook_server_started = False
    
    @client.event
    async def on_ready():
        nonlocal webhook_server_started
        await repo_manager.setup()
        
        # Start webhook server only once
        if not webhook_server_started:
            webhook_server_started = True
            await start_webhook_server()
        
        # Sync existing repositories when bot starts
        if config.GITHUB_TOKEN and config.GITHUB_ORG:
            await repo_manager.sync_existing_repositories()
    
    # Start webhook server
    async def start_webhook_server():
        try:
            app = await setup_webhook_server(repo_manager)
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', config.WEBHOOK_PORT)
            await site.start()
            
            logger.info(f"Webhook server started on port {config.WEBHOOK_PORT}")
        except Exception as e:
            logger.error(f"Failed to start webhook server: {e}")
    
    # Add slash command for manual sync
    @tree.command(name="sync-repos", description="Manually sync repository channels")
    async def sync_repos(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer()
        await repo_manager.sync_existing_repositories()
        await interaction.followup.send("Repository sync completed!")