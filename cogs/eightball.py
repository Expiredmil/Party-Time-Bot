from discord.ext import commands
from common.Game import Game
import random


def instructions():
    msg = "**Eight-ball Help**\n"
    msg += "The magic 8ball will tell your future, ask anything you want to him\n"
    msg += f"`eb ask [question]`: Ask 8ball by filling in the question.\n"
    return msg


class EightBall(Game):

    def __init__(self, client):
        self.client = client
        self._game_name = "8ball"
        self._game_command = f"{self.client.command_prefix}eightball"
        self.help_message = None

    # Game instructions

    @commands.group(name='eightball', aliases=['eb'], case_insensitive=True, invoke_without_command=True)
    async def eightball(self, ctx):
        self.help_message = ctx.send(instructions())
        await self.help_message

    @eightball.command(aliases=[""])
    async def ask(self, ctx, *, question):
        responses = ["It is certain.",
                     "It is decidedly so.",
                     "Without a doubt.",
                     "Yes - definitely.",
                     "You may rely on it.",
                     "As I see it, yes.",
                     "Most likely.",
                     "Outlook good.",
                     "Yes.",
                     "Signs point to yes.",
                     "Reply hazy, try again.",
                     "Ask again later.",
                     "Better not tell you now.",
                     "Cannot predict now.",
                     "Concentrate and ask again.",
                     "Don't count on it.",
                     "My reply is no.",
                     "My sources say no.",
                     "Outlook not so good.",
                     "Very doubtful."]
        await ctx.send(f'`Question: `{question}\n`Answer: `{random.choice(responses)}')


def setup(client):
    client.add_cog(EightBall(client))
