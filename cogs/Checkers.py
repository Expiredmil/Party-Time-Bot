from copy import copy

import discord
from discord.ext import commands
from discord_ui import Button


async def add_to_balance(player_id, x):
    from models import Members
    member = await Members.filter(member_id=player_id).get_or_none()
    cur_bal = member.balance
    await Members.filter(member_id=player_id).update(balance=cur_bal + x)


class CheckersGame(commands.Cog):

    def __init__(self, client):
        self.king = False
        self.client = client
        self.red_checkers = 12
        self.blue_checkers = 12
        self.SIZE = 8
        self.board = [['_' for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.whosemove = ['r', 'R']
        self.player1 = ""
        self.player1_id = 0
        self.player2 = ""
        self.player2_id = 0
        self.turn_id = self.player1_id
        self.move = []
        self.hit = False
        self.select_mode = False
        self.next_movable = False
        self.movable_checkers = []
        self.dirs = ['nw', 'ne', 'sw', 'se']

    async def instructions(self, ctx):
        msg = "**Checkers Help**\n"
        msg += "Capture all opponent tokens! Your tokens can move one space diagonally each turn, or capture an adjacent\n" \
               "opponent piece by jumping over it. If you can capture, you must. If a token reaches the end of the board,\n" \
               "it gains the ability to move multiple spaces and move backwards.\n"
        msg += f"`{await self.client.get_prefix(ctx)}ch start`: Start a game\n"
        return msg

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
            for col in range(self.SIZE):
                if board[col][row] == '_' and col % 2 == 0:
                    msg += ':black_large_square:'
                elif board[col][row] == '_':
                    msg += ':white_large_square:'
                elif board[col][row] == 'r':
                    msg += ':red_circle:'
                elif board[col][row] == 'R':
                    msg += ':orange_circle:'
                elif board[col][row] == 'b':
                    msg += ':blue_circle:'
                elif board[col][row] == 'B':
                    msg += ':purple_circle:'
        else:
            for col in range(self.SIZE):
                if board[col][row] == '_' and col % 2 != 0:
                    msg += ':black_large_square:'
                elif board[col][row] == '_':
                    msg += ':white_large_square:'
                elif board[col][row] == 'r':
                    msg += ':red_circle:'
                elif board[col][row] == 'R':
                    msg += ':orange_circle:'
                elif board[col][row] == 'b':
                    msg += ':blue_circle:'
                elif board[col][row] == 'B':
                    msg += ':purple_circle:'
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

    def movables(self):
        movables = []
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.board[i][j] in self.whosemove:
                    for direction in self.dirs:
                        if self.check_dir(i, j, direction):
                            movables.append([i, j])
        return movables

    def in_range(self, x, y):
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE

    def is_king(self, x, y):
        return self.board[x][y] == 'R' or self.board[x][y] == 'B'

    def check_for_new_king(self, xto, yto):
        if yto == self.SIZE - 1 and self.board[xto][yto] == 'r':
            self.board[xto][yto] = 'R'
        elif yto == 0 and self.board[xto][yto] == 'b':
            self.board[xto][yto] = 'B'

    def hittable_dir(self, x, y, dx, dy):
        if 'r' in self.whosemove or 'R' in self.whosemove:
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
                    return value == '_' and self.board[x][y] != 'r'
            case 'ne':
                if self.in_range(x + 1, y - 1):
                    value = self.board[x + 1][y - 1]
                    if self.hittable_dir(x, y, 2, -2):
                        return True
                    return value == '_' and self.board[x][y] != 'r'
            case 'sw':
                if self.in_range(x - 1, y + 1):
                    value = self.board[x - 1][y + 1]
                    if self.hittable_dir(x, y, -2, 2):
                        return True
                    return value == '_' and self.board[x][y] != 'b'
            case 'se':
                if self.in_range(x + 1, y + 1):
                    value = self.board[x + 1][y + 1]
                    if self.hittable_dir(x, y, 2, 2):
                        return True
                    return value == '_' and self.board[x][y] != 'b'
        return False

    def can_hit_dirs(self, x, y):
        directions = []
        if self.hittable_dir(x, y, -2, -2) and self.board[x][y] != 'r':
            directions.append("nw")
        if self.hittable_dir(x, y, 2, -2) and self.board[x][y] != 'r':
            directions.append("ne")
        if self.hittable_dir(x, y, -2, 2) and self.board[x][y] != 'b':
            directions.append("sw")
        if self.hittable_dir(x, y, 2, 2) and self.board[x][y] != 'b':
            directions.append("se")
        return directions

    def move_up_left(self, xfrom, yfrom):
        xto = xfrom - 1
        yto = yfrom - 1
        if self.board[xto][yto] == 'r' or self.board[xto][yto] == 'R' or self.board[xto][yto] == 'b' or self.board[xto][
            yto] == 'B':
            return [xto - 1, yto - 1]
        return [xto, yto]

    def move_down_left(self, xfrom, yfrom):
        xto = xfrom - 1
        yto = yfrom + 1
        if self.board[xto][yto] == 'r' or self.board[xto][yto] == 'R' or self.board[xto][yto] == 'b' or self.board[xto][
            yto] == 'B':
            return [xto - 1, yto + 1]
        return [xto, yto]

    def move_up_right(self, xfrom, yfrom):
        xto = xfrom + 1
        yto = yfrom - 1
        if self.board[xto][yto] == 'r' or self.board[xto][yto] == 'R' or self.board[xto][yto] == 'b' or self.board[xto][
            yto] == 'B':
            return [xto + 1, yto - 1]
        return [xto, yto]

    def move_down_right(self, xfrom, yfrom):
        xto = xfrom + 1
        yto = yfrom + 1
        if self.board[xto][yto] == 'r' or self.board[xto][yto] == 'R' or self.board[xto][yto] == 'b' or self.board[xto][
            yto] == 'B':
            return [xto + 1, yto + 1]
        return [xto, yto]

    def execute_move(self, xfrom, yfrom, xto, yto):
        self.board[xto][yto] = self.board[xfrom][yfrom]
        self.board[xfrom][yfrom] = '_'
        if abs(xto - xfrom) == 2:
            self.board[round((xfrom + xto) / 2)][round((yfrom + yto) / 2)] = '_'
            self.hit = True
            self.king = False
            if 'b' in self.whosemove:
                self.red_checkers -= 1
            else:
                self.blue_checkers -= 1

    def switch_player(self):
        if 'r' in self.whosemove:
            self.whosemove = ['b', 'B']
            self.turn_id = self.player2_id
        else:
            self.whosemove = ['r', 'R']
            self.turn_id = self.player1_id

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
        emblem = ":red_circle:"
        player = self.player1
        if 'b' in self.whosemove:
            emblem = ":blue_circle:"
            player = self.player2
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {player}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select a checker\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)

        self.movable_checkers = self.movables()
        # Add the reaction buttons from movable checkers
        for i in self.movable_checkers:
            reactions.add(self.y_to_emoji(i[1]))
            reactions.add(self.x_to_emoji(i[0]))
        for reaction in sorted(reactions):
            await msg.add_reaction(reaction)

    async def await_player2_message(self, ctx):
        embed = discord.Embed(
            title='Checkers',
            description=f"Waiting for second player\n" \
                        f"Press join to compete against {self.player1}\n" \
                        f"{self.print_board(self.board)}\n"
        )
        join_button = Button("Join", color="green")
        msg = await ctx.send(embed=embed, components=[join_button])
        try:
            btn = await msg.wait_for("button", self.client, timeout=20)
            self.player2_id = btn.author.id
            self.player2 = btn.author.display_name
            self.select_mode = False
            self.move.clear()
            self.switch_player()
            await msg.delete()
            await self.print_message(ctx)
        except TimeoutError:
            await msg.delete()
            await msg.delete()
            await ctx.send("timeout")

    async def move_message(self, ctx, xfrom, yfrom, direction):
        reactions = []
        emblem = ":red_circle:"
        player = self.player1
        if 'b' in self.whosemove:
            emblem = ":blue_circle:"
            player = self.player2
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {player}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select a move\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        if self.check_dir(xfrom, yfrom, 'nw') and direction is None or self.check_dir(xfrom, yfrom,
                                                                                      'nw') and direction == 'nw':
            reactions.append("↖️")
        if self.check_dir(xfrom, yfrom, 'ne') and direction is None or self.check_dir(xfrom, yfrom,
                                                                                      'ne') and direction == 'ne':
            reactions.append("↗️")
        if self.check_dir(xfrom, yfrom, 'sw') and direction is None or self.check_dir(xfrom, yfrom,
                                                                                      'sw') and direction == 'sw':
            reactions.append("↙️")
        if self.check_dir(xfrom, yfrom, 'se') and direction is None or self.check_dir(xfrom, yfrom,
                                                                                      'ne') and direction == 'se':
            reactions.append("↘️")
        if self.king:
            reactions.append("☑️")
        else:
            reactions.append("↩️")
        for reaction in reactions:
            await msg.add_reaction(reaction)

    async def can_hits_message(self, ctx, can_hits):
        reactions = []
        emblem = ":red_circle:"
        player = self.player1
        if 'b' in self.whosemove:
            emblem = ":blue_circle:"
            player = self.player2
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {player}!\n" \
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
        if 'r' in self.whosemove:
            reactions.sort(reverse=True)
        for reaction in reactions:
            await msg.add_reaction(reaction)

    async def next_movables_message(self, ctx, movables):
        reactions = {""}
        reactions.remove("")
        emblem = ":red_circle:"
        player = self.player1
        if 'b' in self.whosemove:
            emblem = ":blue_circle:"
            player = self.player2
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {player}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select checker for next hit\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        for movable in movables:
            reactions.add(self.x_to_emoji(movable[0]))
            reactions.add(self.y_to_emoji(movable[1]))
        for reaction in sorted(reactions):
            await msg.add_reaction(reaction)

    async def error_message(self, ctx):
        reactions = {""}
        emblem = ":red_circle:"
        player = self.player1
        if 'b' in self.whosemove:
            emblem = ":blue_circle:"
            player = self.player2
        embed = discord.Embed(
            title='Checkers',
            description=f"It's your turn {player}!\n" \
                        f"Turn : {emblem}\n" \
                        "Select a checker\n" \
                        "Invalid input\n" \
                        f"{self.print_board(self.board)}\n"
        )
        msg = await ctx.send(embed=embed)
        # Add the reaction buttons from movable checkers
        for i in self.movable_checkers:
            reactions.add(self.y_to_emoji(i[1]))
            reactions.add(self.x_to_emoji(i[0]))
        reactions.remove("")
        for reaction in sorted(reactions):
            await msg.add_reaction(reaction)

    async def input_handler(self, ctx, reaction):
        self.move.sort()
        xfrom = self.emoji_to_x(self.move[0])
        yfrom = self.emoji_to_y(self.move[1])

        # Check for valid user input
        if [xfrom, yfrom] not in self.movable_checkers:
            self.move.clear()
            await reaction.message.delete()
            await self.error_message(ctx)
            return

        if self.is_king(xfrom, yfrom):
            self.king = True

        # Go to the select move screen
        if self.next_movable:
            self.next_movable = False
            await reaction.message.delete()
            await self.can_hits_message(ctx, self.can_hit_dirs(xfrom, yfrom))
        else:
            await reaction.message.delete()
            await self.move_message(ctx, xfrom, yfrom, None)
        self.select_mode = True

    async def select_handler_king(self, ctx, new_reaction, reaction):
        # Execute user input
        to = []
        xfrom = self.emoji_to_x(self.move[0])
        yfrom = self.emoji_to_y(self.move[1])
        match new_reaction:
            case "↖️":
                to = self.move_up_left(xfrom, yfrom)
                direction = "nw"
            case "↗️":
                to = self.move_up_right(xfrom, yfrom)
                direction = "ne"
            case "↙️":
                to = self.move_down_left(xfrom, yfrom)
                direction = "sw"
            case "↘️":
                to = self.move_down_right(xfrom, yfrom)
                direction = "se"
            case "☑️":
                self.move.clear()
                self.switch_player()
                self.select_mode = False
                self.king = False
                await reaction.message.delete()
                await self.print_message(ctx)
                return
        xto = to[0]
        yto = to[1]
        self.execute_move(xfrom, yfrom, xto, yto)

        # Check for game over
        if self.game_over():
            if self.red_checkers == 0:
                x = 10
                await add_to_balance(self.player2_id, x)
                await ctx.send(f"{self.player2} has won!\n" /
                               f"Balance player 2 increased by {x}")
            else:
                x = 10
                await add_to_balance(self.player1_id, x)
                await ctx.send(f"{self.player1} has won!" /
                               f"Balance player 1 increased by {x}")

        # Check available hits for current player
        self.move[0] = self.x_to_emoji(xto)
        self.move[1] = self.y_to_emoji(yto)
        can_hits = self.can_hit_dirs(xto, yto)
        if len(can_hits) > 0 and self.hit:
            self.hit = False
            await reaction.message.delete()
            await self.can_hits_message(ctx, can_hits)
            return

        # If king has a hit and no hits are available, then next switch players
        if self.hit:
            self.move.clear()
            self.switch_player()
            self.select_mode = False
            await reaction.message.delete()
            await self.print_message(ctx)
            return

        await reaction.message.delete()
        await self.move_message(ctx, xto, yto, direction)

    async def select_handler(self, ctx, new_reaction, reaction):
        self.hit = False
        # Execute user input
        to = []
        xfrom = self.emoji_to_x(self.move[0])
        yfrom = self.emoji_to_y(self.move[1])
        match new_reaction:
            case "↖️":
                to = self.move_up_left(xfrom, yfrom)
            case "↗️":
                to = self.move_up_right(xfrom, yfrom)
            case "↙️":
                to = self.move_down_left(xfrom, yfrom)
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

        # Check next available hits for current player
        if await self.hits_current_player(ctx, reaction, xto, yto):
            return

        # Check for new king
        self.check_for_new_king(xto, yto)

        # Check for game over
        if self.game_over():
            if self.red_checkers == 0:
                x = 10
                await add_to_balance(self.player2_id, x)
                await ctx.send(f"{self.player2} has won!\n" /
                               f"Balance player 2 increased by {x}")
            else:
                x = 10
                await add_to_balance(self.player1_id, x)
                await ctx.send(f"{self.player1} has won!" /
                               f"Balance player 1 increased by {x}")

        # Set second player
        if self.player2_id == 0:
            await reaction.message.delete()
            await self.await_player2_message(ctx)
            return

        # Switch players
        self.select_mode = False
        self.move.clear()
        self.switch_player()

        # Check available hits for next player
        if await self.hits_next_player(ctx, reaction):
            return

        await reaction.message.delete()
        await self.print_message(ctx)

    async def hits_current_player(self, ctx, reaction, xto, yto):
        can_hits = self.can_hit_dirs(xto, yto)
        if len(can_hits) > 0 and self.hit:
            self.hit = False
            self.move[0] = self.x_to_emoji(xto)
            self.move[1] = self.y_to_emoji(yto)
            await reaction.message.delete()
            await self.can_hits_message(ctx, can_hits)
            return True
        return False

    async def hits_next_player(self, ctx, reaction):
        self.movable_checkers.clear()
        self.movable_checkers = self.movables()
        movables = []
        for movable in self.movable_checkers:
            can_hit = self.can_hit_dirs(movable[0], movable[1])
            if len(can_hit) > 0:
                movables.append(movable)
        if len(movables) > 0:
            self.next_movable = True
            await reaction.message.delete()
            await self.next_movables_message(ctx, movables)
            return True
        return False

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        new_reaction = copy(reaction.emoji)
        ctx = await self.client.get_context(reaction.message)
        if user == self.client.user:
            return
        elif user.id == self.turn_id:
            if self.select_mode:
                if not self.king:
                    await self.select_handler(ctx, new_reaction, reaction)
                else:
                    await self.select_handler_king(ctx, new_reaction, reaction)
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
        await ctx.send(await self.instructions(ctx))

    @checkers.command()
    async def start(self, ctx):
        self.board = [['_' for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.whosemove = ['r', 'R']
        self.move = []
        self.hit = False
        self.select_mode = False
        self.next_movable = False
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
    async def player1(self, ctx):
        await ctx.send(f"Player 1 : {self.player1}, {self.player1_id}")

    @checkers.command()
    async def player2(self, ctx):
        await ctx.send(f"Player 2 : {self.player2}, {self.player2_id}")

    @checkers.command()
    async def clear(self):
        self.move = []
        self.select_mode = False


def setup(client):
    client.add_cog(CheckersGame(client))
