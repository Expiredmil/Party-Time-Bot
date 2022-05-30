import discord
import os
import json
from discord.ext import commands, tasks
from dotenv import load_dotenv, find_dotenv
from itertools import cycle

load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')

# Open json file
with open("./config.json") as config_file:
    config = json.load(config_file)

client = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())

prefix = config['prefix']
status = cycle(['[help', 'You!'])


# Running confirmation
@client.event
async def on_ready():
    change_status.start()
    print("Party-Time-Bot running")


@client.event
async def on_message(message):
    msg = message
    if msg.content.startswith(prefix+'hello'):
        await msg.channel.send(f'Hello {msg.author.name}')
    await client.process_commands(msg)


@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=next(status)), status=discord.Status.idle)


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
    await ctx.send(f'pong {round(client.latency * 1000)}ms')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        file = filename[:-3]
        client.load_extension(f'cogs.{file}')
        print(f'Cog loaded {file}')

client.run(TOKEN)
