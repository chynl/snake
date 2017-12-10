#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import tkinter as tk
from snake.base import Pos, PointType


class GameWindow(tk.Tk):

    def __init__(self, m, conf, keybindings=None):
        super().__init__()
        super().title("Snake")
        super().resizable(width=False, height=False)
        self.__map = m
        self.__conf = conf
        self.__grid_width = conf.window_width / conf.map_cols
        self.__grid_height = conf.window_height / conf.map_rows
        self.__canvas = tk.Canvas(self, bg=conf.color_bg,
                                  width=conf.window_width,
                                  height=conf.window_height,
                                  highlightthickness=0)
        self.__canvas.pack()
        self.__destroyed = False
        self.bind('<Escape>', lambda e: self.__quit())
        self.protocol('WM_DELETE_WINDOW', self.__quit)
        if keybindings is not None:
            for kb in keybindings:
                self.bind(kb[0], kb[1])

    def show(self):
        def draw():
            self.__update_contents()
            self.after(self.__conf.interval_draw, draw)
        self.after(100, draw)
        self.mainloop()

    @property
    def destroyed(self):
        return self.__destroyed

    def __quit(self):
        self.destroy()
        self.__destroyed = True

    def __update_contents(self):
        self.__draw_bg()
        for i in range(self.__conf.map_rows):
            for j in range(self.__conf.map_cols):
                self.__draw_grid(j * self.__grid_width,
                                 i * self.__grid_height,
                                 self.__map.point(Pos(i + 1, j + 1)).type)
        self.update()

    def __pad_ratio(self):
        return self.__conf.grid_pad_ratio

    def __draw_bg(self):
        self.__canvas.create_rectangle(0, 0,
                                       self.__conf.window_width,
                                       self.__conf.window_height,
                                       fill=self.__conf.color_bg,
                                       outline='')
        if self.__conf.show_grid_line:
            for i in range(1, self.__conf.map_rows):
                for j in range(1, self.__conf.map_cols):
                    x = j * self.__grid_width
                    y = i * self.__grid_height
                    self.__canvas.create_line(x,
                                              0,
                                              x,
                                              self.__conf.window_height,
                                              fill=self.__conf.color_grid_line)
                    self.__canvas.create_line(0,
                                              y,
                                              self.__conf.window_width,
                                              y,
                                              fill=self.__conf.color_grid_line)

    def __draw_grid(self, x, y, t):
        if t == PointType.WALL:
            self.__canvas.create_rectangle(x,
                                           y,
                                           x + self.__grid_width,
                                           y + self.__grid_height,
                                           fill=self.__conf.color_wall,
                                           outline='')
        elif t == PointType.FOOD:
            food_pad_ratio = 0.9 * self.__pad_ratio()
            self.__canvas.create_rectangle(x + food_pad_ratio * self.__grid_width,
                                           y + food_pad_ratio * self.__grid_height,
                                           x + (1 - food_pad_ratio) * self.__grid_width,
                                           y + (1 - food_pad_ratio) * self.__grid_height,
                                           fill=self.__conf.color_food,
                                           outline='')
        elif t == PointType.HEAD_L:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_head,
                                           outline='')
        elif t == PointType.HEAD_U:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + self.__grid_height,
                                           fill=self.__conf.color_head,
                                           outline='')
        elif t == PointType.HEAD_R:
            self.__canvas.create_rectangle(x,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_head,
                                           outline='')
        elif t == PointType.HEAD_D:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_head,
                                           outline='')
        elif t == PointType.BODY_LU:
            self.__canvas.create_rectangle(x,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__pad_ratio() * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
        elif t == PointType.BODY_UR:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
        elif t == PointType.BODY_RD:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
        elif t == PointType.BODY_DL:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
            self.__canvas.create_rectangle(x,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__pad_ratio() * self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
        elif t == PointType.BODY_HOR:
            self.__canvas.create_rectangle(x,
                                           y + self.__pad_ratio() * self.__grid_height,
                                           x + self.__grid_width,
                                           y + (1 - self.__pad_ratio()) * self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
        elif t == PointType.BODY_VER:
            self.__canvas.create_rectangle(x + self.__pad_ratio() * self.__grid_width,
                                           y,
                                           x + (1 - self.__pad_ratio()) * self.__grid_width,
                                           y + self.__grid_height,
                                           fill=self.__conf.color_body,
                                           outline='')
