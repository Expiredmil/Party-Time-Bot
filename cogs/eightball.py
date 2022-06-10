from discord.ext import commands
import random



class EightBall(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._min_players = 1
        self._game_name = "8ball"
        self.help_message = None

    # Game instructions

    async def instructions(self, ctx):
        prefix = await self.client.get_prefix(ctx)
        msg = "**Eight-ball Help**\n"
        msg += "The magic 8ball will tell your future, ask anything you want to him\n"
        msg += f"`{prefix}eb ask [question]`: Ask 8ball by filling in the question.\n"
        return msg

    @commands.group(name='eightball', aliases=['eb', '8b'], case_insensitive=True, invoke_without_command=True)

    async def eightball(self, ctx):
        self.help_message = ctx.send(await self.instructions(ctx))
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
                     "Don't count on it.",
                     "My reply is no.",
                     "My sources say no.",
                     "Outlook not so good.",
                     "Very doubtful."]
        await ctx.send(f'`Question: `{question}\n`Answer: `{random.choice(responses)}')


def setup(client):
    client.add_cog(EightBall(client))
