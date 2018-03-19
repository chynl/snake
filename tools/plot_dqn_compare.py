#!/usr/bin/env python3
# -*- coding: utf-8 -*

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

COLOR_LEGEND_EDGE = (0 / 255, 0 / 255, 0 / 255)
BAR_WIDTH = 0.24

LABELS_EN = {
    "learn_step": "Learning Step (1e4)",
    "snake_len": "Average Snake Length",
    "snake_step": "Average Snake Step",
    "max": "Maximum",
    "global": "Global",
    "local": "Local",
    "absolute": "Absolute",
    "relative": "Relative", 
}

LABELS_ZH = {
    "learn_step": "迭代次数 (1e4)",
    "snake_len": "蛇的平均长度",
    "snake_step": "蛇的平均步数",
    "max": "最大值",
    "global": "全局",
    "local": "局部",
    "absolute": "绝对",
    "relative": "相对", 
}

LABELS = LABELS_EN

parser = argparse.ArgumentParser(description="Plot dqn performance comparation graphs.")
parser.add_argument("path", help="Path to history data directory")
parser.add_argument("-zh", action="store_true", help="use Chinese characters")
args = parser.parse_args()

if args.zh:
    LABELS = LABELS_ZH
    # Fix Chinese characters for matplotlib
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False


def plot_one(file_path, legend_name, interval=5000):
    data = np.load(file_path)
    x = (np.arange(data.size) + 1)[::interval] / 1e4
    y = data[::interval]
    plt.plot(x, y, label=legend_name)
    return np.max(data)


def add_decorations(y_label):
    plt.xlabel(LABELS["learn_step"])
    plt.ylabel(LABELS[y_label])
    plt.grid(linestyle="--", linewidth=0.5)
    plt.legend(loc="lower right", fancybox=False, edgecolor=COLOR_LEGEND_EDGE)


def make_bar(x, heights, side, color):
    if side == "l":
        xs = x - BAR_WIDTH / 2.
    elif side == "r":
        xs = x + BAR_WIDTH / 2.

    bars = plt.bar(xs, height=heights, width=BAR_WIDTH, alpha=0.4, color=color)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h,
                 "%.2f" % h, ha='center', va='bottom')

    return bars

legends = [
    "%s+%s" % (LABELS["global"], LABELS["absolute"]),
    "%s+%s" % (LABELS["global"], LABELS["relative"]),
    "%s+%s+%s" % (LABELS["global"], LABELS["local"], LABELS["absolute"]),
    "%s+%s+%s" % (LABELS["global"], LABELS["local"], LABELS["relative"]),
]

plt.figure()
max_len = \
plot_one(os.path.join(args.path, "len-dqn-visual-absolute.npy"), legends[0]), \
plot_one(os.path.join(args.path, "len-dqn-visual-relative.npy"), legends[1]), \
plot_one(os.path.join(args.path, "len-dqn-important-absolute.npy"), legends[2]), \
plot_one(os.path.join(args.path, "len-dqn-important-relative.npy"), legends[3])
add_decorations("snake_len")

plt.figure()
max_step = \
plot_one(os.path.join(args.path, "step-dqn-visual-absolute.npy"), legends[0]), \
plot_one(os.path.join(args.path, "step-dqn-visual-relative.npy"), legends[1]), \
plot_one(os.path.join(args.path, "step-dqn-important-absolute.npy"), legends[2]), \
plot_one(os.path.join(args.path, "step-dqn-important-relative.npy"), legends[3])
add_decorations("snake_step")

plt.figure()
x = np.arange(4)
bar_len = make_bar(x, max_len, "l", "r")
bar_step = make_bar(x, max_step, "r", "b")
plt.xticks(x, legends)
plt.ylabel(LABELS["max"])
plt.legend((bar_len[0], bar_step[0]), (LABELS["snake_len"], LABELS["snake_step"]),
           loc="lower right", fancybox=False, edgecolor=COLOR_LEGEND_EDGE)


interval = 100000

legends = [
    "DQN",
    "DQN+Prioritized",
    "DQN+Duel",
    "DQN+Prioritized+Duel",
    "Double",
    "Double+Prioritized",
    "Double+Duel",
    "Double+Prioritized+Duel",
]

plt.figure()
max_len_1 = \
plot_one(os.path.join(args.path, "len-dqn-important-relative.npy"), legends[0], interval), \
plot_one(os.path.join(args.path, "len-dqn-pri-important-relative.npy"), legends[1], interval), \
plot_one(os.path.join(args.path, "len-dqn-duel-important-relative.npy"), legends[2], interval), \
plot_one(os.path.join(args.path, "len-dqn-pri-duel-important-relative.npy"), legends[3], interval)
add_decorations("snake_len")

plt.figure()
max_step_1 = \
plot_one(os.path.join(args.path, "step-dqn-important-relative.npy"), legends[0], interval), \
plot_one(os.path.join(args.path, "step-dqn-pri-important-relative.npy"), legends[1], interval), \
plot_one(os.path.join(args.path, "step-dqn-duel-important-relative.npy"), legends[2], interval), \
plot_one(os.path.join(args.path, "step-dqn-pri-duel-important-relative.npy"), legends[3], interval)
add_decorations("snake_step")

plt.figure()
max_len_2 = \
plot_one(os.path.join(args.path, "len-ddqn-important-relative.npy"), legends[4], interval), \
plot_one(os.path.join(args.path, "len-ddqn-pri-important-relative.npy"), legends[5], interval), \
plot_one(os.path.join(args.path, "len-ddqn-duel-important-relative.npy"), legends[6], interval), \
plot_one(os.path.join(args.path, "len-ddqn-pri-duel-important-relative.npy"), legends[7], interval)
add_decorations("snake_len")

plt.figure()
max_step_2 = \
plot_one(os.path.join(args.path, "step-ddqn-important-relative.npy"), legends[4], interval), \
plot_one(os.path.join(args.path, "step-ddqn-pri-important-relative.npy"), legends[5], interval), \
plot_one(os.path.join(args.path, "step-ddqn-duel-important-relative.npy"), legends[6], interval), \
plot_one(os.path.join(args.path, "step-ddqn-pri-duel-important-relative.npy"), legends[7], interval)
add_decorations("snake_step")

plt.figure()
x = np.arange(8)
bar_len = make_bar(x, max_len_1 + max_len_2, "l", "r")
bar_step = make_bar(x, max_step_1 + max_step_2, "r", "b")
plt.xticks(x, legends)
plt.ylabel(LABELS["max"])
plt.legend((bar_len[0], bar_step[0]), (LABELS["snake_len"], LABELS["snake_step"]),
           loc="lower right", fancybox=False, edgecolor=COLOR_LEGEND_EDGE)

plt.show()
