#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,W0201,W0703

import errno
import os
import traceback
from enum import Enum, unique

import matplotlib.pyplot as plt

from snake.base import Direc, Map, PointType, Pos, Snake
from snake.gui import GameWindow
from snake.solver import DQNSolver, GreedySolver, HamiltonSolver


@unique
class GameMode(Enum):
    NORMAL = 0         # AI with GUI
    BENCHMARK = 1      # Run benchmarks without GUI
    TRAIN_DQN = 2      # Train DQNSolver without GUI
    TRAIN_DQN_GUI = 3  # Train DQNSolver with GUI


class GameConf:

    def __init__(self):
        """Initialize a default configuration."""

        # Game mode
        self.mode = GameMode.NORMAL

        # Solver
        self.solver_name = 'HamiltonSolver'  # Class name of the solver

        # Size
        self.map_rows = 10
        self.map_cols = self.map_rows
        self.map_width = 190  # pixels
        self.map_height = self.map_width
        self.info_panel_width = 170  # pixels
        self.window_width = self.map_width + self.info_panel_width
        self.window_height = self.map_height
        self.grid_pad_ratio = 0.25

        # Switch
        self.show_grid_line = False
        self.show_info_panel = True

        # Delay
        self.interval_draw = 40       # ms
        self.interval_draw_max = 200  # ms

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
            "<w/a/s/d>: up/left/down/right\n"
            "<space>: pause/resume\n"
            "<r>: restart    <esc>: exit\n"
            "---------------------------------\n"
            "solver: %s\n"
            "status: %s\n"
            "episode: %d   step: %d\n"
            "length: %d/%d (" + str(self.map_rows) + "x" + str(self.map_cols) + ")\n"
            "---------------------------------\n"
            "move delay:"
        )
        self.info_status = ['eating', 'dead', 'full']

class Game:

    def __init__(self, conf):
        self.__conf = conf
        self.__map = Map(conf.map_rows + 2, conf.map_cols + 2)
        self.__snake = Snake(self.__map, conf.init_direc,
                             conf.init_bodies, conf.init_types)
        self.__pause = False
        self.__solver = globals()[self.__conf.solver_name](self.__snake)
        self.__episode = 1
        self.__init_log_file()

    @property
    def snake(self):
        return self.__snake

    @property
    def episode(self):
        return self.__episode

    def run(self):
        if self.__conf.mode == GameMode.BENCHMARK:
            self.__run_benchmarks()
        elif self.__conf.mode == GameMode.TRAIN_DQN:
            self.__run_dqn_train()
            self.__plot_history()
        else:
            window = GameWindow("Snake", self.__conf, self.__map, self, self.__on_exit, (
                ('<w>', lambda e: self.__update_direc(Direc.UP)),
                ('<a>', lambda e: self.__update_direc(Direc.LEFT)),
                ('<s>', lambda e: self.__update_direc(Direc.DOWN)),
                ('<d>', lambda e: self.__update_direc(Direc.RIGHT)),
                ('<r>', lambda e: self.__reset()),
                ('<space>', lambda e: self.__toggle_pause())
            ))
            if self.__conf.mode == GameMode.NORMAL:
                window.show(self.__game_main_normal)
            elif self.__conf.mode == GameMode.TRAIN_DQN_GUI:
                window.show(self.__game_main_dqn_train)
                self.__plot_history()

    def __run_benchmarks(self):
        STEPS_LIMIT = 5000
        NUM_EPISODES = int(input("Please input the number of episodes: "))

        print("\nMap size: %dx%d" % (self.__conf.map_rows, self.__conf.map_cols))
        print("Solver: %s\n" % self.__conf.solver_name[:-6].lower())

        tot_suc, tot_suc_steps, tot_len = 0, 0, 0

        for _ in range(NUM_EPISODES):
            print("Episode %d - " % self.__episode, end="")
            while True:
                self.__game_main_normal()
                if self.__map.is_full():
                    tot_suc += 1
                    tot_suc_steps += self.__snake.steps
                    print("SUC (len: %d | steps: %d)"
                          % (self.__snake.len(), self.__snake.steps))
                    break
                elif self.__snake.dead:
                    print("DEAD (len: %d | steps: %d)"
                          % (self.__snake.len(), self.__snake.steps))
                    break
                elif self.__snake.steps >= STEPS_LIMIT:
                    print("STEP LIMIT (len: %d | steps: %d)"
                          % (self.__snake.len(), self.__snake.steps))
                    self.__write_logs()  # Write the last step
                    break
            tot_len += self.__snake.len()
            self.__reset()

        suc_rate = 100 * tot_suc / NUM_EPISODES
        avg_suc_steps = tot_suc_steps / tot_suc if tot_suc != 0 else -1
        avg_len = tot_len / NUM_EPISODES
        print("\n[Summary]\nSuccess: %d (%.2f%%)\nAverage Steps: %.2f\nAverage Length: %.2f\n"
              % (tot_suc, suc_rate, avg_suc_steps, avg_len))

        self.__on_exit()

    def __run_dqn_train(self):
        try:
            while True:
                self.__game_main_dqn_train()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()

    def __game_main_dqn_train(self):
        if not self.__map.has_food():
            self.__map.create_rand_food()

        if self.__pause:
            return

        episode_end = self.__solver.train()

        if episode_end:
            self.__reset()

    def __game_main_normal(self):
        if not self.__map.has_food():
            self.__map.create_rand_food()

        if self.__pause or self.__episode_end():
            return

        self.__update_direc(self.__solver.next_direc())

        if self.__conf.mode == GameMode.NORMAL and self.__snake.direc_next != Direc.NONE:
            self.__write_logs()

        self.__snake.move()

        if self.__episode_end():
            self.__write_logs()  # Write the last step

    def __plot_history(self):
        plt.figure()
        steps, history_loss = self.__solver.loss_history()
        plt.plot(steps, history_loss)
        plt.xlabel("Learn Step")
        plt.ylabel("Loss")
        plt.title("Loss")

        plt.figure()
        episodes, history_reward = self.__solver.reward_history()
        plt.plot(episodes, history_reward)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Total Reward")

        plt.figure()
        episodes, history_avg_reward = self.__solver.avg_reward_history()
        plt.plot(episodes, history_avg_reward)
        plt.xlabel("Learn Step")
        plt.ylabel("Reward")
        plt.title("Average Reward")

        plt.show()

    def __update_direc(self, new_direc):
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
