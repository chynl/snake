#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103

import random
from snake.base import Direc, Pos, PointType, Map
from snake.solver.base import BaseSolver


class _CycleTableCell:

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
        self.__table = [[_CycleTableCell() for _ in range(snake.map.num_cols)]
                        for _ in range(snake.map.num_rows)]
        self.__maze_map = Map(self.snake.map.num_rows - 1, self.snake.map.num_cols - 1)
        self.__maze_visit = [[False for _ in range(self.__maze_map.num_cols)]
                             for _ in range(self.__maze_map.num_rows)]
        self.__build_cycle()

    @property
    def maze_map(self):
        return self.__maze_map

    def next_direc(self):
        """Generate the next direction of the snake."""
        return NotImplemented

    def __build_cycle(self):
        """Build a hamiltonian cycle on the map."""
        # Generate a maze
        self.__reset_maze_attr()
        self.__dfs_break_walls(HamiltonSolver.__to_maze_pos(self.snake.head()))

    @staticmethod
    def __to_maze_pos(pos):
        return Pos(HamiltonSolver.__to_maze_xy(pos.x), HamiltonSolver.__to_maze_xy(pos.y))

    @staticmethod
    def __to_maze_xy(xy):
        return 2 * ((xy + 1) // 2) - 1

    def __reset_maze_attr(self):
        for i in range(1, self.__maze_map.num_rows - 1):
            if i % 2 == 0:
                cols = range(1, self.__maze_map.num_cols - 1)
            else:
                cols = range(2, self.__maze_map.num_cols - 1, 2)
            for j in cols:
                self.__maze_map.point(Pos(i, j)).type = PointType.WALL
        for i in range(self.__maze_map.num_rows):
            for j in range(self.__maze_map.num_cols):
                self.__maze_visit[i][j] = False

    def __dfs_break_walls(self, cur):
        self.__maze_visit[cur.x][cur.y] = True
        direcs = [Direc.LEFT, Direc.UP, Direc.RIGHT, Direc.DOWN]
        random.shuffle(direcs)
        for direc in direcs:
            wall = cur.adj(direc)
            if self.__maze_map.is_inside(wall):
                adj = wall.adj(direc)
                if not self.__maze_visit[adj.x][adj.y]:
                    self.__maze_map.point(wall).type = PointType.EMPTY  # Break the wall
                    self.__dfs_break_walls(adj)
