#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import tkinter as tk
from snake.base import Pos, PointType


class GameWindow(tk.Tk):

    def __init__(self, conf, m, s=None, on_exit=None, keybindings=None):
        super().__init__()
        super().title("Snake")
        super().resizable(width=False, height=False)
        super().configure(background=conf.color_bg)
        if conf.show_info_panel:
            super().geometry("%dx%d" % (conf.window_width, conf.window_height))
        self.__conf = conf
        self.__map = m
        self.__snake = s
        self.__grid_width = conf.map_width / conf.map_cols
        self.__grid_height = conf.map_height / conf.map_rows
        self.__init_widgets()
        self.__init_draw_params()

        def on_destroy():
            if callable(on_exit):
                on_exit()
            self.destroy()

        self.__init_keybindings(keybindings, on_destroy)

    def show(self, game_loop=None):
        def cb():
            if callable(game_loop):
                game_loop()
            self.__update_contents()
            self.after(self.__conf.interval_draw, cb)
        self.after(100, cb)
        self.mainloop()

    def __init_widgets(self):
        self.__canvas = tk.Canvas(self, bg=self.__conf.color_bg,
                                  width=self.__conf.map_width,
                                  height=self.__conf.map_height,
                                  highlightthickness=0)
        self.__canvas.pack(side=tk.LEFT)
        if self.__conf.show_info_panel:
            self.__info_var = tk.StringVar()
            tk.Message(self,
                       textvariable=self.__info_var,
                       fg=self.__conf.color_txt,
                       bg=self.__conf.color_bg,
                       font=self.__conf.font_info) \
            .place(x=self.__conf.map_width, y=0)

    def __init_keybindings(self, keybindings, on_destroy):
        self.bind('<Escape>', lambda e: on_destroy())
        self.protocol('WM_DELETE_WINDOW', on_destroy)
        if keybindings:
            for kb in keybindings:
                self.bind(kb[0], kb[1])

    def __init_draw_params(self):
        pad_ratio = self.__conf.grid_pad_ratio
        food_pad_ratio = 0.9 * pad_ratio
        self.__dx1 = pad_ratio * self.__grid_width
        self.__dx2 = (1 - pad_ratio) * self.__grid_width
        self.__dy1 = pad_ratio * self.__grid_height
        self.__dy2 = (1 - pad_ratio) * self.__grid_height
        self.__dx1_food = food_pad_ratio * self.__grid_width
        self.__dx2_food = (1 - food_pad_ratio) * self.__grid_width
        self.__dy1_food = food_pad_ratio * self.__grid_height
        self.__dy2_food = (1 - food_pad_ratio) * self.__grid_height

    def __update_contents(self):
        self.__canvas.delete(tk.ALL)
        self.__draw_bg()
        if self.__conf.show_grid_line:
            self.__draw_grid_line()
        if self.__conf.show_info_panel:
            self.__draw_info_panel()
        self.__draw_map_contents()
        self.update()

    def __draw_bg(self):
        self.__canvas.create_rectangle(0, 0, self.__conf.map_width, self.__conf.map_height,
                                       fill=self.__conf.color_bg, outline='')

    def __draw_grid_line(self):
        for i in range(1, self.__conf.map_rows):
            for j in range(1, self.__conf.map_cols):
                x = j * self.__grid_width
                y = i * self.__grid_height
                self.__canvas.create_line(x, 0,
                                          x, self.__conf.map_height,
                                          fill=self.__conf.color_line)
                self.__canvas.create_line(0, y,
                                          self.__conf.map_width, y,
                                          fill=self.__conf.color_line)

    def __draw_info_panel(self):
        self.__canvas.create_line(self.__conf.map_width - 1, 0,
                                  self.__conf.map_width - 1, self.__conf.map_height,
                                  fill=self.__conf.color_line)
        # Info str
        if self.__snake.dead:
            status_str = self.__conf.info_status[1]
        elif self.__map.is_full():
            status_str = self.__conf.info_status[2]
        else:
            status_str = self.__conf.info_status[0]
        self.__info_var.set(self.__conf.info_str %
                            (status_str,
                             self.__snake.steps,
                             self.__snake.len(), self.__map.capacity))

    def __draw_map_contents(self):
        for i in range(self.__conf.map_rows):
            for j in range(self.__conf.map_cols):
                self.__draw_grid(j * self.__grid_width, i * self.__grid_height,
                                 self.__map.point(Pos(i + 1, j + 1)).type)

    def __draw_grid(self, x, y, t):
        if t == PointType.WALL:
            self.__canvas.create_rectangle(x, y,
                                           x + self.__grid_width, y + self.__grid_height,
                                           fill=self.__conf.color_wall, outline='')
        elif t == PointType.FOOD:
            self.__canvas.create_rectangle(x + self.__dx1_food, y + self.__dy1_food,
                                           x + self.__dx2_food, y + self.__dy2_food,
                                           fill=self.__conf.color_food, outline='')
        elif t == PointType.HEAD_L:
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__grid_width, y + self.__dy2,
                                           fill=self.__conf.color_head, outline='')
        elif t == PointType.HEAD_U:
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__dx2, y + self.__grid_height,
                                           fill=self.__conf.color_head, outline='')
        elif t == PointType.HEAD_R:
            self.__canvas.create_rectangle(x, y + self.__dy1,
                                           x + self.__dx2, y + self.__dy2,
                                           fill=self.__conf.color_head, outline='')
        elif t == PointType.HEAD_D:
            self.__canvas.create_rectangle(x + self.__dx1, y,
                                           x + self.__dx2, y + self.__dy2,
                                           fill=self.__conf.color_head, outline='')
        elif t == PointType.BODY_LU:
            self.__canvas.create_rectangle(x, y + self.__dy1,
                                           x + self.__dx1, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
            self.__canvas.create_rectangle(x + self.__dx1, y,
                                           x + self.__dx2, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
        elif t == PointType.BODY_UR:
            self.__canvas.create_rectangle(x + self.__dx1, y,
                                           x + self.__dx2, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__grid_width, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
        elif t == PointType.BODY_RD:
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__grid_width, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__dx2, y + self.__grid_height,
                                           fill=self.__conf.color_body, outline='')
        elif t == PointType.BODY_DL:
            self.__canvas.create_rectangle(x + self.__dx1, y + self.__dy1,
                                           x + self.__dx2, y + self.__grid_height,
                                           fill=self.__conf.color_body, outline='')
            self.__canvas.create_rectangle(x, y + self.__dy1,
                                           x + self.__dx1, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
        elif t == PointType.BODY_HOR:
            self.__canvas.create_rectangle(x, y + self.__dy1,
                                           x + self.__grid_width, y + self.__dy2,
                                           fill=self.__conf.color_body, outline='')
        elif t == PointType.BODY_VER:
            self.__canvas.create_rectangle(x + self.__dx1, y,
                                           x + self.__dx2, y + self.__grid_height,
                                           fill=self.__conf.color_body, outline='')
