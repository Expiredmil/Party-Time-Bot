import discord
import os
from discord.ext import commands
from tortoise import Tortoise
from models import GuildConfig
from dotenv import load_dotenv, find_dotenv
import constants

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')


async def get_prefix(bot: commands.Bot, message: discord.Message):
    config = await GuildConfig.filter(id=message.guild.id).get_or_none()
    return config.prefix if config else constants.DEFAULT_PREFIX


client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())


async def connect_db():
    await Tortoise.init(
        db_url=f"postgres://postgres:7s7m50jintgs@localhost:5432/testingbot",
        modules={'models': ["models"]}
    )
    await Tortoise.generate_schemas()


# Running confirmation
@client.event
async def on_ready():
    await connect_db()
    print("Party-Time-Bot running")


@client.event
async def on_message(message):
    msg = message
    if msg.content.startswith(".hello"):
        await msg.channel.send(f'Hello {msg.author.name}')

    await client.process_commands(msg)


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension}')
    print(f'Loaded cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension}')
    print(f'Unloaded cogs.{extension}')


@client.command()
async def reload(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            file = filename[:-3]
            client.unload_extension(f'cogs.{file}')
            await ctx.send(f'Cog unloaded {file}')
            print(f'Cog unloaded cogs.{file}')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            file = filename[:-3]
            client.load_extension(f'cogs.{file}')
            await ctx.send(f'Cog loaded {file}')
            print(f'Cog loaded cogs.{file}')
    await ctx.send('Cogs reloaded')


@client.command()
async def ping(ctx):
    await ctx.send('pong')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        file = filename[:-3]
        client.load_extension(f'cogs.{file}')
        print(f'Cog loaded {file}')

client.run(TOKEN)
