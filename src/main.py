import discord
import config

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# Future module imports would go here:
# from yomiage import yomiage as yomiage_bot
# from umigame import umigame as umigame_bot
from src.sync_channel import sync_channel
from src.comment_connecter import comment_connecter
# yomiage_bot.setup(tree, client)
# umigame_bot.setup(tree, client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
    # モジュールのセットアップ
    await sync_channel.setup(tree, client)
    await comment_connecter.setup(tree, client)
    
    # グローバルコマンドの同期
    await tree.sync()
    print("グローバルスラッシュコマンドを同期しました")
    # ギルドごとのコマンドの同期
    for guild in client.guilds:
        await tree.sync(guild=discord.Object(id=guild.id))
        print(f"スラッシュコマンドをギルド {guild.id} に同期しました")

if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        client.run(config.DISCORD_TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables")
        print("Please copy .env.sample to .env and set your Discord bot token")