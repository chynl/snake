#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103

from snake.base import Direc
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver


class _TableCell:

    def __init__(self):
        self.reset()

    def __str__(self):
        return "{ idx: %d  direc: %s }" % \
               (self.idx, self.direc)
    __repr__ = __str__

    def reset(self):
        self.idx = None
        self.direc = Direc.NONE


class HamiltonSolver(BaseSolver):

    def __init__(self, snake):
        if snake.map.num_rows % 2 != 0 or snake.map.num_cols % 2 != 0:
            raise ValueError("num_rows and num_cols must be even.")
        super().__init__(snake)
        self.__path_solver = PathSolver(snake)
        self.__table = [[_TableCell() for _ in range(snake.map.num_cols)]
                        for _ in range(snake.map.num_rows)]
        self.__build_cycle()

    @property
    def table(self):
        return self.__table

    def next_direc(self):
        """Generate the next direction of the snake."""
        head = self.snake.head()
        return self.__table[head.x][head.y].direc

    def __build_cycle(self):
        """Build a hamiltonian cycle on the map."""
        path = self.__path_solver.longest_path_to_tail()
        cur, cnt = self.snake.head(), 0
        for direc in path:
            self.__table[cur.x][cur.y].idx = cnt
            self.__table[cur.x][cur.y].direc = direc
            cur = cur.adj(direc)
            cnt += 1
        tail = self.snake.tail()
        self.__table[tail.x][tail.y].idx = cnt
        self.__table[tail.x][tail.y].direc = self.snake.direc
