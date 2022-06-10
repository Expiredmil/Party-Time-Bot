from discord import Message, User, Embed
from discord.ext import commands

from common.Game import Game
from common.Player import Player


# To-do list:
# - Add check for word to be censored by the player "|| ... ||"
# - Use embeds to display



class HangManPlayer(commands.Cog):
    class Player:
        def __int__(self, user: User):
            self.user = user

        def user(self):
            return self.user


class HangManGame(commands.Cog):
    def __init__(self, client):
        self.players = []
        self.client = client
        self._game_name = "Hang Man"
        self._game_command = f"{self.client.command_prefix}hangman"
        self._max_players = 5
        self.word = ""
        self.guessed_letters = []
        self.correct_letters = []
        self.game_started = False
        self.guesses = 7
        self.join_message = None
        self.context = None
        self.host = None

    async def instructions(self, ctx):
        prefix = await self.client.get_prefix(ctx)
        msg = "**Hang Man Help**\n"
        msg += "A game of hang man where other players guess a word/phrase.\n"
        msg += f"`{prefix}hm start [phrase]` : Start a game with the given word \n"
        msg += f"`{prefix}hm gs [phrase/letter]` : Guess a letter or the phrase \n"
        msg += f"`{prefix}hm quit` : Quit a running game\n"
        return msg

    # @property
    # def join_message(self):
    #     return self.join_message
    #
    # @join_message.setter
    # def join_message(self, message: Message):
    #     self.join_message = message

    # Guess check
    def chkguess(self, str_guess):
        if str_guess == self.word:
            return True
        else:
            return False

    # Guess check
    async def wrong_guess(self, ctx):
        self.guesses -= 1
        if self.guesses != 0:
            await ctx.send("Wrong guess! You have " + str(self.guesses) + " tries left.")
        else:
            msg = "Game Over\n"
            msg += "Word was: " + self.word
            await ctx.send(msg)
            self.game_started = False

    # Concatenate a group of args
    def concatenate(self, args):
        conc = ""
        for i in args:
            conc = conc + " " + i
        return conc.lower()

    # Print layout
    async def print(self):
        word_size = len(self.word)
        msg = "```"
        for i in range(1, word_size):
            if self.word[i] == " ":
                msg += "  "
            else:
                if self.word[i] in self.guessed_letters:
                    msg += self.word[i].upper() + " "
                else:
                    msg += "_ "
        msg += "```"
        await self.context.send(msg)

    # Initialise game
    async def init_game(self, ctx):
        self.game_started = True
        await self.joining(ctx)
        await self.print()

    # Quitting game
    def quit_game(self):
        self.players = []
        self.word = ""
        self.letters = []
        self.correct_letters = []
        self.game_started = False
        self.guesses = 7
        self.join_message = None
        self.context = None

    # Game won
    async def win(self, ctx):
        word_size = len(self.word)
        msg = "```"
        for i in range(1, word_size):
            if self.word[i] == " ":
                msg += "  "
            else:
                msg += self.word[i].upper() + " "
        msg += "```"
        await self.context.send(msg)
        await ctx.send("Victory Royale!")
        self.quit_game()

    # Join message
    async def joining(self, ctx):
        msg = "React to this message with ✅ to join the game"
        self.join_message = await ctx.send(msg)
        await self.join_message.add_reaction("✅")

    # Add a player to the game
    async def add_player(self, ctx):
        user_id = ctx.author.id
        if user_id not in self.players and self.players.count != self._max_players:
            self.players.append(user_id)
            user_name = ctx.author.name
            await self.context.send(user_name)
        else:
            await self.context.send("Unable to join the game")

    @commands.group(aliases=['hm'], case_insensitive=True, invoke_without_command=True)
    async def hangman(self, ctx):
        await ctx.send(await self.instructions(ctx))

    @hangman.command(case_insensitive=True, invoke_without_command=True)
    async def start(self, ctx, *args):
        self.context = ctx
        if not args:
            return
        if not self.game_started:
            await ctx.message.delete()
            self.players.append(ctx.message.author.id)
            self.host = ctx.message.author
            self.word = self.concatenate(args)
            await self.init_game(ctx)
        await ctx.send(self.word)

    @hangman.command(aliases=['q'], case_insensitive=True, invoke_without_command=True)
    async def quit(self, ctx):
        if ctx.message.author.id != self.host.id:
            if ctx.message.author.id in self.players:
                await ctx.send("Thanks for playing " + ctx.message.author.name)
                self.players.remove(ctx.message.author.id)
            return
        if self.game_started:
            msg = "The word was:" + self.word + "\n"
            msg += "Ending game..."
            await ctx.send(msg)
            self.quit_game()
        else:
            await ctx.send("No game currently in play")

    @hangman.command(aliases=["gs"], case_insensitive=True)
    async def guess(self, ctx, *args):
        str_guess = self.concatenate(args)
        await ctx.send("str_guess =" + str_guess)
        if len(str_guess) == 2:
            str_guess = str_guess[1]
            if str_guess in self.word and str_guess not in self.guessed_letters:
                self.correct_letters.append(str_guess)
            else:
                await self.wrong_guess(ctx)
            if str_guess not in self.guessed_letters:
                self.guessed_letters.append(str_guess)
            await self.print()
            return
        if not self.chkguess(str_guess):
            await self.wrong_guess(ctx)
        else:
            await self.win(ctx)

    # Handle reaction
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user:
            return
        if self.join_message is not None and reaction.message.id == self.join_message.id and reaction.emoji == "✅":
            ctx = await self.client.get_context(reaction.message)
            ctx.author = user
            if ctx.author.id not in self.players:
                await self.context.send("no way")
                await self.add_player(ctx)


def setup(client):
    client.add_cog(HangManGame(client))
