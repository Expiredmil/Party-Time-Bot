import discord_ui
from discord.ext import commands, tasks
from discord_ui import Button, LinkButton, UI
from server import prefix

class MenuSession:
    def __init__(self, ctx, parent, message_menu):
        self.__ctx = ctx
        self.__parent = parent
        self.__message_menu = message_menu

    @property
    def ctx(self):
        return self.__ctx

    @property
    def message_menu(self):
        return self.__message_menu

class Menu (commands.Cog):

    def __init__(self, client):
        self.client = client
        self.menu_sessions = []
        self.command_sessions = []

    @commands.group(name='menu')
    async def menu(self, ctx):
        msg = '_*****Main menu*****_\n'
        msg += f'🎱 : `{prefix}8b` - 8ball\n'
        msg += f'⚪ : `{prefix}ch` - Checkers\n'
        msg += f'❌ : `{prefix}o` - Checkers\n'
        msg += f'📮 : `{prefix}mb` - mail box\n'

        # message_menu = await ctx.channel.send(msg)
        # await message_menu.add_reaction("🎱")
        # await message_menu.add_reaction("⚪")
        # await message_menu.add_reaction("❌")
        # await message_menu.add_reaction("📮")
        # self.menu_sessions.append(MenuSession(ctx, self, message_menu))

        message = await ctx.channel.send("you", components=[
            [Button("press me", color="green"), LinkButton("https://discord.com", emoji="😁")],
            Button(custom_id="my_custom_id")
        ])
        try:
            btn = await message.wait_for("button", self.client, by=ctx.author, timeout=20)
            await btn.respond("you pressed `" + btn.content + "`")
        except TimeoutError:
            await message.delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user:
            return
        ctx = await self.client.get_context(reaction.message)
        ctx.author = user
        command = None
        if reaction.emoji == "🎱":
            command = self.client.get_command("eightball")
        elif reaction.emoji == "⚪":
            command = self.client.get_command("checkers")
        elif reaction.emoji == "❌":
            command =self.client.get_command("tic-tac-toe")
        if command != None:
            await ctx.invoke(command)
        return

def setup(client):
    client.add_cog(Menu(client))