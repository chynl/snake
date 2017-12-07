#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definition of class Map."""

import random
from snake.base.pos import Pos
from snake.base.point import PointType, Point


class Map(object):
    """2D game map."""

    def __init__(self, num_rows, num_cols):
        """Initialize a Map object."""
        if not isinstance(num_rows, int) or not isinstance(num_cols, int):
            raise TypeError("\'num_rows\' and \'num_cols\' must be integers")
        if num_rows < 5 or num_cols < 5:
            raise ValueError("\'num_rows\' and \'num_cols\' must >= 5")
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__capacity = (num_rows - 2) * (num_cols - 2)
        self.__food = None
        self.__content = [[Point() for _ in range(num_cols)]
                          for _ in range(num_rows)]
        # Add boundary walls
        for i in range(num_rows):
            if i == 0 or i == num_rows - 1:
                for j in range(num_cols):
                    self.__content[i][j].type = PointType.WALL
            else:
                self.__content[i][0].type = PointType.WALL
                self.__content[i][-1].type = PointType.WALL

    def point(self, pos):
        """Return a point on the map.

        DO NOT directly modify the point type to PointType.FOOD and vice versa.
        Use {add|rm}_food() methods instead.

        Args:
            pos (snake.pos.Pos): The position of the point to be fetched

        Returns:
            snake.point.Point: The point at the given position.

        """
        return self.__content[pos.x][pos.y]

    def is_inside(self, pos):
        return pos.x > 0 and pos.x < self.num_rows - 1 \
               and pos.y > 0 and pos.y < self.num_cols - 1

    def is_empty(self, pos):
        return self.is_inside(pos) and self.point(pos).type == PointType.EMPTY

    def is_safe(self, pos):
        return self.is_inside(pos) and (self.point(pos).type == PointType.EMPTY or self.point(pos).type == PointType.FOOD)

    def is_full(self):
        """Check if the map is filled with the snake's bodies."""
        for i in range(1, self.num_rows - 1):
            for j in range(1, self.num_cols - 1):
                t = self.__content[i][j].type
                if t != PointType.SNAKE_HEAD and t != PointType.SNAKE_BODY:
                    return False
        return True

    def has_food(self):
        return self.__food is not None

    def rm_food(self):
        if self.has_food():
            self.point(self.__food).type = PointType.EMPTY
            self.__food = None

    def add_food(self, pos):
        if not self.has_food():
            self.point(pos).type = PointType.FOOD
            self.__food = pos

    def add_rand_food(self):
        empty_pos = []
        for i in range(1, self.__num_rows - 1):
            for j in range(1, self.__num_cols - 1):
                t = self.__content[i][j].type
                if t == PointType.EMPTY:
                    empty_pos.append(Pos(i, j))
                elif t == PointType.FOOD:
                    return None  # Stop if food exists
        food = random.choice(empty_pos)
        self.add_food(food)
        return food

    @property
    def num_rows(self):
        return self.__num_rows

    @property
    def num_cols(self):
        return self.__num_cols

    @property
    def capacity(self):
        return self.__capacity

    @property
    def food(self):
        return self.__food
