#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from snake.base import Direc, Pos, PointType, Map, Snake
from snake.gui import GameWindow


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""

        # Size
        self.map_rows = 20
        self.map_cols = 20
        self.window_width = 300
        self.window_height = 300
        self.grid_pad_ratio = 0.25

        # Switch
        self.show_grid_line = False

        # Color
        self.color_grid_line = '#424242'
        self.color_bg = '#000000'
        self.color_wall = '#F5F5F5'
        self.color_food = '#F5F5F5'
        self.color_head = '#F5F5F5'
        self.color_body = '#F5F5F5'

        # Initial snake
        self.init_direc = Direc.RIGHT
        self.init_bodies = [Pos(1, 3), Pos(1, 2), Pos(1, 1)]
        self.init_types = [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR]


class Game:

    def __init__(self, conf):
        """Initialize a Game object.

        Args:
            conf (snake.game.GameConf): Game configuration.

        """
        self.__conf = conf
        self.__map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__window = GameWindow(self.__map, conf)

    def run(self):
        self.__window.after(100, self.__game_loop)
        self.__window.mainloop()

    def __game_loop(self):
        while True:
            self.__window.render()
