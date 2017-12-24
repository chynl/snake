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

    def __init__(self, snake, shortcuts=True):
        if snake.map.num_rows % 2 != 0 or snake.map.num_cols % 2 != 0:
            raise ValueError("num_rows and num_cols must be even.")
        super().__init__(snake)
        self.__shortcuts = shortcuts
        self.__path_solver = PathSolver(snake)
        self.__table = [[_TableCell() for _ in range(snake.map.num_cols)]
                        for _ in range(snake.map.num_rows)]
        self.__build_cycle()

    @property
    def table(self):
        return self.__table

    def next_direc(self):
        head = self.snake.head()
        nxt_direc = self.__table[head.x][head.y].direc

        # Take shorcuts when the snake is not too long
        if self.__shortcuts and self.map.capacity - self.snake.len() > 10:
            path = self.__path_solver.shortest_path_to_food()
            if path:
                tail, nxt, food = self.snake.tail(), head.adj(path[0]), self.map.food
                tail_idx = self.__table[tail.x][tail.y].idx
                head_idx = self.__table[head.x][head.y].idx
                nxt_idx = self.__table[nxt.x][nxt.y].idx
                food_idx = self.__table[food.x][food.y].idx
                # Exclude one exception
                if not (len(path) == 1 and abs(food_idx - tail_idx) == 1):
                    head_idx_rel = self.__relative_dist(tail_idx, head_idx, self.map.capacity)
                    nxt_idx_rel = self.__relative_dist(tail_idx, nxt_idx, self.map.capacity)
                    food_idx_rel = self.__relative_dist(tail_idx, food_idx, self.map.capacity)
                    if nxt_idx_rel > head_idx_rel and nxt_idx_rel <= food_idx_rel:
                        nxt_direc = path[0]

        return nxt_direc

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

    def __relative_dist(self, ori, x, size):
        if ori > x:
            x += size
        return x - ori
