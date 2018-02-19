#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,E1101

import sys
import random
from collections import deque
from snake.base import Direc, PointType
from snake.solver.base import BaseSolver


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


class PathSolver(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)
        self._table = [[_TableCell() for _ in range(snake.map.num_cols)]
                       for _ in range(snake.map.num_rows)]

    @property
    def table(self):
        return self._table

    def shortest_path_to_food(self):
        return self.path_to(self.map.food, "shortest")

    def longest_path_to_tail(self):
        return self.path_to(self.snake.tail(), "longest")

    def path_to(self, des, path_type):
        ori_type = self.map.point(des).type
        self.map.point(des).type = PointType.EMPTY
        if path_type == "shortest":
            path = self.shortest_path_to(des)
        elif path_type == "longest":
            path = self.longest_path_to(des)
        self.map.point(des).type = ori_type  # Restore origin type
        return path

    def shortest_path_to(self, des):
        """Find the shortest path from the snake's head to the destination.

        Args:
            des (snake.base.pos.Pos): The destination position on the map.

        Returns:
            A collections.deque of snake.base.direc.Direc indicating the path directions.

        """
        self._reset_table()

        head = self.snake.head()
        self._table[head.x][head.y].dist = 0
        queue = deque()
        queue.append(head)

        while queue:
            cur = queue.popleft()
            if cur == des:
                return self._build_path(head, des)

            # Arrange the order of traverse to make the path as straight as possible
            if cur == head:
                first_direc = self.snake.direc
            else:
                first_direc = self._table[cur.x][cur.y].parent.direc_to(cur)
            adjs = cur.all_adj()
            random.shuffle(adjs)
            for i, pos in enumerate(adjs):
                if first_direc == cur.direc_to(pos):
                    adjs[0], adjs[i] = adjs[i], adjs[0]
                    break

            # Traverse adjacent positions
            for pos in adjs:
                if self._is_valid(pos):
                    adj_cell = self._table[pos.x][pos.y]
                    if adj_cell.dist == sys.maxsize:
                        adj_cell.parent = cur
                        adj_cell.dist = self._table[cur.x][cur.y].dist + 1
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

        self._reset_table()
        cur = head = self.snake.head()

        # Set all positions on the shortest path to 'visited'
        self._table[cur.x][cur.y].visit = True
        for direc in path:
            cur = cur.adj(direc)
            self._table[cur.x][cur.y].visit = True

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
                if self._is_valid(cur_test) and self._is_valid(nxt_test):
                    self._table[cur_test.x][cur_test.y].visit = True
                    self._table[nxt_test.x][nxt_test.y].visit = True
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

    def _reset_table(self):
        for row in self._table:
            for col in row:
                col.reset()

    def _build_path(self, src, des):
        path = deque()
        tmp = des
        while tmp != src:
            parent = self._table[tmp.x][tmp.y].parent
            path.appendleft(parent.direc_to(tmp))
            tmp = parent
        return path

    def _is_valid(self, pos):
        return self.map.is_safe(pos) and not self._table[pos.x][pos.y].visit
