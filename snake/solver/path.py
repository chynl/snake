#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

import sys
import random
from collections import deque


class _TableCell:

    def __init__(self):
        self.reset()

    def __str__(self):
        return "{ dist: %d  parent: %s }" % (self.dist, str(self.parent))
    __repr__ = __str__

    def reset(self):
        self.parent = None
        self.dist = sys.maxsize


class PathSolver:

    def __init__(self, snake):
        self.__snake = snake
        self.__map = snake.map
        self.__table = [[_TableCell() for _ in range(snake.map.num_cols)]
                        for _ in range(snake.map.num_rows)]

    @property
    def table(self):
        return self.__table

    def shortest_path_to(self, des):
        """Find the shortest path from the snake's head to the destination.

        Args:
            des (snake.base.pos.Pos): The destination position on the map.

        Returns:
            A collections.deque of snake.base.direc.Direc indicating the path directions.

        """
        for row in self.__table:
            for col in row:
                col.reset()

        head = self.__snake.head()
        self.__table[head.x][head.y].dist = 0
        queue = deque()
        queue.append(head)

        while queue:
            cur_pos = queue.popleft()
            if cur_pos == des:
                return self.__build_path(head, des)

            # Arrange the order of traverse to make the path as straight as possible
            if cur_pos == head:
                first_direc = self.__snake.direc
            else:
                first_direc = self.__table[cur_pos.x][cur_pos.y].parent.direc_to(cur_pos)
            adjs = cur_pos.all_adj()
            random.shuffle(adjs)
            for i, pos in enumerate(adjs):
                if first_direc == cur_pos.direc_to(pos):
                    adjs[0], adjs[i] = adjs[i], adjs[0]
                    break

            # Traverse adjacent positions
            for pos in adjs:
                if self.__map.is_safe(pos):
                    adj_cell = self.__table[pos.x][pos.y]
                    if adj_cell.dist == sys.maxsize:
                        adj_cell.parent = cur_pos
                        adj_cell.dist = self.__table[cur_pos.x][cur_pos.y].dist + 1
                        queue.append(pos)

    def __build_path(self, src, des):
        path = deque()
        tmp = des
        while tmp != src:
            parent = self.__table[tmp.x][tmp.y].parent
            path.appendleft(parent.direc_to(tmp))
            tmp = parent
        return path
