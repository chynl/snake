#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import os
import errno
from snake.base import Direc, Pos, PointType, Map, Snake
from snake.gui import GameWindow


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""

        # Size
        self.map_rows = 20
        self.map_cols = 20
        self.map_width = 400      # pixels
        self.map_height = 400     # pixels
        self.window_width = 550   # pixels
        self.window_height = 400  # pixels
        self.grid_pad_ratio = 0.25

        # Delay
        self.interval_draw = 100   # ms

        # Switch
        self.show_grid_line = False
        self.show_info_panel = True

        # Color
        self.color_bg = '#000000'
        self.color_txt = '#F5F5F5'
        self.color_line = '#424242'
        self.color_wall = '#F5F5F5'
        self.color_food = '#FFF59D'
        self.color_head = '#F5F5F5'
        self.color_body = '#F5F5F5'

        # Initial snake
        self.init_direc = Direc.RIGHT
        self.init_bodies = None  # Randomly initialize
        self.init_types = None

        # Font
        self.font_info = ('Helvetica', 10)

        # Info
        self.info_str = (
            "[ keys ]\n"
            "w: move up\n"
            "a: move left\n"
            "s: move down\n"
            "d: move right\n"
            "r: restart\n"
            "space: pause/resume\n"
            "esc: exit\n\n"
            "[ status ]\n"
            "%s\n\n"
            "[ steps ]\n"
            "%d\n\n"
            "[ length ]\n"
            "%d/%d (" + str(self.map_rows) + "x" + str(self.map_cols) + ")\n\n"
        )
        self.info_status = ['eating', 'dead', 'full']

class Game:

    def __init__(self, conf):
        self.__conf = conf
        self.__map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__pause = False
        self.__window = GameWindow(conf, self.__map, self.__snake, self.__on_exit, (
            ('<w>', lambda e: self.__update_direc(Direc.UP)),
            ('<a>', lambda e: self.__update_direc(Direc.LEFT)),
            ('<s>', lambda e: self.__update_direc(Direc.DOWN)),
            ('<d>', lambda e: self.__update_direc(Direc.RIGHT)),
            ('<r>', lambda e: self.__reset()),
            ('<space>', lambda e: self.__toggle_pause())
        ))
        self.__init_log_file()

    def run(self):
        self.__window.show(self.__game_main)

    def __game_main(self):
        if not self.__map.has_food():
            self.__map.create_rand_food()
        if not self.__pause and not self.__snake.dead:
            self.__snake.move()
            self.__write_logs()

    def __update_direc(self, new_direc):
        if Direc.opposite(new_direc) != self.__snake.direc:
            self.__snake.direc_next = new_direc
            if self.__pause:
                self.__snake.move()

    def __toggle_pause(self):
        self.__pause = not self.__pause

    def __reset(self):
        self.__pause = True
        self.__snake.reset()
        self.__pause = False

    def __on_exit(self):
        if self.__log_file:
            self.__log_file.close()

    def __init_log_file(self):
        try:
            os.makedirs("logs")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            self.__log_file = None
            self.__log_file = open('logs/snake.log', 'w')
        except FileNotFoundError:
            if self.__log_file:
                self.__log_file.close()

    def __write_logs(self):
        self.__log_file.write("Step %d:\n" % self.__snake.steps)
        # Map content
        for i in range(self.__map.num_rows):
            for j in range(self.__map.num_cols):
                t = self.__map.point(Pos(i, j)).type
                if t == PointType.EMPTY:
                    self.__log_file.write("  ")
                elif t == PointType.WALL:
                    self.__log_file.write("# ")
                elif t == PointType.FOOD:
                    self.__log_file.write("F ")
                elif t == PointType.HEAD_L or t == PointType.HEAD_U or \
                    t == PointType.HEAD_R or t == PointType.HEAD_D:
                    self.__log_file.write("H ")
                else:
                    self.__log_file.write("B ")
            self.__log_file.write("\n")
        self.__log_file.write("Last direc: %s\n" % str(self.__snake.direc))
        self.__log_file.write("\n")
