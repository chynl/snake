#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

from snake.solver.base import BaseSolver


class GreedySolver(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)

    def next_direc(self):
        return self.snake.direc
