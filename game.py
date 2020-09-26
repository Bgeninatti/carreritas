import random

import numpy as np
from PIL import Image, ImageDraw
from db import Player, User, Game, init_db, create_random_user


class Map:

    def __init__(self):
        self._image = Image.open("assets/mapa.jpg")
        self.size = self._image.size
        self._matrix = np.asarray(self._image)
        self.valid_zone = np.transpose(np.sum(self._matrix, axis=2) > 0)
        self.start_end = np.where(self.valid_zone[:, self.size[1] - 1])

    def render(self, players, winners):
        frame = self._image.copy()
        draw = ImageDraw.Draw(frame)
        for player in players:
            image_size = player.image.size
            frame.paste(player.image,
                        (player.position[0] - image_size[0],
                         player.position[1] - image_size[1]))

        for i, player in enumerate(players):
            message = f"{player.user} " + \
                      f" [gear = {player.gear}, rotation = {player.rotation}º]" + \
                      f"{' - WINNER!' if player in winners  else ''}"
            draw.text((20, 20*(1 + i)), message, fill=player.color)

        return frame

    def is_valid_zone(self, point):
        return self.valid_zone[point[0], point[1]]


def main():
    init_db("carreritas.db")
    users = User.select()
    if not users.count():
        create_random_user()
        users = User.select()
    _map = Map()
    game = Game(users[0], _map)
    frame = game.map.render(game.players, game.winners)
    frame.save("0.png")
    while True:
        player = game.next_player()
        game.play_turn(player)

        frame = game.map.render(game.players, game.winners)
        frame.save(f"{game.turn}.png")

        if game.is_turn_finished():
            if game.is_game_finished():
                winners = [p for p in game.players if p.is_winner]
                if len(winners) > 0:
                    print(f"Hubo mas de un ganador: {winners}")
                else:
                    print(f"Ganó el jugador {winners[0]}")
            else:
                game.turn += 1


if __name__ == '__main__':
    main()
