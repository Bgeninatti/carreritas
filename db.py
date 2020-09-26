import string
import datetime
import random

import numpy as np
from PIL import Image, ImageDraw

from peewee import (BooleanField, CharField, CompositeKey, DateTimeField, FloatField,
                    ForeignKeyField, IntegerField, Model, SqliteDatabase)

database = SqliteDatabase(None)

class BaseModel(Model):

    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database


class User(BaseModel):
    last_name = CharField()
    first_name = CharField()
    last_login = DateTimeField(default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.id}" if not self.first_name and not self.last_name else \
            f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.__repr__()


class Game(BaseModel):

    code = CharField(primary_key=True)
    turn = IntegerField()

    def __init__(self, creator, _map, speed_constant=5):
        super().__init__()
        self.code = "".join((random.choice(string.ascii_letters) for i in range(4)))
        self.speed_constant = speed_constant
        self.map = _map
        self.players = []
        self.winners = []
        self.turn = 0
        self.save()
        self.init_player(creator)

    def init_player(self, user):
        player_separation = 20
        road_start = np.min(self.map.start_end)
        i = len(self.players)
        position = (road_start + player_separation*(i + 1), self.map.size[1] - 1)
        color = tuple((random.choice(range(100, 256, int(256/16))) for i in range(3)))
        rotation = 0
        gear = 0
        player = Player(self.code, user, position, rotation, gear, color)
        player.save()
        self.players.append(player)

    def play_turn(self, player):

        print(f"Turno del ugador {player.user}")
        aceleracion_str = input("1) Acelera\n2) Frena\nSeleccione una opción: ")
        available_directions = [-90, -45, 0, 45, 90]
        direccion_str = input(
            "Seleccione una dirección" + \
            "\n".join([f"{i}) {a}º" + "\n"
                       for i, a in enumerate(available_directions)]))
        rotation_deg = available_directions[int(direccion_str)]
        direction = player.rotation + np.deg2rad(rotation_deg)

        acelera = int(aceleracion_str) == 1
        frena = int(aceleracion_str) == 2
        if acelera:
            print("Acelerando")
            player.gear = min(player.gear + 1, 6)
        if frena:
            print("Frenando")
            player.gear = max(player.gear - 1, 0)

        print(f"Angulo de direction: {direction}")
        magnitud = self.speed_constant*player.gear
        direccion_vector = np.array([
            np.sin(direction), np.cos(direction)
        ])
        print(f"Vector de direction: ({direccion_vector[0]}, {direccion_vector[1]})")
        speed = (direccion_vector*magnitud).astype(int)
        print(f"La velocidad es ({speed[0]}, {speed[1]})")

        destination = player.position - speed
        destination[0] = max(0, min(self.map.size[0] - 1, destination[0]))
        destination[1] = max(0, min(self.map.size[1] - 1, destination[1]))

        print(f"Destino: {destination}")
        if not self.map.is_valid_zone(destination):
            print(f"JUGADOR {player.user} PIERDE EL TURNO")
        else:
            player.rotation += rotation_deg
            player.image = player.image.rotate(rotation_deg)
            player.position -= speed
        player.turns_played += 1
        player.save()
        print(f"La posicion del jugador {player.user}" + \
              f"es ({player.position[0]}, {player.position[1]})")
        print("--------------------")

    def is_game_finished(self):
        map_middle = int(self.map.size[0] / 2)
        is_finished = False
        for player in self.players:
            if player.position[1] == self.map.size[1] - 1 \
                    and player.position[0] > map_middle:
                player.is_winner = True
                player.save()
                is_finished = True
        return is_finished

    def next_player(self):
        self.players.sort(key=lambda p: p.turns_played)
        return self.players[0]

    def is_turn_finished(self):
        return len(set((p.turns_played for p in self.players))) == 1


class Player(BaseModel):
    game = ForeignKeyField(Game, backref='players')
    user = ForeignKeyField(User, backref='games')
    _position_x = IntegerField()
    _position_y = IntegerField()
    rotation = FloatField()
    gear = IntegerField()
    _color_r = IntegerField()
    _color_g = IntegerField()
    _color_b = IntegerField()
    turns_played = IntegerField()
    is_winner = BooleanField()

    class Meta:
        primary_key = CompositeKey('game', 'user')

    def __init__(self, game_id, user, position, rotation, gear, color):
        super().__init__()
        self.game_id = game_id
        self.user = user
        self._position_x = position[0]
        self._position_y = position[1]
        self.rotation = rotation
        self.gear = gear
        self._color_r = color[0]
        self._color_g = color[1]
        self._color_b = color[2]
        self.position = position
        self.color = color
        self.image = Image.new('RGB', (10, 10), (255, 255, 255))
        self.turns_played = 0
        self.is_winner = False
        draw = ImageDraw.Draw(self.image)
        draw.polygon(((0, 9), (5, 0), (10, 9)),
                     fill=self.color,
                     outline=(0, 0, 0))


def init_db(db_path):
    database.init(db_path)
    database.connect()
    database.create_tables([User, Player, Game])
    return database

def create_random_user():
    user = User()
    user.first_name = "Bruno"
    user.last_name = "G."
    user.save()
    print("Random user created")

