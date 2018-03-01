#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import tkinter as tk
from snake.base import Pos, PointType


class GameWindow(tk.Tk):

    def __init__(self, title, conf, game_map, game=None, on_exit=None, keybindings=None):
        super().__init__()
        super().title(title)
        super().resizable(width=False, height=False)
        super().configure(background=conf.color_bg)
        if conf.show_info_panel:
            super().geometry("%dx%d" % (conf.window_width, conf.window_height))

        self._conf = conf
        self._map = game_map
        self._grid_width = conf.map_width / (game_map.num_rows - 2)
        self._grid_height = conf.map_height / (game_map.num_cols - 2)
        self._init_widgets()
        self._init_draw_params()

        if game is not None:
            self._game = game
            self._snake = game.snake

        def on_destroy():
            if callable(on_exit):
                on_exit()
            self.destroy()

        self._init_keybindings(keybindings, on_destroy)

    def show(self, game_loop=None):
        def cb():
            if callable(game_loop):
                game_loop()
            self._update_contents()
            self.after(self._conf.interval_draw, cb)
        self.after(100, cb)
        self.mainloop()

    def _init_widgets(self):
        self._canvas = tk.Canvas(self,
                                 bg=self._conf.color_bg,
                                 width=self._conf.map_width,
                                 height=self._conf.map_height,
                                 highlightthickness=0)
        self._canvas.pack(side=tk.LEFT)

        if self._conf.show_info_panel:

            self._info_var = tk.StringVar()

            frm = tk.Frame(self, bg=self._conf.color_bg)
            frm.pack(side=tk.RIGHT, anchor=tk.N)

            tk.Message(frm,
                       textvariable=self._info_var,
                       fg=self._conf.color_txt,
                       bg=self._conf.color_bg,
                       font=self._conf.font_info).pack(side=tk.TOP, anchor=tk.W)

            scale = tk.Scale(frm,
                             font=self._conf.font_info,
                             fg=self._conf.color_txt,
                             bg=self._conf.color_bg,
                             highlightthickness=0,
                             from_=self._conf.interval_draw_max,
                             to=0,
                             orient=tk.HORIZONTAL,
                             length=self._conf.window_width - self._conf.map_width,
                             showvalue=False,
                             tickinterval=0,
                             resolution=1,
                             command=self._update_speed)
            scale.pack(side=tk.TOP, anchor=tk.W)
            scale.set(self._conf.interval_draw)

    def _update_speed(self, speed):
        self._conf.interval_draw = int(speed)

    def _init_keybindings(self, keybindings, on_destroy):
        self.bind('<Escape>', lambda e: on_destroy())
        self.protocol('WM_DELETE_WINDOW', on_destroy)
        if keybindings:
            for kb in keybindings:
                self.bind(kb[0], kb[1])

    def _init_draw_params(self):
        pad_ratio = self._conf.grid_pad_ratio
        food_pad_ratio = 0.9 * pad_ratio
        self._dx1 = pad_ratio * self._grid_width
        self._dx2 = (1 - pad_ratio) * self._grid_width + 1
        self._dy1 = pad_ratio * self._grid_height
        self._dy2 = (1 - pad_ratio) * self._grid_height + 1
        self._dx1_food = food_pad_ratio * self._grid_width
        self._dx2_food = (1 - food_pad_ratio) * self._grid_width
        self._dy1_food = food_pad_ratio * self._grid_height
        self._dy2_food = (1 - food_pad_ratio) * self._grid_height

    def _update_contents(self):
        self._canvas.delete(tk.ALL)
        self._draw_bg()
        if self._conf.show_grid_line:
            self._draw_grid_line()
        if self._conf.show_info_panel:
            self._draw_info_panel()
        self._draw_map_contents()
        self.update()

    def _draw_bg(self):
        self._canvas.create_rectangle(0, 0, self._conf.map_width, self._conf.map_height,
                                      fill=self._conf.color_bg, outline='')

    def _draw_grid_line(self):
        for i in range(1, self._map.num_rows - 2):
            for j in range(1, self._map.num_cols - 2):
                x = j * self._grid_width
                y = i * self._grid_height
                self._canvas.create_line(x, 0,
                                         x, self._conf.map_height,
                                         fill=self._conf.color_line)
                self._canvas.create_line(0, y,
                                         self._conf.map_width, y,
                                         fill=self._conf.color_line)

    def _draw_info_panel(self):
        self._canvas.create_line(self._conf.map_width - 1, 0,
                                 self._conf.map_width - 1, self._conf.map_height,
                                 fill=self._conf.color_line)

        if self._snake.dead:
            status_str = self._conf.info_status[1]
        elif self._map.is_full():
            status_str = self._conf.info_status[2]
        else:
            status_str = self._conf.info_status[0]

        self._info_var.set(self._conf.info_str %
                            (status_str,
                             self._game.episode, self._snake.steps,
                             self._snake.len(), self._map.capacity))

    def _draw_map_contents(self):
        for i in range(self._map.num_rows - 2):
            for j in range(self._map.num_cols - 2):
                self._draw_grid(j * self._grid_width, i * self._grid_height,
                                self._map.point(Pos(i + 1, j + 1)).type)

    def _draw_grid(self, x, y, t):
        if t == PointType.WALL:
            self._canvas.create_rectangle(x, y,
                                          x + self._grid_width, y + self._grid_height,
                                          fill=self._conf.color_wall, outline='')
        elif t == PointType.FOOD:
            self._canvas.create_rectangle(x + self._dx1_food, y + self._dy1_food,
                                          x + self._dx2_food, y + self._dy2_food,
                                          fill=self._conf.color_food, outline='')
        elif t == PointType.HEAD_L:
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._grid_width, y + self._dy2,
                                          fill=self._conf.color_head, outline='')
        elif t == PointType.HEAD_U:
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._dx2, y + self._grid_height,
                                          fill=self._conf.color_head, outline='')
        elif t == PointType.HEAD_R:
            self._canvas.create_rectangle(x, y + self._dy1,
                                          x + self._dx2, y + self._dy2,
                                          fill=self._conf.color_head, outline='')
        elif t == PointType.HEAD_D:
            self._canvas.create_rectangle(x + self._dx1, y,
                                          x + self._dx2, y + self._dy2,
                                          fill=self._conf.color_head, outline='')
        elif t == PointType.BODY_LU:
            self._canvas.create_rectangle(x, y + self._dy1,
                                          x + self._dx1, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
            self._canvas.create_rectangle(x + self._dx1, y,
                                          x + self._dx2, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
        elif t == PointType.BODY_UR:
            self._canvas.create_rectangle(x + self._dx1, y,
                                          x + self._dx2, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._grid_width, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
        elif t == PointType.BODY_RD:
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._grid_width, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._dx2, y + self._grid_height,
                                          fill=self._conf.color_body, outline='')
        elif t == PointType.BODY_DL:
            self._canvas.create_rectangle(x + self._dx1, y + self._dy1,
                                          x + self._dx2, y + self._grid_height,
                                          fill=self._conf.color_body, outline='')
            self._canvas.create_rectangle(x, y + self._dy1,
                                          x + self._dx1, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
        elif t == PointType.BODY_HOR:
            self._canvas.create_rectangle(x, y + self._dy1,
                                          x + self._grid_width, y + self._dy2,
                                          fill=self._conf.color_body, outline='')
        elif t == PointType.BODY_VER:
            self._canvas.create_rectangle(x + self._dx1, y,
                                          x + self._dx2, y + self._grid_height,
                                          fill=self._conf.color_body, outline='')
