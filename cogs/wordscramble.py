import asyncio
import os
import random
import time

import discord.embeds
from discord.ext import commands
from discord_ui import Button


class WordScramble(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._game_name = "wordscramble"
        self._game_command = f"{self.client.command_prefix}wordscramble"
        self.help_message = ""
        self.answer = ""
        self.shuffledWord = ""
        self.authorid = 0
        self.authorname = ""
        self.started = False
        self.guesses = 0
        self.timer = time.time()
        self.noShuffles = 0
        self.embed = discord.Embed()
        self.quitButton = Button(label="Quit", custom_id="quit", color="blurple", emoji="❌")
        self.shuffleButton = Button(label="Shuffle", custom_id="shuffle", color="green", emoji="🔄")
        self.restartButton = Button(label="Play again", custom_id="play_again", color="blurple", emoji="🔁")
        self.ctxInit = 0

    def instructions(self):

        msg = f"Start a game by typing `{self.client.command_prefix}ws`.\n"
        msg += f"Guess the scrambled word by typing `{self.client.command_prefix}ws [guess]`.\n"
        msg += f"Shuffle the letters from the word by typing `{self.client.command_prefix}ws shuffle`.\n"
        msg += f"Show the word again by typing `{self.client.command_prefix}ws repeat`.\n"
        msg += f"Quit an existing game by typing `{self.client.command_prefix}ws quit`.\n"
        msg += f"Open this help menu by typing `{self.client.command_prefix}ws help`.\n"
        msg += "Type `prefix?` for necessary prefix\n"
        return msg

    async def send_embed(self, ctx):
        try:
            msg = await ctx.send(embed=self.embed, components=[self.shuffleButton, self.quitButton])
            btn = await msg.wait_for("button", self.client)
            await btn.respond()
            if await self.game_started(ctx, btn.author.id):
                if btn.custom_id == "quit":
                    await self.quit_command(ctx)
                elif btn.custom_id == "shuffle":
                    await self.shuffleCommand(ctx)
        except asyncio.TimeoutError:
            return

    async def end_game(self, ctx):
        self.started = False
        elapsed_time = time.time() - self.timer
        self.embed.set_field_at(1, name="Guesses done:", value=str(self.guesses), inline=True)
        self.embed.add_field(name="Time it took:", value=str(round(elapsed_time)) + " seconds", inline=True)
        msg = await ctx.send(embed=self.embed, components=[self.restartButton])
        try:
            btn = await msg.wait_for("button", self.client, timeout=20)
            await btn.respond()
            ctx.author = btn.author
            await self.wordscramble(self.ctxInit)
        except asyncio.TimeoutError:
            return

    async def game_started(self, ctx, authorid):
        if not self.started:
            await ctx.send("There is no game running at the moment.")
        elif self.authorid is not ctx.author.id is not authorid:
            await ctx.send(
                self.authorname + " is currently playing the game. Please wait until their game is finished.")
        return self.started and (self.authorid is ctx.author.id is authorid)

    async def check_answer(self, ctx, guess):
        self.guesses += 1
        if self.answer == guess:
            self.embed.description = "Congratulations, the word was indeed `" + self.answer + "`."
            await self.end_game(ctx)
        else:
            self.embed.set_field_at(1, name="Guesses done:", value=str(self.guesses), inline=True)
            await self.send_embed(ctx)
        return self.answer == guess

    async def shuffle_word(self):
        responses = list(self.answer)
        random.shuffle(responses)
        self.shuffledWord = ""
        for x in responses:
            self.shuffledWord += x
        self.embed.description = "`" + self.shuffledWord + "`"

    async def shuffleCommand(self, ctx):
        if await self.game_started(ctx, ctx.author.id):
            if self.noShuffles == 0:
                await self.send_embed(ctx)
                return
            self.noShuffles -= 1
            await self.shuffle_word()
            self.embed.set_field_at(0, name="Shuffles left:", value=str(self.noShuffles))
            await self.send_embed(ctx)

    async def quit_command(self, ctx):
        if await self.game_started(ctx, ctx.author.id):
            self.embed.description = "Better luck next time, the word was `" + self.answer + "`."
            await self.end_game(ctx)

    async def start_game(self, ctx, *args):
        await ctx.send(f"Guess the scrambled word by typing `{self.client.command_prefix}ws [guess]`.\n")
        with open(os.path.join(os.path.dirname(__file__), '../common/wordlist.txt'),
                  'r') as f:  # List with possible words in a separate file
            word_list = [line.strip() for line in f]
            self.answer = random.choice(word_list).lower()
        self.authorid = ctx.author.id
        self.authorname = ctx.author.name
        self.started = True
        self.timer = time.time()
        self.guesses = 0
        self.noShuffles = 2
        self.ctxInit = ctx
        await self.shuffle_word()
        self.embed = discord.Embed(title="Word Scramble",
                                   description="`" + self.shuffledWord + "`",
                                   color=0xFF5733)
        self.embed.add_field(name="Shuffles left:",
                             value=str(self.noShuffles),
                             inline=True)
        self.embed.add_field(name="Guesses done:",
                             value=str(self.guesses),
                             inline=True)
        await self.send_embed(ctx)

    @commands.group(name='wordscramble', aliases=['ws'], invoke_without_command=True)
    async def wordscramble(self, ctx, *args):
        if not self.started:  # Creating a game
            await self.start_game(ctx, *args)
        else:  # Checking whether guessed word is the correct word
            if not await self.game_started(ctx, ctx.author.id):
                return
            elif not args:
                await ctx.send("Please enter your guess before starting a new game.")
            else:
                await self.check_answer(ctx, args[0].lower())
        return

    @wordscramble.command()
    async def shuffle(self, ctx):
        await self.shuffleCommand(ctx)

    @wordscramble.command(aliases=[])
    async def help(self, ctx):
        self.help_message = ctx.send(self.instructions())
        await self.help_message
        return

    @wordscramble.command()
    async def quit(self, ctx):
        await self.quit_command(ctx)

    @wordscramble.command()
    async def repeat(self, ctx):
        if await self.game_started(ctx, ctx.author.id):
            await self.send_embed(ctx)


def setup(client):
    client.add_cog(WordScramble(client))