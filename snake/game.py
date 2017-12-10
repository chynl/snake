#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import time
from threading import Thread
from snake.base import Direc, Pos, PointType, Map, Snake
from snake.gui import GameWindow


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""

        # Size
        self.map_rows = 20
        self.map_cols = 20
        self.window_width = 400
        self.window_height = 400
        self.grid_pad_ratio = 0.25

        # Delay
        self.interval_draw = 100   # ms

        # Switch
        self.show_grid_line = False

        # Color
        self.color_grid_line = '#424242'
        self.color_bg = '#000000'
        self.color_wall = '#F5F5F5'
        self.color_food = '#FFF59D'
        self.color_head = '#F5F5F5'
        self.color_body = '#F5F5F5'

        # Initial snake
        self.init_direc = Direc.RIGHT
        self.init_bodies = [Pos(1, 3), Pos(1, 2), Pos(1, 1)]
        self.init_types = [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR]


class Game:

    def __init__(self, conf):
        self.__conf = conf
        self.__map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__window = GameWindow(self.__map, conf, self.__keybindings())
        self.__pause = False

    def run(self):
        self.__window.show(self.__game_main)

    def __game_main(self):
        if not self.__map.has_food():
            self.__map.create_rand_food()
        if not self.__pause:
            self.__snake.move()

    def __keybindings(self):
        return (
            ('<w>', lambda e: self.__update_direc(Direc.UP)),
            ('<a>', lambda e: self.__update_direc(Direc.LEFT)),
            ('<s>', lambda e: self.__update_direc(Direc.DOWN)),
            ('<d>', lambda e: self.__update_direc(Direc.RIGHT)),
            ('<r>', lambda e: self.__reset()),
            ('<space>', lambda e: self.__toggle_pause())
        )

    def __update_direc(self, new_direc):
        if Direc.opposite(new_direc) != self.__snake.direc:
            self.__snake.direc_next = new_direc
            if self.__pause:
                self.__snake.move()

    def __toggle_pause(self):
        self.__pause = not self.__pause

    def __reset(self):
        self.__snake.dead = True
        self.__map.reset()
        self.__snake = Snake(self.__map, self.__conf.init_direc,
                             self.__conf.init_bodies, self.__conf.init_types)
        self.__pause = False
