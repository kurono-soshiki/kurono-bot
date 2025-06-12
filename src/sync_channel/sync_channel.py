import discord
from discord.ext import commands
import asyncio
from typing import List, Dict, Optional
from github import Github
import logging
import config
from .utils import validate_config, get_channel_name_from_repo, format_repo_description

logger = logging.getLogger(__name__)

class SyncChannel:
    """GitHubリポジトリとDiscordチャンネルを同期するクラス"""
    
    def __init__(self, client: discord.Client):
        self.client = client
        self.github = Github(config.GITHUB_TOKEN) if config.GITHUB_TOKEN else None
        self.organization_name = config.GITHUB_ORGANIZATION
        self.guild_id = config.DISCORD_GUILD_ID
        self.category_id = config.DISCORD_CATEGORY_ID
        
        # 設定の検証
        if not validate_config():
            logger.error("設定が不完全です")
        
        if not self.github:
            logger.warning("GitHub token not found. GitHub integration will be disabled.")
    
    async def get_github_repositories(self) -> List[Dict]:
        """GitHubのorganizationからリポジトリ一覧を取得"""
        if not self.github:
            logger.error("GitHub client not initialized")
            return []
        
        try:
            org = self.github.get_organization(self.organization_name)
            repos = []
            
            for repo in org.get_repos():
                if not repo.archived:  # アーカイブされていないリポジトリのみ
                    repos.append({
                        'name': repo.name,
                        'description': repo.description or "説明なし",
                        'url': repo.html_url,
                        'created_at': repo.created_at,
                        'updated_at': repo.updated_at,
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'forks': repo.forks_count,
                        'private': repo.private
                    })
            
            logger.info(f"取得したリポジトリ数: {len(repos)}")
            return repos
            
        except Exception as e:
            logger.error(f"GitHubリポジトリの取得に失敗: {e}")
            return []
    
    async def get_discord_channels(self) -> List[discord.TextChannel]:
        """指定されたカテゴリ内のDiscordチャンネル一覧を取得"""
        guild = self.client.get_guild(self.guild_id)
        if not guild:
            logger.error(f"Guild {self.guild_id} not found")
            return []
        
        category = guild.get_channel(self.category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            logger.error(f"Category {self.category_id} not found or not a category")
            return []
        
        return [ch for ch in category.channels if isinstance(ch, discord.TextChannel)]
    
    async def create_channel(self, repo_info: Dict, category: discord.CategoryChannel) -> Optional[discord.TextChannel]:
        """リポジトリに対応するDiscordチャンネルを作成"""
        try:
            # チャンネル名はリポジトリ名をDiscord用に変換
            channel_name = get_channel_name_from_repo(repo_info['name'])
            
            # チャンネルのトピックを設定
            topic = f"🔗 {repo_info['url']}\n📝 {format_repo_description(repo_info['description'], 200)}"
            if repo_info['language']:
                topic += f"\n💻 {repo_info['language']}"
            
            channel = await category.create_text_channel(
                name=channel_name,
                topic=topic[:1024],  # Discordのトピック文字数制限
                reason=f"GitHub repository sync: {repo_info['name']}"
            )
            
            logger.info(f"チャンネル作成: {channel.name}")
            return channel
            
        except Exception as e:
            logger.error(f"チャンネル作成に失敗 ({repo_info['name']}): {e}")
            return None
    
    async def update_channel(self, channel: discord.TextChannel, repo_info: Dict):
        """既存のチャンネル情報を更新"""
        try:
            # トピックを更新
            topic = f"🔗 {repo_info['url']}\n📝 {repo_info['description']}"
            if repo_info['language']:
                topic += f"\n💻 {repo_info['language']}"
            
            await channel.edit(
                topic=topic[:1024],
                reason=f"GitHub repository sync update: {repo_info['name']}"
            )
            
            logger.info(f"チャンネル更新: {channel.name}")
            
        except Exception as e:
            logger.error(f"チャンネル更新に失敗 ({channel.name}): {e}")
    
    async def sync_repositories(self) -> Dict[str, int]:
        """リポジトリとチャンネルの同期を実行"""
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        # GitHubリポジトリを取得
        repos = await self.get_github_repositories()
        if not repos:
            logger.warning("同期対象のリポジトリが見つかりません")
            return stats
        
        # Discordのギルドとカテゴリを取得
        guild = self.client.get_guild(self.guild_id)
        if not guild:
            logger.error(f"Guild {self.guild_id} not found")
            return stats
        
        category = guild.get_channel(self.category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            logger.error(f"Category {self.category_id} not found or not a category")
            return stats
        
        # 既存のチャンネル一覧を取得
        existing_channels = await self.get_discord_channels()
        existing_channel_names = {ch.name: ch for ch in existing_channels}
        
        # リポジトリごとに処理
        for repo in repos:
            try:
                channel_name = repo['name'].lower().replace('_', '-').replace(' ', '-')
                
                if channel_name in existing_channel_names:
                    # 既存チャンネルを更新
                    await self.update_channel(existing_channel_names[channel_name], repo)
                    stats['updated'] += 1
                else:
                    # 新しいチャンネルを作成
                    created_channel = await self.create_channel(repo, category)
                    if created_channel:
                        stats['created'] += 1
                        
                        # 作成メッセージを送信
                        embed = discord.Embed(
                            title=f"📁 {repo['name']}",
                            description=repo['description'],
                            color=0x00ff00,
                            url=repo['url']
                        )
                        embed.add_field(name="言語", value=repo['language'] or "不明", inline=True)
                        embed.add_field(name="⭐ スター", value=repo['stars'], inline=True)
                        embed.add_field(name="🍴 フォーク", value=repo['forks'], inline=True)
                        embed.add_field(name="作成日", value=repo['created_at'].strftime('%Y-%m-%d'), inline=True)
                        embed.add_field(name="更新日", value=repo['updated_at'].strftime('%Y-%m-%d'), inline=True)
                        embed.add_field(name="プライベート", value="Yes" if repo['private'] else "No", inline=True)
                        
                        await created_channel.send(embed=embed)
                    else:
                        stats['errors'] += 1
                
                # レート制限対策で少し待機
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"リポジトリ処理中にエラー ({repo['name']}): {e}")
                stats['errors'] += 1
        
        logger.info(f"同期完了 - 作成: {stats['created']}, 更新: {stats['updated']}, エラー: {stats['errors']}")
        return stats


async def setup(tree: discord.app_commands.CommandTree, client: discord.Client):
    """モジュールのセットアップ（スラッシュコマンドの登録）"""
    sync_channel = SyncChannel(client)
    
    @tree.command(name="sync-repos", description="GitHubリポジトリとDiscordチャンネルを同期します")
    async def sync_repos_command(interaction: discord.Interaction):
        # 権限チェック（管理者権限が必要）
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ このコマンドを実行するには管理者権限が必要です。",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            stats = await sync_channel.sync_repositories()
            
            embed = discord.Embed(
                title="🔄 リポジトリ同期完了",
                color=0x00ff00
            )
            embed.add_field(name="作成", value=f"{stats['created']} チャンネル", inline=True)
            embed.add_field(name="更新", value=f"{stats['updated']} チャンネル", inline=True)
            embed.add_field(name="エラー", value=f"{stats['errors']} 件", inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"同期コマンド実行中にエラー: {e}")
            await interaction.followup.send(
                f"❌ 同期中にエラーが発生しました: {str(e)}",
                ephemeral=True
            )
    
    @tree.command(name="list-repos", description="GitHubリポジトリ一覧を表示します")
    async def list_repos_command(interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            repos = await sync_channel.get_github_repositories()
            
            if not repos:
                await interaction.followup.send("❌ リポジトリが見つかりませんでした。")
                return
            
            embed = discord.Embed(
                title=f"📚 {config.GITHUB_ORGANIZATION} のリポジトリ一覧",
                color=0x0099ff
            )
            
            # リポジトリ情報を10個ずつ表示
            repo_list = []
            for repo in repos[:20]:  # 最大20個まで表示
                status = "🔒" if repo['private'] else "🌐"
                repo_list.append(
                    f"{status} **[{repo['name']}]({repo['url']})**\n"
                    f"   📝 {repo['description'][:50]}{'...' if len(repo['description']) > 50 else ''}\n"
                    f"   💻 {repo['language'] or '不明'} | ⭐ {repo['stars']} | 🍴 {repo['forks']}"
                )
            
            embed.description = "\n\n".join(repo_list)
            
            if len(repos) > 20:
                embed.set_footer(text=f"+ {len(repos) - 20} 個のリポジトリがあります")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"リポジトリ一覧取得中にエラー: {e}")
            await interaction.followup.send(
                f"❌ リポジトリ一覧の取得中にエラーが発生しました: {str(e)}",
                ephemeral=True
            )