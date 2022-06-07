from copy import copy

import discord
from discord.ext import commands

from common.Game import Game
from server import prefix


def instructions():
    msg = "**Checkers Help**\n"
    msg += "Capture all opponent tokens! Your tokens can move one space diagonally each turn, or capture an adjacent " \
           "opponent piece by jumping over it. If you can capture, you must. If a token reaches the end of the board, " \
           "it gains the ability to move multiple spaces and move backwards.\n "
    msg += f"`{prefix}ch start`: Start a room.\n"
    msg += f"`{prefix}ch join XXXX`: Join an existing room with its room ID specified in place of XXXX.\n"
    return msg


class CheckersGame(Game):
    def __init__(self, client):
        super().__init__(client)
        self.client = client
        self.SIZE = 8
        self.board = [['_' for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.checkers = ['r', 'R', 'b', 'B']
        self.whosemove = 'r'
        self.help_message = None
        self.move = []
        self.hit = False
        self.select_mode = False
        self.player1 = ""
        self.player1_id = 0
        self.player2 = ""
        self.player2_id = 0
        self.turn_id = self.player1_id
        self.red_checkers = 12
        self.blue_checkers = 12
        self.dirs = ['nw', 'ne', 'sw', 'se']

    def init_board(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                self.board[i][j] = '_'
        for i in range(1, self.SIZE, 2):
            self.board[i][1] = 'r'
            self.board[i][5] = 'b'
            self.board[i][7] = 'b'
        for i in range(0, self.SIZE, 2):
            self.board[i][0] = 'r'
            self.board[i][2] = 'r'
            self.board[i][6] = 'b'

    def print_row(self, board, row):
        msg = ""
        if row % 2 == 0:
            for i in range(self.SIZE):
                if board[i][row] == '_' and i % 2 == 0:
                    msg += ':black_large_square:'
                elif board[i][row] == '_':
                    msg += ':white_large_square:'
                elif board[i][row] == 'r':
                    msg += ':red_circle:'
                elif board[i][row] == 'b':
                    msg += ':blue_circle:'
        else:
            for i in range(self.SIZE):
                if board[i][row] == '_' and i % 2 != 0:
                    msg += ':black_large_square:'
                elif board[i][row] == '_':
                    msg += ':white_large_square:'
                elif board[i][row] == 'r':
                    msg += ':red_circle:'
                elif board[i][row] == 'b':
                    msg += ':blue_circle:'
        msg += '\n'
        return msg

    def print_board(self, board):
        msg = ""
        msg += ':blue_square::one::two::three::four::five::six::seven::eight:\n'
        msg += ":regional_indicator_a:" + self.print_row(board, 0)
        msg += ":regional_indicator_b:" + self.print_row(board, 1)
        msg += ":regional_indicator_c:" + self.print_row(board, 2)
        msg += ":regional_indicator_d:" + self.print_row(board, 3)
        msg += ":regional_indicator_e:" + self.print_row(board, 4)
        msg += ":regional_indicator_f:" + self.print_row(board, 5)
        msg += ":regional_indicator_g:" + self.print_row(board, 6)
        msg += ":regional_indicator_h:" + self.print_row(board, 7)
        return msg

    def movables(self, board):
        movables = []
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if board[i][j] == self.whosemove:
                    for direction in self.dirs:
                        if self.check_dir(i, j, direction):
                            movables.append([i, j])
        return movables

    def in_range(self, x, y):
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE

    def is_king(self, x, y):
        return self.board[x][y] == 'R' or self.board[x][y] == 'B'

    def hittable_dir(self, x, y, dx, dy):
        if self.whosemove == 'r' or self.whosemove == 'R':
            if self.in_range(x + dx, y + dy):
                if self.board[round(x + dx / 2)][round(y + dy / 2)] == 'b' and self.board[x + dx][y + dy] == '_':
                    return True
                elif self.board[round(x + dx / 2)][round(y + dy / 2)] == 'B' and self.board[x + dx][y + dy] == '_':
                    return True
            return False
        else:
            if self.in_range(x + dx, y + dy):
                if self.board[round(x + dx / 2)][round(y + dy / 2)] == 'r' and self.board[x + dx][y + dy] == '_':
                    return True
                elif self.board[round(x + dx / 2)][round(y + dy / 2)] == 'R' and self.board[x + dx][y + dy] == '_':
                    return True
            return False

    def check_dir(self, x, y, direction):
        match direction:
            case 'nw':
                if self.in_range(x - 1, y - 1):
                    value = self.board[x - 1][y - 1]
                    if self.hittable_dir(x, y, -2, -2):
                        return True
                    return value == '_' and not self.whosemove == 'r'
            case 'ne':
                if self.in_range(x + 1, y - 1):
                    value = self.board[x + 1][y - 1]
                    if self.hittable_dir(x, y, 2, -2):
                        return True
                    return value == '_' and not self.whosemove == 'r'
            case 'sw':
                if self.in_range(x - 1, y + 1):
                    value = self.board[x - 1][y + 1]
                    if self.hittable_dir(x, y, -2, 2):
                        return True
                    return value == '_' and not self.whosemove == 'b'
            case 'se':
                if self.in_range(x + 1, y + 1):
                    value = self.board[x + 1][y + 1]
                    if self.hittable_dir(x, y, 2, 2):
                        return True
                    return value == '_' and not self.whosemove == 'b'
        return False

    def can_hit_dirs(self, x, y):
        directions = []
        if self.hittable_dir(x, y, -2, -2):
            directions.append("nw")
        if self.hittable_dir(x, y, 2, -2):
            directions.append("ne")
        if self.hittable_dir(x, y, -2, 2):
            directions.append("sw")
        if self.hittable_dir(x, y, 2, 2):
            directions.append("se")
        return directions

    def move_up_left(self, xfrom, yfrom):
        xto = xfrom - 1
        yto = yfrom - 1
        if self.board[xto][yto] == 'b' or self.board[xto][yto] == 'r':
            return [xto - 1, yto - 1]
        return [xto, yto]

    def move_down_left(self, xfrom, yfrom):
        xto = xfrom - 1
        yto = yfrom + 1
        if self.board[xto][yto] == 'b' or self.board[xto][yto] == 'r':
            return [xto - 1, yto + 1]
        return [xto, yto]

    def move_up_right(self, xfrom, yfrom):
        xto = xfrom + 1
        yto = yfrom - 1
        if self.board[xto][yto] == 'b' or self.board[xto][yto] == 'r':
            return [xto + 1, yto - 1]
        return [xto, yto]

    def move_down_right(self, xfrom, yfrom):
        xto = xfrom + 1
        yto = yfrom + 1
        if self.board[xto][yto] == 'b' or self.board[xto][yto] == 'r':
            return [xto + 1, yto + 1]
        return [xto, yto]

    def execute_move(self, xfrom, yfrom, xto, yto):
        self.board[xfrom][yfrom] = '_'
        self.board[xto][yto] = self.whosemove
        if abs(xto - xfrom) == 2:
            self.board[round((xfrom + xto) / 2)][round((yfrom + yto) / 2)] = '_'
            self.hit = True
        if self.whosemove == 'r':
            self.red_checkers -= 1
        else:
            self.blue_checkers -= 1

    def switch_whosemove(self):
        if self.whosemove == 'r':
            self.whosemove = 'b'
        else:
            self.whosemove = 'r'

    def game_over(self):
        return self.blue_checkers == 0 or self.red_checkers == 0

    @staticmethod
    def emoji_to_x(emoji):
        match emoji:
            case "1️⃣":
                return 0
            case "2️⃣":
                return 1
            case "3️⃣":
                return 2
            case "4️⃣":
                return 3
            case "5️⃣":
                return 4
            case "6️⃣":
                return 5
            case "7️⃣":
                return 6
            case "8️⃣":
                return 7

    @staticmethod
    def emoji_to_y(y):
        match y:
            case "🇦":
                return 0
            case "🇧":
                return 1
            case "🇨":
                return 2
            case "🇩":
                return 3
            case "🇪":
                return 4
            case "🇫":
                return 5
            case "🇬":
                return 6
            case "🇭":
                return 7

    @staticmethod
    def x_to_emoji(x):
        match x:
            case 0:
                return "1️⃣"
            case 1:
                return "2️⃣"
            case 2:
                return "3️⃣"
            case 3:
                return "4️⃣"
            case 4:
                return "5️⃣"
            case 5:
                return "6️⃣"
            case 6:
                return "7️⃣"
            case 7:
                return "8️⃣"

    @staticmethod
    def y_to_emoji(y):
        match y:
            case 0:
                return "🇦"
            case 1:
                return "🇧"
            case 2:
                return "🇨"
            case 3:
                return "🇩"
            case 4:
                return "🇪"
            case 5:
                return "🇫"
            case 6:
                return "🇬"
            case 7:
                return "🇭"

    async def print_message(self, ctx):
        reactions = {""}
        reactions.remove("")
        emblem = ":blue_circle:"
        if self.whosemove == 'r':
            emblem = ":red_circle:"
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {self.player1}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select a checker\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)

        movables = self.movables(self.board)
        # Add the reaction buttons from movable checkers
        for i in movables:
            reactions.add(self.y_to_emoji(i[1]))
            reactions.add(self.x_to_emoji(i[0]))

        for reaction in sorted(reactions):
            await msg.add_reaction(reaction)

    async def move_message(self, ctx, xfrom, yfrom):
        reactions = []
        emblem = ":blue_circle:"
        if self.whosemove == 'r':
            emblem = ":red_circle:"
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {self.player1}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select direction\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        if self.check_dir(xfrom, yfrom, 'nw'):
            reactions.append("↖️")
        if self.check_dir(xfrom, yfrom, 'ne'):
            reactions.append("↗️")
        if self.check_dir(xfrom, yfrom, 'sw'):
            reactions.append("↙️")
        if self.check_dir(xfrom, yfrom, 'se'):
            reactions.append("↘️")
        reactions.append("↩️")
        for reaction in reactions:
            await msg.add_reaction(reaction)

    async def can_hits_message(self, ctx, can_hits):
        reactions = []
        emblem = ":blue_circle:"
        if self.whosemove == 'r':
            emblem = ":red_circle:"
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {self.player1}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select next hit\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        if 'nw' in can_hits:
            reactions.append("↖️")
        if 'ne' in can_hits:
            reactions.append("↗️")
        if 'sw' in can_hits:
            reactions.append("↙️")
        if 'se' in can_hits:
            reactions.append("↘️")
        if self.whosemove == 'r':
            reactions.sort(reverse=True)
        for reaction in reactions:
            await msg.add_reaction(reaction)

    async def error_message(self, ctx):
        reactions = {""}
        emblem = ":blue_circle:"
        if self.whosemove == 'r':
            emblem = ":red_circle:"
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {self.player1}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select a checker\n" \
                        "Invalid input\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        movables = self.movables(self.board)
        # Add the reaction buttons from movable checkers
        for i in movables:
            reactions.add(self.y_to_emoji(i[1]))
            reactions.add(self.x_to_emoji(i[0]))
        reactions.remove("")
        for reaction in sorted(reactions):
            await msg.add_reaction(reaction)

    async def input_handler(self, ctx, reaction):
        self.move.sort()
        xfrom = self.emoji_to_x(self.move[0])
        yfrom = self.emoji_to_y(self.move[1])

        valid_dirs = 0
        for direction in self.dirs:
            if self.check_dir(xfrom, yfrom, direction):
                valid_dirs += 1
        if valid_dirs == 0:
            self.move.clear()
            await reaction.message.delete()
            await self.error_message(ctx)
            return

        await reaction.message.delete()
        await self.move_message(ctx, xfrom, yfrom)
        self.select_mode = True

    async def select_handler(self, ctx, new_reaction, reaction):
        to = []
        xfrom = self.emoji_to_x(self.move[0])
        yfrom = self.emoji_to_y(self.move[1])
        match new_reaction:
            case "↖️":
                to = self.move_up_left(xfrom, yfrom)
            case "↗️":
                to = self.move_up_right(xfrom, yfrom)
            case "↙️":
                to = self.move_up_right(xfrom, yfrom)
            case "↘️":
                to = self.move_down_right(xfrom, yfrom)
            case "↩️":
                self.move.clear()
                self.select_mode = False
                await reaction.message.delete()
                await self.print_message(ctx)
                return
        xto = to[0]
        yto = to[1]
        self.execute_move(xfrom, yfrom, xto, yto)
        # Check available hits for current player
        can_hits = self.can_hit_dirs(xto, yto)
        if len(can_hits) > 0 and self.hit:
            self.move[0] = self.x_to_emoji(xto)
            self.move[1] = self.y_to_emoji(yto)
            self.hit = False
            await reaction.message.delete()
            await self.can_hits_message(ctx, can_hits)
            return


        self.select_mode = False
        self.move.clear()
        self.turn_id = self.player2_id
        self.switch_whosemove()

        # Check available hits for next player
        movables = self.movables(self.board)
        for position in movables:
            can_hit = self.can_hit_dirs(position[0], position[1])
            if len(can_hit) > 0:
                self.select_mode = True
                self.move.clear()
                self.move = [self.x_to_emoji(position[0]), self.y_to_emoji(position[1])]
                await reaction.message.delete()
                await self.can_hits_message(ctx, can_hit)
                return

        await reaction.message.delete()
        await self.print_message(ctx)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        new_reaction = copy(reaction.emoji)
        ctx = await self.client.get_context(reaction.message)
        if user == self.client.user:
            return
        # Set the second player on added reaction
        if self.player2 == "" and self.whosemove == 'b':
            if new_reaction in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "🇦", "🇧", "🇨", "🇩", "🇪",
                                "🇫", "🇬", "🇭"]:
                self.move.clear()
                self.player2 = user.name
                self.player2_id = user.id
                self.turn_id = self.player2_id
                await self.on_reaction_add(reaction, user)
                return
        elif user.id == self.turn_id:
            if self.select_mode:
                await self.select_handler(ctx, new_reaction, reaction)
                return
            if len(self.move) < 2:
                if new_reaction in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]:
                    if len(self.move) == 1 and self.move[0] in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]:
                        self.move.clear()
                        await reaction.message.delete()
                        await self.error_message(ctx)
                        return
                    self.move.append(new_reaction)
                    if len(self.move) == 2:
                        await self.input_handler(ctx, reaction)
                        return
                elif new_reaction in ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭"]:
                    if len(self.move) == 1 and self.move[0] in ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭"]:
                        self.move.clear()
                        await reaction.message.delete()
                        await self.error_message(ctx)
                        return
                    self.move.append(new_reaction)
                    if len(self.move) == 2:
                        await self.input_handler(ctx, reaction)
                        return

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        new_reaction = copy(reaction.emoji)
        if user == self.client.user:
            return
        if user.id == self.turn_id:
            self.move.remove(new_reaction)

    @commands.group(name="checkers", aliases=['ch'], case_insensitive=True, invoke_without_command=True)
    async def checkers(self, ctx):
        self.help_message = ctx.send(instructions())
        await self.help_message

    @checkers.command()
    async def start(self, ctx):
        self.board = [['_' for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.whosemove = 'r'
        self.help_message = None
        self.move = []
        self.select_mode = False
        self.player2 = ""
        self.player2_id = 0
        self.red_checkers = 12
        self.blue_checkers = 12
        self.init_board()
        self.player1 = ctx.message.author.name
        self.player1_id = ctx.message.author.id
        self.turn_id = self.player1_id
        await self.print_message(ctx)

    @checkers.command()
    async def clear(self, ctx):
        self.help_message = None
        self.move = []
        self.select_mode = False


def setup(client):
    client.add_cog(CheckersGame(client))
