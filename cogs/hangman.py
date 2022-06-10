from discord import User
from discord.ext import commands
import discord.embeds
import discord.file
import random
import os
from models import Members


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
        self._max_players = 5
        self.word = ""
        self.guessed_letters = []
        self.game_message = None
        self.game_started = False
        self.guesses = 7
        self.join_message = None
        self.context = None
        self.host = None
        self.embed = discord.Embed()

    # ~~~~~~~~~~~~~~~~~~~ Instructions ~~~~~~~~~~~~~~~~~~~ #

    async def instructions(self, ctx):
        prefix = await self.client.get_prefix(ctx)
        msg = "**Hang Man Help**\n"
        msg += "A game of hang man where other players guess a word/phrase.\n"
        msg += f"`{prefix}hm start : Start a game with a random word \n"
        msg += f"{prefix}hm start [phrase] : Start a game with the given word/phrase \n"
        msg += f"{prefix}hm gs [phrase/letter] : Guess a letter or the phrase \n"
        msg += f"{prefix}hm quit : Quit a running game`"
        return msg

    # ~~~~~~~~~~~~~~~~~~~ Editing Embed ~~~~~~~~~~~~~~~~~~~ #

    # Updates self.embed
    async def update_embed(self):
        self.embed.description = await self.layout_string()
        self.embed.set_field_at(0,
                                name="Guessed letters:",
                                value=self.guessed_string(),
                                inline=True)

    # Returns layout
    async def layout_string(self):
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
        return msg

    # Returns guessed letters
    def guessed_string(self):
        msg = ""
        for i in range(0, len(self.guessed_letters)):
            msg += " " + self.guessed_letters[i].upper()
        if msg == "":
            msg = "-"
        return msg

    # Prints embed
    async def print(self):
        guesses = str(self.guesses) + ".png"
        filepath = "common/hangman_stages/" + guesses
        file = discord.File(filepath, filename=guesses)
        if self.game_message != None:
            await self.game_message.delete()
        await self.update_embed()
        self.embed.set_image(url="attachment://" + guesses)
        self.game_message = await self.context.send(file=file, embed=self.embed)

    # ~~~~~~~~~~~~~~~~~~~ Guess Command Functions ~~~~~~~~~~~~~~~~~~~ #

    # Checks if the given string is equal to the word
    def chkguess(self, str_guess):
        if str_guess == self.word:
            return True
        else:
            return False

    # Checks if the given string is equal to the word
    def letterguess(self):
        for i in range(1, len(self.word)):
            if self.word[i] not in self.guessed_letters:
                return False
        return True

    # Wrong guess is input
    async def wrong_guess(self, ctx):
        self.guesses -= 1
        if self.guesses != 0:
            await ctx.send("Wrong guess! You have " + str(self.guesses) + " tries left.")
            await self.print()
        else:
            msg = "Game Over!\n"
            msg += "The word was: " + self.word
            await ctx.send(msg)
            self.game_started = False

    # ~~~~~~~~~~~~~~~~~~~ Game Start/End ~~~~~~~~~~~~~~~~~~~ #

    # Concatenate a group of args | Used to combine the host's args into a string to guess
    def concatenate(self, args):
        conc = ""
        for i in args:
            conc = conc + " " + i
        return conc.lower()

    # Initialise game
    async def init_game(self, ctx, args):
        self.quit_game()
        self.context = ctx
        self.players.append(ctx.message.author.id)
        self.host = ctx.message.author
        self.word = self.concatenate(args)
        self.game_started = True
        self.embed = discord.Embed(title="Hang Man",
                                   description=await self.layout_string(),
                                   color=0xFF5733)
        self.embed.add_field(name="Guessed letters:",
                             value="-",
                             inline=True)
        await self.joining(ctx)
        await self.print()

    # Quitting game
    def quit_game(self):
        self.players = []
        self.word = ""
        self.guessed_letters = []
        self.game_message = None
        self.game_started = False
        self.guesses = 7
        self.join_message = None
        self.context = None
        self.host = None
        self.embed = discord.Embed()

    # Game won
    async def win(self, ctx):
        for i in range(1, len(self.word)):
            if self.word[i] not in self.guessed_letters:
                self.guessed_letters.append(self.word[i])
        await self.print()
        # Updates database {
        player_id = ctx.message.author.id
        member = await Members.filter(member_id=player_id).get_or_none()
        cur_bal = member.balance
        await Members.filter(member_id=player_id).update(balance=cur_bal + 5)
        # }
        msg = "Victory Royale!\n"
        msg += ctx.message.author.name + " has won 5 tokens!"
        await ctx.send(msg)
        self.quit_game()

    # ~~~~~~~~~~~~~~~~~~~ Player Handling ~~~~~~~~~~~~~~~~~~~ #

    # Prints message for people to join through
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
            await self.context.send(user_name + " has joined the battle!")
        else:
            await self.context.send("Game is full")

    # ~~~~~~~~~~~~~~~~~~~ Command Logic ~~~~~~~~~~~~~~~~~~~ #

    # Called when user wants to quit a game
    async def start_comm(self, ctx, args):
        if not self.game_started:
            await ctx.message.delete()
            await self.init_game(ctx, args)
        else:
            await ctx.send("Another game is currently running")

    # Called when the start command has no arguments | A game is started using a random word from wordlist.txt
    async def wordlist_comm(self, ctx):
        if not self.game_started:
            await ctx.message.delete()
            with open(os.path.join(os.path.dirname(__file__), '../common/wordlist.txt'),
                      'r') as f:  # List with possible words in a separate file
                wordlist = [line.strip() for line in f]
                args = [random.choice(wordlist).lower()]
            await self.init_game(ctx, args)
        else:
            await ctx.send("Another game is currently running")

    # Called when user wants to quit a game
    async def quit_comm(self, ctx):
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

    # Called when a user wants to guess a letter/phrase
    async def guess_comm(self, ctx, args):
        str_guess = self.concatenate(args)
        if len(str_guess) == 2:
            str_guess = str_guess[1]
            if str_guess in self.word and str_guess not in self.guessed_letters:
                self.guessed_letters.append(str_guess)
                await ctx.send("Correct!")
                if self.letterguess():
                    await self.win(ctx)
                    return
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

    # ~~~~~~~~~~~~~~~~~~~ Discord Commands ~~~~~~~~~~~~~~~~~~~ #

    @commands.group(aliases=['hm'], case_insensitive=True, invoke_without_command=True)
    async def hangman(self, ctx):
        await ctx.send(await self.instructions(ctx))

    @hangman.command(case_insensitive=True, invoke_without_command=True)
    async def start(self, ctx, *args):
        if not args:
            await self.wordlist_comm(ctx)
        else:
            await self.start_comm(ctx, args)

    @hangman.command(aliases=['q'], case_insensitive=True, invoke_without_command=True)
    async def quit(self, ctx):
        await self.quit_comm(ctx)

    @hangman.command(aliases=["gs"], case_insensitive=True)
    async def guess(self, ctx, *args):
        await self.guess_comm(ctx, args)

    # Handles reaction
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.client.user:
            return
        if self.join_message != None and reaction.message.id == self.join_message.id and reaction.emoji == "✅":
            ctx = await self.client.get_context(reaction.message)
            ctx.author = user
            if ctx.author.id not in self.players:
                await self.add_player(ctx)


def setup(client):
    client.add_cog(HangManGame(client))
