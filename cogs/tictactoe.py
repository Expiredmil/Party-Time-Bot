import discord
from discord.ext import commands
import random
from common.Game import Game

player1 = ""
player2 = ""
turn = ""
gameOver = True
global count

board = []



def checkwinner(winningconditions, mark):
    global gameOver
    for condition in winningconditions:
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
        self.prefix = None

    async def instructions(self, ctx):
        self.prefix = await self.client.get_prefix(ctx)
        msg = "**TicTacToe Help**\n"
        msg += "Play TicTacToe against an opponent or yourself!\n"
        msg += f"`{self.prefix}ttt start @opponent` - start a game again opponent\n"
        msg += f"` {self.prefix}ttt place (1-9)` - during game place on tile\n"
        return msg

    @commands.group(name='tictactoe', aliases=['ttt'], invoke_without_command=True)
    async def tictactoe(self, ctx):
        await ctx.send(await self.instructions(ctx))

    @tictactoe.command()
    async def start(self, ctx, p2: discord.Member):
        global count
        global player1
        global player2
        global turn
        global gameOver

        if gameOver:
            global board
            board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:"]
            turn = ""
            gameOver = False
            count = 0

            player1 = ctx.author
            player2 = p2

            # print the board
            line = ""
            for x in range(len(board)):
                if x == 2 or x == 5 or x == 8:
                    line += " " + board[x]
                    await ctx.send(line)
                    line = ""
                else:
                    line += " " + board[x]

            # determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
            elif num == 2:
                turn = player2
                await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
        else:
            await ctx.send("A game is already in progress! Finish it before starting a new one.")

    @tictactoe.command()
    async def place(self, ctx, pos: int):
        global turn
        global player1
        global player2
        global board
        global count
        global gameOver

        if not gameOver:
            mark = ""
            if turn == ctx.author:
                if turn == player1 and count % 2 == 1:
                    mark = ":regional_indicator_x:"
                elif turn == player2 and count % 2 == 0:
                    mark = ":o2:"
                if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                    board[pos - 1] = mark
                    count += 1

                    # print the board
                    line = ""
                    for x in range(len(board)):
                        if x == 2 or x == 5 or x == 8:
                            line += " " + board[x]
                            await ctx.send(line)
                            line = ""
                        else:
                            line += " " + board[x]

                    checkwinner(winningConditions, mark)
                    print(count)
                    if gameOver:
                        await ctx.send(mark + " wins!")
                    elif count >= 9:
                        gameOver = True
                        await ctx.send("It's a tie!")

                    # switch turns
                    if turn == player1:
                        turn = player2
                    elif turn == player2:
                        turn = player1
                else:
                    await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
            elif ctx.author == player1 or ctx.author == player2:
                await ctx.send("It is not your turn.")
            else:
                await ctx.send("You are not in this game.")
        else:
            await ctx.send('Please start a new game using the '+ self.prefix +'tictactoe command.')

    @tictactoe.command()
    async def endgame(self, ctx):
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

    @tictactoe.error
    async def tictactoe_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please mention a opponent for this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please make sure to mention/ping players (ie. <@980446423642411098>).")

    @place.error
    async def place_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if gameOver:
                await ctx.send('Please start a new game using the '+ self.prefix +'tictactoe command.')
            else:
                await ctx.send("Please enter a position you would like to mark.")
        elif isinstance(error, commands.BadArgument):
            if gameOver:
                await ctx.send('Please start a new game using the '+ self.prefix +'tictactoe command.')
            else:
                await ctx.send("Please make sure to enter an integer.")


def setup(client):
    client.add_cog(TicTacToe(client))