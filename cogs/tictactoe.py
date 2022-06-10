import discord
from discord.ext import commands
import random
import discord.embeds
from discord_ui import Button
import asyncio
from models import Members

player1 = ""
player2 = ""
turn = ""
gameOver = True
global count

board = []


def check_winner(winning_conditions, mark):
    global gameOver
    for condition in winning_conditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]


class TicTacToe(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.help_message = None
        self.prefix = '.'
        self.embed = discord.Embed()
        self.buttons = [Button()] * 9

    async def instructions(self, ctx):
        self.prefix = await self.client.get_prefix(ctx)
        msg = "**TicTacToe Help**\n"
        msg += "Play TicTacToe against an opponent or yourself!\n"
        msg += f"`{self.prefix}ttt start` - start a game\n"
        msg += f"Place a tile by clicking the corresponding button\n"
        return msg

    @staticmethod
    async def add_to_balance(player_id, x):
        member = await Members.filter(member_id=player_id).get_or_none()
        cur_bal = member.balance
        await Members.filter(member_id=player_id).update(balance=cur_bal + x)

    async def send_embed(self, ctx, player):
        try:
            if not gameOver:
                self.embed.description = "It is " + str(player) + "'s turn."
            for x in range(len(board)):
                match board[x]:
                    case ":white_large_square:":
                        self.buttons[x] = Button(color="grey", custom_id=str(x))
                    case "✖":
                        self.buttons[x] = Button(color="green", emoji="✖", custom_id=str(x))
                    case "⚪":
                        self.buttons[x] = Button(color="red", emoji="⚪", custom_id=str(x))
            msg = await ctx.send(embed=self.embed, components=[[self.buttons[0], self.buttons[1], self.buttons[2]],
                                                               [self.buttons[3], self.buttons[4], self.buttons[5]],
                                                               [self.buttons[6], self.buttons[7], self.buttons[8]]])
            btn = await msg.wait_for("button", self.client)
            await btn.respond()
            await self.place_command(ctx, int(btn.custom_id) + 1, btn.author, msg)
        except asyncio.TimeoutError:
            return

    async def place_command(self, ctx, pos: int, author, msg):
        global turn
        global player1
        global player2
        global board
        global count
        global gameOver

        if not gameOver:
            mark = ""
            if turn == author:
                if turn == player1 and count % 2 == 1:
                    mark = "✖"
                elif turn == player2 and count % 2 == 0:
                    mark = "⚪"
                if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                    board[pos - 1] = mark
                    count += 1
                    check_winner(winningConditions, mark)
                    if gameOver:
                        self.embed.description = str(turn) + " (" + mark + ") wins!"
                        await msg.delete()
                        turn_id = turn.id
                        await self.add_to_balance(turn_id, 5)
                        self.embed.description=str(turn) + " (" + mark + ") wins!"
                        await self.send_embed(ctx, turn)
                        return
                    elif count >= 9:
                        gameOver = True
                        self.embed.description = "It's a tie!"
                        await msg.delete()
                        await self.send_embed(ctx, turn)
                        return
                    # switch turns
                    if turn == player1:
                        turn = player2
                    elif turn == player2:
                        turn = player1
                    await msg.delete()
                else:
                    await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
            elif author == player1 or author == player2:
                await ctx.send("It is not your turn.")
            else:
                await ctx.send("You are not in this game.")
            await self.send_embed(ctx, turn)
        else:
            await ctx.send('Please start a new game using the ' + self.prefix + 'tictactoe command.')

    @commands.group(name='tictactoe', aliases=['ttt'], invoke_without_command=True)
    async def tictactoe(self, ctx):
        self.help_message = ctx.send(await self.instructions(ctx))
        await self.help_message

    @tictactoe.command()
    async def start(self, ctx):
        global count
        global player1
        global player2
        global turn
        global gameOver

        await ctx.message.delete()
        if gameOver:
            try:
                self.embed = discord.Embed(title="Tic Tac Toe", description="Waiting for opponent to join...",
                                           color=0xFF5733)
                msg = await ctx.send(embed=self.embed, components=[Button("Join", color="green")])
                btn = await msg.wait_for("button", self.client, timeout=10)
                await btn.respond()
                global board
                board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                         ":white_large_square:", ":white_large_square:", ":white_large_square:",
                         ":white_large_square:", ":white_large_square:", ":white_large_square:"]
                turn = ""
                gameOver = False
                count = 0

                player1 = ctx.author
                player2 = btn.author
                # determine who goes first
                turn = random.choice([player1, player2])
                await msg.delete()
                await self.send_embed(ctx, turn)
            except asyncio.TimeoutError:
                self.embed.description = "No opponent has joined."
                await ctx.send(embed=self.embed)
        else:
            await ctx.send("A game is already in progress! Finish it before starting a new one.")

    @tictactoe.command()
    async def quit(self, ctx):
        global gameOver
        global count
        if not gameOver:
            if ctx.author == player1 or ctx.author == player2:
                gameOver = True
                count = 0
                await ctx.send("Game has been ended.")
            else:
                await ctx.send("You cannot end a game that you are not in!")
        else:
            await ctx.send("There is no started game to end!")


def setup(client):
    client.add_cog(TicTacToe(client))
