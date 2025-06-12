import discord
from discord.ext import commands
import aiohttp
import json
import asyncio
from typing import Dict, Optional, List, Tuple
import logging
from github import Github
import config
from .utils import PersistentStorage, extract_repo_and_issue_from_url, format_github_content, create_github_embed
from .exceptions import GitHubAPIError, WebHookError, DiscordAPIError, ConfigurationError

logger = logging.getLogger(__name__)

class CommentConnector:
    def __init__(self, client: discord.Client):
        self.client = client
        self.github = Github(config.GITHUB_TOKEN) if config.GITHUB_TOKEN else None
        self.storage = PersistentStorage()
        
        # 永続化されたデータを読み込み
        self.user_mappings = self.storage.get_user_mappings()
        self.thread_mappings = self.storage.get_thread_mappings()
        self.channel_mappings = self.storage.get_channel_mappings()
        
    async def setup_webhook_server(self, port: int = None):
        """WebHookサーバーを起動"""
        if port is None:
            port = config.WEBHOOK_PORT
            
        from aiohttp import web
        
        app = web.Application()
        app.router.add_post('/webhook/github', self.handle_github_webhook)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        logger.info(f"WebHook server started on port {port}")
        
    async def handle_github_webhook(self, request):
        """GitHub WebHookのイベントを処理"""
        from aiohttp import web
        
        try:
            payload = await request.json()
            event_type = request.headers.get('X-GitHub-Event')
            
            if event_type == 'issues':
                await self.handle_issue_event(payload)
            elif event_type == 'issue_comment':
                await self.handle_issue_comment_event(payload)
            elif event_type == 'pull_request':
                await self.handle_pull_request_event(payload)
            elif event_type == 'pull_request_review':
                await self.handle_pull_request_review_event(payload)
            elif event_type == 'pull_request_review_comment':
                await self.handle_pull_request_review_comment_event(payload)
                
            return web.Response(text='OK')
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return web.Response(text='Error', status=500)
    
    async def handle_issue_event(self, payload):
        """Issueイベントの処理"""
        action = payload['action']
        issue = payload['issue']
        repository = payload['repository']
        
        if action in ['opened', 'reopened']:
            await self.notify_issue_created(issue, repository)
        elif action == 'closed':
            await self.notify_issue_closed(issue, repository)
            
    async def handle_issue_comment_event(self, payload):
        """Issue コメントイベントの処理"""
        action = payload['action']
        comment = payload['comment']
        issue = payload['issue']
        repository = payload['repository']
        
        if action == 'created':
            await self.notify_issue_comment(comment, issue, repository)
            
    async def handle_pull_request_event(self, payload):
        """Pull Requestイベントの処理"""
        action = payload['action']
        pull_request = payload['pull_request']
        repository = payload['repository']
        
        if action in ['opened', 'reopened']:
            await self.notify_pull_request_created(pull_request, repository)
        elif action == 'closed':
            await self.notify_pull_request_closed(pull_request, repository)
            
    async def handle_pull_request_review_event(self, payload):
        """Pull Request レビューイベントの処理"""
        action = payload['action']
        review = payload['review']
        pull_request = payload['pull_request']
        repository = payload['repository']
        
        if action == 'submitted':
            await self.notify_pull_request_review(review, pull_request, repository)
            
    async def handle_pull_request_review_comment_event(self, payload):
        """Pull Request レビューコメントイベントの処理"""
        action = payload['action']
        comment = payload['comment']
        pull_request = payload['pull_request']
        repository = payload['repository']
        
        if action == 'created':
            await self.notify_pull_request_review_comment(comment, pull_request, repository)
    
    async def notify_issue_created(self, issue, repository):
        """Issue作成通知"""
        channel_id = self.channel_mappings.get(repository['name'])
        if not channel_id:
            return
            
        channel = self.client.get_channel(channel_id)
        if not channel:
            return
            
        embed = discord.Embed(
            title=f"📝 Issue Created: #{issue['number']}",
            description=format_github_content(issue['title']),
            url=issue['html_url'],
            color=0x28a745
        )
        embed.add_field(name="Author", value=self.convert_github_mention(issue['user']['login']), inline=True)
        embed.add_field(name="Repository", value=repository['name'], inline=True)
        
        if issue['body']:
            embed.add_field(name="Description", value=format_github_content(issue['body'], 500), inline=False)
            
        message = await channel.send(embed=embed)
        
        # スレッドを作成
        thread_name = f"Issue #{issue['number']}: {issue['title'][:50]}"
        thread = await message.create_thread(name=thread_name)
        
        # 永続化
        self.thread_mappings[issue['html_url']] = thread.id
        self.storage.set_thread_mapping(issue['html_url'], thread.id)
        
    async def notify_issue_comment(self, comment, issue, repository):
        """Issue コメント通知"""
        thread_id = self.thread_mappings.get(issue['html_url'])
        if not thread_id:
            return
            
        thread = self.client.get_channel(thread_id)
        if not thread:
            return
            
        embed = discord.Embed(
            title=f"💬 New Comment on Issue #{issue['number']}",
            description=comment['body'][:1000] + "..." if len(comment['body']) > 1000 else comment['body'],
            url=comment['html_url'],
            color=0x0366d6
        )
        embed.add_field(name="Author", value=self.convert_github_mention(comment['user']['login']), inline=True)
        
        await thread.send(embed=embed)
        
    async def notify_pull_request_created(self, pull_request, repository):
        """Pull Request作成通知"""
        channel_id = self.channel_mappings.get(repository['name'])
        if not channel_id:
            return
            
        channel = self.client.get_channel(channel_id)
        if not channel:
            return
            
        embed = discord.Embed(
            title=f"🔄 Pull Request Created: #{pull_request['number']}",
            description=format_github_content(pull_request['title']),
            url=pull_request['html_url'],
            color=0x28a745
        )
        embed.add_field(name="Author", value=self.convert_github_mention(pull_request['user']['login']), inline=True)
        embed.add_field(name="Repository", value=repository['name'], inline=True)
        embed.add_field(name="Base Branch", value=pull_request['base']['ref'], inline=True)
        embed.add_field(name="Head Branch", value=pull_request['head']['ref'], inline=True)
        
        if pull_request['body']:
            embed.add_field(name="Description", value=format_github_content(pull_request['body'], 500), inline=False)
            
        message = await channel.send(embed=embed)
        
        # スレッドを作成
        thread_name = f"PR #{pull_request['number']}: {pull_request['title'][:50]}"
        thread = await message.create_thread(name=thread_name)
        
        # 永続化
        self.thread_mappings[pull_request['html_url']] = thread.id
        self.storage.set_thread_mapping(pull_request['html_url'], thread.id)
        
    async def notify_pull_request_closed(self, pull_request, repository):
        """Pull Request終了通知"""
        thread_id = self.thread_mappings.get(pull_request['html_url'])
        if not thread_id:
            return
            
        thread = self.client.get_channel(thread_id)
        if not thread:
            return
            
        status = "merged" if pull_request['merged'] else "closed"
        color = 0x6f42c1 if pull_request['merged'] else 0xd73a49
        
        embed = discord.Embed(
            title=f"🔄 Pull Request {status.title()}: #{pull_request['number']}",
            description=pull_request['title'],
            url=pull_request['html_url'],
            color=color
        )
        
        await thread.send(embed=embed)
        
    async def notify_pull_request_review(self, review, pull_request, repository):
        """Pull Request レビュー通知"""
        thread_id = self.thread_mappings.get(pull_request['html_url'])
        if not thread_id:
            return
            
        thread = self.client.get_channel(thread_id)
        if not thread:
            return
            
        state_emoji = {
            'approved': '✅',
            'changes_requested': '❌',
            'commented': '💬'
        }
        
        embed = discord.Embed(
            title=f"{state_emoji.get(review['state'], '💬')} Review on PR #{pull_request['number']}",
            description=review['body'] if review['body'] else f"Review state: {review['state']}",
            url=review['html_url'],
            color=0x0366d6
        )
        embed.add_field(name="Reviewer", value=self.convert_github_mention(review['user']['login']), inline=True)
        
        await thread.send(embed=embed)
        
    async def notify_pull_request_review_comment(self, comment, pull_request, repository):
        """Pull Request レビューコメント通知"""
        thread_id = self.thread_mappings.get(pull_request['html_url'])
        if not thread_id:
            return
            
        thread = self.client.get_channel(thread_id)
        if not thread:
            return
            
        embed = discord.Embed(
            title=f"💬 Review Comment on PR #{pull_request['number']}",
            description=comment['body'][:1000] + "..." if len(comment['body']) > 1000 else comment['body'],
            url=comment['html_url'],
            color=0x0366d6
        )
        embed.add_field(name="Author", value=self.convert_github_mention(comment['user']['login']), inline=True)
        
        await thread.send(embed=embed)
    
    def convert_github_mention(self, github_username: str) -> str:
        """GitHubユーザー名をDiscordメンションに変換"""
        discord_user_id = self.user_mappings.get(github_username)
        if discord_user_id:
            return f"<@{discord_user_id}>"
        return f"@{github_username}"
        
    def convert_discord_mention(self, discord_user_id: str) -> str:
        """DiscordユーザーIDをGitHubユーザー名に変換"""
        for github_username, user_id in self.user_mappings.items():
            if user_id == discord_user_id:
                return f"@{github_username}"
        return f"<@{discord_user_id}>"
    
    async def post_github_comment(self, repo_name: str, issue_number: int, comment_body: str):
        """GitHubにコメントを投稿"""
        if not self.github:
            logger.error("GitHub token not configured")
            raise ConfigurationError("GitHub token not configured")
            
        try:
            repo = self.github.get_repo(f"{config.GITHUB_ORGANIZATION}/{repo_name}")
            issue = repo.get_issue(issue_number)
            issue.create_comment(comment_body)
            logger.info(f"Successfully posted comment to {repo_name}#{issue_number}")
            return True
        except Exception as e:
            error_msg = f"Error posting GitHub comment to {repo_name}#{issue_number}: {e}"
            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from e
    
    async def handle_discord_message(self, message: discord.Message):
        """Discordメッセージの処理（スレッド内でのbotメンション）"""
        if not message.author.bot and self.client.user in message.mentions:
            # スレッドかどうかチェック
            if isinstance(message.channel, discord.Thread):
                # GitHubのissue/PRスレッドかどうかチェック
                github_url = None
                for url, thread_id in self.thread_mappings.items():
                    if thread_id == message.channel.id:
                        github_url = url
                        break
                        
                if github_url:
                    await self.process_discord_to_github_comment(message, github_url)
                    
    async def process_discord_to_github_comment(self, message: discord.Message, github_url: str):
        """DiscordメッセージをGitHubコメントに変換"""
        try:
            # URLからリポジトリ名とissue/PR番号を抽出
            repo_name, issue_number, issue_type = extract_repo_and_issue_from_url(github_url)
            
            # メンションを変換
            comment_body = message.content
            # Discord メンションをGitHub メンションに変換
            for mention in message.mentions:
                discord_id = str(mention.id)
                github_mention = self.convert_discord_mention(discord_id)
                comment_body = comment_body.replace(f"<@{mention.id}>", github_mention)
            
            # botメンションを削除
            comment_body = comment_body.replace(f"<@{self.client.user.id}>", "").strip()
            
            # 投稿者情報を追加
            comment_body = f"*From Discord user: {message.author.display_name}*\n\n{comment_body}"
            
            # GitHubにコメント投稿
            success = await self.post_github_comment(repo_name, issue_number, comment_body)
            
            if success:
                await message.add_reaction("✅")
                logger.info(f"Successfully posted comment to GitHub: {github_url}")
            else:
                await message.add_reaction("❌")
                logger.error(f"Failed to post comment to GitHub: {github_url}")
                
        except Exception as e:
            logger.error(f"Error processing Discord to GitHub comment: {e}")
            await message.add_reaction("❌")

# グローバルインスタンス
comment_connector = None

async def setup(tree: discord.app_commands.CommandTree, client: discord.Client):
    """Comment Connectorモジュールのセットアップ"""
    global comment_connector
    comment_connector = CommentConnector(client)
    
    # WebHookサーバー起動
    asyncio.create_task(comment_connector.setup_webhook_server())
    
    # Discordメッセージイベントハンドラー登録
    @client.event
    async def on_message(message):
        await comment_connector.handle_discord_message(message)
    
    # ユーザー紐づけコマンド
    @tree.command(name="link_user", description="GitHubユーザーとDiscordユーザーを紐づけ")
    async def link_user(interaction: discord.Interaction, github_username: str, discord_user: discord.Member = None):
        if discord_user is None:
            discord_user = interaction.user
            
        comment_connector.user_mappings[github_username] = str(discord_user.id)
        comment_connector.storage.set_user_mapping(github_username, str(discord_user.id))
        await interaction.response.send_message(f"✅ GitHubユーザー `{github_username}` とDiscordユーザー {discord_user.mention} を紐づけました")
    
    # チャンネル紐づけコマンド
    @tree.command(name="link_channel", description="GitHubリポジトリとDiscordチャンネルを紐づけ")
    async def link_channel(interaction: discord.Interaction, repo_name: str, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
            
        comment_connector.channel_mappings[repo_name] = channel.id
        comment_connector.storage.set_channel_mapping(repo_name, channel.id)
        await interaction.response.send_message(f"✅ GitHubリポジトリ `{repo_name}` とDiscordチャンネル {channel.mention} を紐づけました")
    
    # 設定確認コマンド
    @tree.command(name="connector_status", description="Comment Connectorの設定状況を確認")
    async def connector_status(interaction: discord.Interaction):
        embed = discord.Embed(title="Comment Connector Status", color=0x0366d6)
        
        user_mappings_text = "\n".join([f"`{gh}` → <@{dc}>" for gh, dc in comment_connector.user_mappings.items()]) or "なし"
        embed.add_field(name="ユーザー紐づけ", value=user_mappings_text[:1000], inline=False)
        
        channel_mappings_text = "\n".join([f"`{repo}` → <#{ch}>" for repo, ch in comment_connector.channel_mappings.items()]) or "なし"
        embed.add_field(name="チャンネル紐づけ", value=channel_mappings_text[:1000], inline=False)
        
        thread_count = len(comment_connector.thread_mappings)
        embed.add_field(name="アクティブスレッド数", value=str(thread_count), inline=True)
        
        github_status = "✅ 接続済み" if comment_connector.github else "❌ 未設定"
        embed.add_field(name="GitHub接続", value=github_status, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    # ユーザー紐づけ解除コマンド
    @tree.command(name="unlink_user", description="GitHubユーザーとDiscordユーザーの紐づけを解除")
    async def unlink_user(interaction: discord.Interaction, github_username: str):
        if github_username in comment_connector.user_mappings:
            del comment_connector.user_mappings[github_username]
            comment_connector.storage.save_data()
            await interaction.response.send_message(f"✅ GitHubユーザー `{github_username}` の紐づけを解除しました")
        else:
            await interaction.response.send_message(f"❌ GitHubユーザー `{github_username}` は紐づけされていません")
    
    logger.info("Comment Connector module setup completed")
