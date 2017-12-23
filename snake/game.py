#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import os
import errno
from snake.base import Direc, Pos, PointType, Map, Snake
from snake.gui import GameWindow
from snake.solver import GreedySolver, HamiltonSolver


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""

        # Size
        self.map_rows = 10
        self.map_cols = self.map_rows
        self.map_width = 400      # pixels
        self.map_height = 400     # pixels
        self.window_width = 550   # pixels
        self.window_height = 400  # pixels
        self.grid_pad_ratio = 0.25

        # AI
        self.enable_AI = True
        self.solver_name = 'HamiltonSolver'

        # Switch
        self.show_gui = True
        self.show_grid_line = False
        self.show_info_panel = True

        # Delay
        self.interval_draw = 40       # ms
        self.interval_draw_max = 250  # ms

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
        self.init_bodies = [Pos(1, 2), Pos(1, 1)]
        self.init_types = [PointType.HEAD_R, PointType.BODY_HOR]

        # Font
        self.font_info = ('Helvetica', 9)

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
            "[ solver ]\n"
            "%s\n\n"
            "[ status ]\n"
            "%s\n\n"
            "[ steps ]\n"
            "%d\n\n"
            "[ length ]\n"
            "%d/%d (" + str(self.map_rows) + "x" + str(self.map_cols) + ")\n"
        )
        self.info_status = ['eating', 'dead', 'full']

class Game:

    def __init__(self, conf):
        self.__conf = conf
        self.__map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__pause = False
        self.__window = GameWindow(conf, self.__map, "Snake", self.__snake, self.__on_exit, (
            ('<w>', lambda e: self.__update_direc(Direc.UP)),
            ('<a>', lambda e: self.__update_direc(Direc.LEFT)),
            ('<s>', lambda e: self.__update_direc(Direc.DOWN)),
            ('<d>', lambda e: self.__update_direc(Direc.RIGHT)),
            ('<r>', lambda e: self.__reset()),
            ('<space>', lambda e: self.__toggle_pause())
        ))
        self.__solver = globals()[self.__conf.solver_name](self.__snake)
        self.__episode = 1
        self.__init_log_file()

    def run(self):
        if self.__conf.show_gui:
            self.__window.show(self.__game_main)
        else:
            self.__run_batch_episodes()

    def __run_batch_episodes(self):
        STEPS_LIMIT = 10000
        episodes = int(input("Please input the number of episodes: "))
        print("\nMap size: %dx%d\n" % (self.__conf.map_rows, self.__conf.map_cols))
        tot_suc, tot_suc_steps = 0, 0
        for _ in range(episodes):
            print("Episode %d - " % self.__episode, end="")
            while True:
                self.__game_main()
                if self.__map.is_full():
                    tot_suc += 1
                    tot_suc_steps += self.__snake.steps
                    print("SUC  (steps: %d)" % self.__snake.steps)
                    break
                if self.__snake.dead or self.__snake.steps >= STEPS_LIMIT:
                    print("FAIL  (steps: %d)" % self.__snake.steps)
                    if self.__snake.steps >= STEPS_LIMIT:
                        self.__write_logs()  # Write the last step
                    break
            self.__reset()
        suc_ratio = tot_suc / (self.__episode - 1)
        avg_suc_steps = 0
        if tot_suc != 0:
            avg_suc_steps = tot_suc_steps // tot_suc
        print("\n[Summary]\nTotal: %d  SUC: %d (%.2f%%)  Avg SUC steps: %d\n" % \
              (self.__episode - 1, tot_suc, 100 * suc_ratio, avg_suc_steps))
        self.__on_exit()

    def __game_main(self):
        """Main function in the game loop."""
        if not self.__map.has_food():
            self.__map.create_rand_food()

        if self.__pause or self.__episode_end():
            return

        if self.__conf.enable_AI:
            self.__update_direc(self.__solver.next_direc())

        if self.__conf.show_gui and self.__snake.direc_next != Direc.NONE:
            self.__write_logs()

        self.__snake.move()

        if self.__episode_end():
            self.__write_logs()  # Write the last step

    def __update_direc(self, new_direc):
        if Direc.opposite(new_direc) != self.__snake.direc:
            self.__snake.direc_next = new_direc
            if self.__pause:
                self.__snake.move()

    def __toggle_pause(self):
        self.__pause = not self.__pause

    def __episode_end(self):
        return self.__snake.dead or self.__map.is_full()

    def __reset(self):
        self.__snake.reset()
        self.__episode += 1

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
        self.__log_file.write("[ Episode %d / Step %d ]\n" % \
                              (self.__episode, self.__snake.steps))
        for i in range(self.__map.num_rows):
            for j in range(self.__map.num_cols):
                pos = Pos(i, j)
                t = self.__map.point(pos).type
                if t == PointType.EMPTY:
                    self.__log_file.write("  ")
                elif t == PointType.WALL:
                    self.__log_file.write("# ")
                elif t == PointType.FOOD:
                    self.__log_file.write("F ")
                elif t == PointType.HEAD_L or t == PointType.HEAD_U or \
                    t == PointType.HEAD_R or t == PointType.HEAD_D:
                    self.__log_file.write("H ")
                elif pos == self.__snake.tail():
                    self.__log_file.write("T ")
                else:
                    self.__log_file.write("B ")
            self.__log_file.write("\n")
        self.__log_file.write("[ last/next direc: %s/%s ]\n" % \
                              (self.__snake.direc, self.__snake.direc_next))
        self.__log_file.write("\n")
