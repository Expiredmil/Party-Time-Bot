import discord
from discord.ext import commands
from discord_ui import Button


class Menu(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.group(name='menu')
    async def menu(self, ctx):
        hangman = discord.utils.get(self.client.emojis, name='noosethink')
        prefix = await self.client.get_prefix(ctx)
        msg = '_*****Main menu*****_\n'
        msg += f'🎱 : `{prefix}eb` - 8ball\n'
        msg += f'⚪ : `{prefix}ch` - Checkers\n'
        msg += f'❌ : `{prefix}ttt` - Tic-Tac-Toe\n'
        msg += f'{hangman} : `{prefix}hm` - Hangman\n'
        msg += f'🇼 : `{prefix}ws` - Word scramble\n'

        message = await ctx.channel.send(msg, components=[
            [Button(emoji="🎱", custom_id="eb", color='grey'), Button(emoji="⚪", custom_id='ch', color='grey'),
             Button(emoji='❌', custom_id='ttt', color='grey'), Button(emoji=hangman, custom_id='hm', color='grey')],
            Button(emoji='🇼', custom_id="ws", color='grey')
        ])
        command = None
        btn = await message.wait_for("button", self.client, by=ctx.author)
        await btn.respond()
        if btn.custom_id == "eb":
            command = self.client.get_command(btn.custom_id)
        elif btn.custom_id == "ch":
            command = self.client.get_command(btn.custom_id)
        elif btn.custom_id == "ttt":
            command = self.client.get_command(btn.custom_id)
        elif btn.custom_id == "hm":
            command = self.client.get_command(btn.custom_id)
        elif btn.custom_id == "ws":
            command = self.client.get_command(btn.custom_id)
        if btn.custom_id is not None:
            await message.delete()
            await ctx.invoke(command)
        return


def setup(client):
    client.add_cog(Menu(client))
