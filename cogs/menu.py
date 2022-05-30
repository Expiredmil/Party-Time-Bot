from discord.ext import commands, tasks
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
        msg += f'🎱 : `{prefix}eb` - 8ball\n'
        msg += f'⚪ : `{prefix}ch` - Checkers\n'
        msg += f'❌ : `{prefix}o` - Tic Tac Toe\n'
        msg += f'🔢 : `{prefix}o` - Four in a row\n'
        message_menu = await ctx.channel.send(msg)
        await message_menu.add_reaction("🎱")
        await message_menu.add_reaction("⚪")
        await message_menu.add_reaction("❌")
        await message_menu.add_reaction("🔢")
        self.menu_sessions.append(MenuSession(ctx, self, message_menu))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user:
            return
        ctx = await self.client.get_context(reaction.message)
        ctx.author = user
        command = None
        if reaction.emoji == "🎱":
            command = self.client.get_command("eightball")
            self.command_sessions.append(command)
        elif reaction.emoji == "⚪":
            command = self.client.get_command("checkers")
            self.command_sessions.append(command)
        elif reaction.emoji == "❌":
            command =self.client.get_command("tic-tac-toe")
            self.command_sessions.append(command)
        if command != None:
            await ctx.invoke(command)
        return


def setup(client):
    client.add_cog(Menu(client))