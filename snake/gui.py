#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import tkinter as tk


class GameWindow(tk.Tk):

    def __init__(self, m):
        super().__init__()
        super().title("Snake")
        super().resizable(width=False, height=False)
        self.__map = m
        self.__canvas = tk.Canvas(self, bg='black', width=300, height=300,
                                  highlightthickness=0)
        self.__canvas.pack()

    def render(self):
        self.update()
