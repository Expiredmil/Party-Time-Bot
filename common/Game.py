from discord.ext import commands
from discord import User
from common import Player

class Game(commands.Cog):

    def __init__(self, client):
        self._client = client
        self.sessions = []
        self._max_players = 0
        self._min_players = 0
        self._game_name = ""
        self._game_command = ""

    @property
    def max_players(self):
        return self._max_players

    @property
    def min_players(self):
        return self._min_players

    @property
    def sessions(self):
        return self.sessions

    @sessions.setter
    def sessions(self, value):
        self._sessions = value
