#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,E1101

import sys
import random
from collections import deque
from snake.base import Direc


class _TableCell:

    def __init__(self):
        self.reset()

    def __str__(self):
        return "{ dist: %d  parent: %s  visit: %d }" % \
               (self.dist, str(self.parent), self.visit)
    __repr__ = __str__

    def reset(self):
        # Shortest path
        self.parent = None
        self.dist = sys.maxsize
        # Longest path
        self.visit = False


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
        self.__reset_table()

        head = self.__snake.head()
        self.__table[head.x][head.y].dist = 0
        queue = deque()
        queue.append(head)

        while queue:
            cur = queue.popleft()
            if cur == des:
                return self.__build_path(head, des)

            # Arrange the order of traverse to make the path as straight as possible
            if cur == head:
                first_direc = self.__snake.direc
            else:
                first_direc = self.__table[cur.x][cur.y].parent.direc_to(cur)
            adjs = cur.all_adj()
            random.shuffle(adjs)
            for i, pos in enumerate(adjs):
                if first_direc == cur.direc_to(pos):
                    adjs[0], adjs[i] = adjs[i], adjs[0]
                    break

            # Traverse adjacent positions
            for pos in adjs:
                if self.__is_valid(pos):
                    adj_cell = self.__table[pos.x][pos.y]
                    if adj_cell.dist == sys.maxsize:
                        adj_cell.parent = cur
                        adj_cell.dist = self.__table[cur.x][cur.y].dist + 1
                        queue.append(pos)

        return deque()

    def longest_path_to(self, des):
        """Find the longest path from the snake's head to the destination.

        Args:
            des (snake.base.pos.Pos): The destination position on the map.

        Returns:
            A collections.deque of snake.base.direc.Direc indicating the path directions.

        """
        path = self.shortest_path_to(des)
        if not path:
            return deque()

        self.__reset_table()
        cur = head = self.__snake.head()

        # Set all positions on the shortest path to 'visited'
        self.__table[cur.x][cur.y].visit = True
        for direc in path:
            cur = cur.adj(direc)
            self.__table[cur.x][cur.y].visit = True

        # Extend the path between each pair of the positions
        idx, cur = 0, head
        while True:
            cur_direc = path[idx]
            nxt = cur.adj(cur_direc)

            if cur_direc == Direc.LEFT or cur_direc == Direc.RIGHT:
                tests = [Direc.UP, Direc.DOWN]
            elif cur_direc == Direc.UP or cur_direc == Direc.DOWN:
                tests = [Direc.LEFT, Direc.RIGHT]

            extended = False
            for test_direc in tests:
                cur_test = cur.adj(test_direc)
                nxt_test = nxt.adj(test_direc)
                if self.__is_valid(cur_test) and self.__is_valid(nxt_test):
                    self.__table[cur_test.x][cur_test.y].visit = True
                    self.__table[nxt_test.x][nxt_test.y].visit = True
                    path.insert(idx, test_direc)
                    path.insert(idx + 2, Direc.opposite(test_direc))
                    extended = True
                    break

            if not extended:
                cur = nxt
                idx += 1
                if idx >= len(path):
                    break

        return path

    def __reset_table(self):
        for row in self.__table:
            for col in row:
                col.reset()

    def __build_path(self, src, des):
        path = deque()
        tmp = des
        while tmp != src:
            parent = self.__table[tmp.x][tmp.y].parent
            path.appendleft(parent.direc_to(tmp))
            tmp = parent
        return path

    def __is_valid(self, pos):
        return self.__map.is_safe(pos) and not self.__table[pos.x][pos.y].visit
