import random

import numpy as np
from PIL import Image, ImageDraw

map_size = (100, 100)


class Player:

    def __init__(self, pid, position):
        self.pid = pid
        self.color = tuple((random.choice(range(0, 256, int(256/16))) for i in range(3)))
        self.image = Image.new('RGB', (10, 10), (255, 255, 255))
        draw = ImageDraw.Draw(self.image)
        draw.polygon(((0, 9), (5, 0), (10, 9)),
                     fill=self.color,
                     outline=(0, 0, 0))

        self.position = np.array(position)
        self.rotation = 0
        self.gear = 0

class Map:

    def __init__(self):
        self._image = Image.open("assets/mapa.jpg")
        self.size = self._image.size
        self._matrix = np.asarray(self._image)
        self.valid_zone = np.transpose(np.sum(self._matrix, axis=2) > 0)
        self.start_end = np.where(self.valid_zone[:, self.size[1] - 1])

    def render(self, players):
        frame = self._image.copy()
        for player in players:
            image_size = player.image.size
            frame.paste(player.image,
                        (player.position[0] - image_size[0],
                         player.position[1] - image_size[1]))
        return frame

    def is_valid_zone(self, point):
        return self.valid_zone[point[0], point[1]]


class Game:

    def __init__(self, players_count, speed_constant=5):
        self.speed_constant = speed_constant
        self.map = Map()

        player_separation = 20

        road_start = np.min(self.map.start_end)
        self.players = []
        for jid in range(players_count):
            posicion = (road_start + player_separation*(jid + 1), self.map.size[1] - 1)
            self.players.append(Player(jid, posicion))

        self.winners = []

    def play_turn(self):

        for player in self.players:

            print(f"Turno del ugador {player.pid}")
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
                print(f"JUGADOR {player.pid} PIERDE EL TURNO")
            else:
                player.rotation = direction
                player.image = player.image.rotate(rotation_deg)
                player.position -= speed
            print(f"La posicion del jugador {player.pid}" + \
                  f"es ({player.position[0]}, {player.position[1]})")
            print("--------------------")

    def is_finish(self):
        map_middle = int(self.map.size[0] / 2)
        self.winners = []
        for player in self.players:
            if player.position[1] == self.map.size[1] - 1 \
                    and player.position[0] > map_middle:
                self.winners.append(player.pid)
        return len(self.winners) > 0



def main():
    game = Game(2)
    frame = game.map.render(game.players)
    frame.save("0.png")
    t = 1
    while True:
        game.play_turn()

        frame = game.map.render(game.players)
        frame.save(f"{t + 1}.png")

        if game.is_finish():
            if len(game.winners) > 0:
                print(f"Hubo mas de un ganador: {game.winners}")
            else:
                print(f"Ganó el jugador {game.winners[0]}")
        t += 1


if __name__ == '__main__':
    main()
