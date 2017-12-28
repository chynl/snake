#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,E1101


from snake.base import Direc
from snake.solver.base import BaseSolver


class DQNSolver(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)

    def next_direc(self):
        """Generate the next direction of the snake."""
        return Direc.RIGHT
