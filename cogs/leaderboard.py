from discord.ext import commands

from models import Members


class Leaderboard(commands.Cog):
    def __int__(self, client):
        self.client = client

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        msg = f'{await Members.all().order_by("-balance").values_list("identity","balance")}'
        temp = "'"
        temp1 = "' "
        #msg.replace(')', ') \n ')
        await ctx.send(msg.replace(')', ' \n').replace('[', 'Here is the leaderboard: \n ').replace(']', '').replace(',', '').replace('(','    ').replace(temp1,', with a score of: ').replace(temp, ''))


def setup(client):
    client.add_cog(Leaderboard(client))
