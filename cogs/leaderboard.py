from discord.ext import commands
import discord
import typing
import constants
from models import GuildConfig, WelcomeConfig, LeaveConfig, Members
from server import client


class Leaderboard(commands.Cog):
    def __int__(self, client):
        self.client = client

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        await ctx.send(f'{await Members.all().order_by("-balance").values("balance")}')


def setup(client):
    client.add_cog(Leaderboard(client))
