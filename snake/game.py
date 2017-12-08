#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from snake.base import Direc, Pos, PointType, Map, Snake
from snake.gui import GameWindow


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""
        self.width = 12
        self.height = 12
        self.init_direc = Direc.RIGHT
        self.init_bodies = [Pos(1, 3), Pos(1, 2), Pos(1, 1)]
        self.init_types = [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR]


class Game:

    def __init__(self, conf):
        """Initialize a Game object.

        Args:
            conf (snake.game.GameConf): Game configuration.

        """
        self.__map = Map(conf.width, conf.height)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__window = GameWindow(self.__map)

    def run(self):
        self.__window.after(100, self.__game_loop)
        self.__window.mainloop()

    def __game_loop(self):
        while True:
            self.__window.render()
