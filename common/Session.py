import imp
from discord.ext import commands
from discord import User
import Player


import random

def generate_roomID (sessions):
    letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M",
                "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    id = ""
    while len(id) < 4:
        id += random.choice(letters)
    return id

class Session(commands.Cog):
    def __init__(self, parent):
        self.parent = parent
        self.players = []
        self.session_id = generate_roomID(parent.sessions)
        self.game = ""


    def add_player(self, player: Player):
        if not any(player.user.id == active_player.user.id for active_player in self.__players):
            self.__players.append(player)

    def remove_player(self, user: User):
        for player in reversed(self.__players):
            if player.user.id == user.id:
                self.__players.remove(player)