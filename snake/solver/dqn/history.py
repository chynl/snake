#!/usr/bin/env python3
# -*- coding: utf-8 -*--

import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from snake.solver.dqn.logger import log

_DIR_LOG = "logs"


class History:

    PATH_DATA = os.path.join(_DIR_LOG, "history-%s-%d-%d.npy")

    def __init__(self, num_avg):
        self._NUM_AVG = num_avg
        self._X_SCALE = 1e-4
        self._COLOR_FILL = (240 / 255, 240 / 255, 240 / 255)
        self._COLOR_LEGEND_EDGE = (0 / 255, 0 / 255, 0 / 255)

        self._tot_reward = 0
        self._max_avg_len = 0.0

        self._history_loss = []

        self._history_reward = []
        self._history_len = []
        self._history_step = []

        self._history_avg_reward = []
        self._history_avg_len = []
        self._history_avg_step = []

        self._history_min_reward = []
        self._history_min_len = []
        self._history_min_step = []

        self._history_max_reward = []
        self._history_max_len = []
        self._history_max_step = []

    def add_loss(self, loss):
        self._history_loss.append(loss)

    def add_snake_step(self, done, reward, snake):
        self._tot_reward += reward
        if done:  # Episode ends
            self._history_reward.append(self._tot_reward)
            self._history_len.append(snake.len())
            self._history_step.append(snake.steps)
            self._tot_reward = 0

    def add_learn_step(self):
        avg_reward, min_reward, max_reward = [0.0] * 3
        if self._history_reward:
            chunks = self._history_reward[-self._NUM_AVG:]
            avg_reward = np.mean(chunks)
            min_reward = np.min(chunks)
            max_reward = np.max(chunks)
        self._history_avg_reward.append(avg_reward)
        self._history_min_reward.append(min_reward)
        self._history_max_reward.append(max_reward)

        avg_len, min_len, max_len =[self._max_avg_len] * 3
        if self._history_len:
            chunks = self._history_len[-self._NUM_AVG:]
            avg_len = np.mean(chunks)
            min_len = np.min(chunks)
            max_len = np.max(chunks)
        self._history_avg_len.append(avg_len)
        self._history_min_len.append(min_len)
        self._history_max_len.append(max_len)

        avg_steps, min_steps, max_steps = [0.0] * 3
        if self._history_step:
            chunks = self._history_step[-self._NUM_AVG:]
            avg_steps = np.mean(chunks)
            min_steps = np.min(chunks)
            max_steps = np.max(chunks)
        self._history_avg_step.append(avg_steps)
        self._history_min_step.append(min_steps)
        self._history_max_step.append(max_steps)

        new_max_avg_len = avg_len > self._max_avg_len
        if new_max_avg_len:
            self._max_avg_len = avg_len

        return avg_reward, avg_len, avg_steps, new_max_avg_len

    def plot(self, beg_step):
        title = "Loss"
        plt.figure(num=title)
        steps = np.arange(len(self._history_loss)) + beg_step
        plt.plot(steps, self._history_loss)
        plt.xlabel("Learning Step")
        plt.ylabel("Loss")

        self._plot_avg(beg_step, "Reward", "green",
                       self._history_avg_reward,
                       self._history_min_reward,
                       self._history_max_reward)

        self._plot_avg(beg_step, "Snake Length", "red",
                       self._history_avg_len,
                       self._history_min_len,
                       self._history_max_len)

        self._plot_avg(beg_step, "Snake Step", "blue",
                       self._history_avg_step,
                       self._history_min_step,
                       self._history_max_step)

        plt.show()

    def save(self, beg_step, end_step):
        log("Saving history...")
        np.save(History.PATH_DATA % ("loss", beg_step, end_step), self._history_loss)
        np.save(History.PATH_DATA % ("avg-reward", beg_step, end_step), self._history_avg_reward)
        np.save(History.PATH_DATA % ("min-reward", beg_step, end_step), self._history_min_reward)
        np.save(History.PATH_DATA % ("max-reward", beg_step, end_step), self._history_max_reward)
        np.save(History.PATH_DATA % ("avg-len", beg_step, end_step), self._history_avg_len)
        np.save(History.PATH_DATA % ("min-len", beg_step, end_step), self._history_min_len)
        np.save(History.PATH_DATA % ("max-len", beg_step, end_step), self._history_max_len)
        np.save(History.PATH_DATA % ("avg-step", beg_step, end_step), self._history_avg_step)
        np.save(History.PATH_DATA % ("min-step", beg_step, end_step), self._history_min_step)
        np.save(History.PATH_DATA % ("max-step", beg_step, end_step), self._history_max_step)

    def load(self, beg_step, end_step):
        log("Loading history...")
        self._history_loss = np.load(History.PATH_DATA % ("loss", beg_step, end_step))
        self._history_avg_reward = np.load(History.PATH_DATA % ("avg-reward", beg_step, end_step))
        self._history_min_reward = np.load(History.PATH_DATA % ("min-reward", beg_step, end_step))
        self._history_max_reward = np.load(History.PATH_DATA % ("max-reward", beg_step, end_step))
        self._history_avg_len = np.load(History.PATH_DATA % ("avg-len", beg_step, end_step))
        self._history_min_len = np.load(History.PATH_DATA % ("min-len", beg_step, end_step))
        self._history_max_len = np.load(History.PATH_DATA % ("max-len", beg_step, end_step))
        self._history_avg_step = np.load(History.PATH_DATA % ("avg-step", beg_step, end_step))
        self._history_min_step = np.load(History.PATH_DATA % ("min-step", beg_step, end_step))
        self._history_max_step = np.load(History.PATH_DATA % ("max-step", beg_step, end_step))

    def _plot_avg(self, learn_step_beg, name, color, data_avg, data_min, data_max):
        plt.figure(num=name)

        steps = (np.arange(len(data_avg)) + learn_step_beg) * self._X_SCALE
        plt.fill_between(steps, data_min, data_max, color=self._COLOR_FILL, label="Min/Max")
        plt.plot(steps, data_avg, "-", color=color, linewidth=0.5, label="Average")

        plt.xlabel("Learning Step (1e4)")
        plt.ylabel(name)

        plt.legend(loc="upper left", fancybox=False, edgecolor=self._COLOR_LEGEND_EDGE)

        x_max_max = (np.argmax(data_max) + learn_step_beg) * self._X_SCALE
        y_max_max = np.max(data_max)
        x_max_avg = (np.argmax(data_avg) + learn_step_beg) * self._X_SCALE
        y_max_avg = np.max(data_avg)

        plt.annotate("Max: %.2f" % y_max_max,
                     xy=(x_max_max, y_max_max), xytext=(-50, -25),
                     textcoords="offset points",
                     arrowprops=dict(facecolor="black", arrowstyle="->"))
        plt.annotate("Max: %.2f" % y_max_avg,
                     xy=(x_max_avg, y_max_avg), xytext=(-50, 20),
                     textcoords="offset points",
                     arrowprops=dict(facecolor="black", arrowstyle="->"))
