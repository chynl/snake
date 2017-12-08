#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definition of class Snake."""

from collections import deque
from snake.base.direc import Direc
from snake.base.point import PointType


class Snake:
    """Snake of the game."""

    def __init__(self, m, direc, init_bodies, init_types):
        """Initialize a Snake object.

        Args:
            m (base.map.Map): The map that the snake moves on.
            direc (base.direc.Direc): Initial move direction.
            init_bodies (list of base.pos.Pos): Initial snake bodies positions.
            init_types (list of base.point.PointType): Types of each position in init_bodies.

        """
        self.__dead = False
        self.__direc = direc
        self.__map = m
        self.__bodies = deque(init_bodies)
        for i, pos in enumerate(init_bodies):
            self.__map.point(pos).type = init_types[i]

    @property
    def dead(self):
        return self.__dead

    @property
    def direc(self):
        return self.__direc

    def len(self):
        return len(self.__bodies)

    def head(self):
        if not self.__bodies:
            return None
        else:
            return self.__bodies[0]

    def tail(self):
        if not self.__bodies:
            return None
        else:
            return self.__bodies[-1]

    def move(self, new_direc):
        if self.__dead or new_direc == Direc.NONE \
           or Direc.opposite(new_direc) == self.__direc:
            return
        old_head_type, new_head_type = self.__new_types(self.__direc, new_direc)
        self.__map.point(self.head()).type = old_head_type
        new_head = self.head().adj(new_direc)
        self.__bodies.appendleft(new_head)
        if not self.__map.is_safe(new_head):
            self.__dead = True
        if self.__map.point(new_head).type == PointType.FOOD:
            self.__map.rm_food()
        else:
            self.__rm_tail()
        self.__map.point(new_head).type = new_head_type
        self.__direc = new_direc

    def __rm_tail(self):
        self.__map.point(self.tail()).type = PointType.EMPTY
        self.__bodies.pop()

    def __new_types(self, old_direc, new_direc):
        old_head_type, new_head_type = None, None
        # new_head_type
        if new_direc == Direc.LEFT:
            new_head_type = PointType.HEAD_L
        elif new_direc == Direc.UP:
            new_head_type = PointType.HEAD_U
        elif new_direc == Direc.RIGHT:
            new_head_type = PointType.HEAD_R
        elif new_direc == Direc.DOWN:
            new_head_type = PointType.HEAD_D
        # old_head_type
        if (old_direc == Direc.LEFT and new_direc == Direc.LEFT) or \
           (old_direc == Direc.RIGHT and new_direc == Direc.RIGHT):
            old_head_type = PointType.BODY_HOR
        elif (old_direc == Direc.UP and new_direc == Direc.UP) or \
             (old_direc == Direc.DOWN and new_direc == Direc.DOWN):
            old_head_type = PointType.BODY_VER
        elif (old_direc == Direc.RIGHT and new_direc == Direc.UP) or \
             (old_direc == Direc.DOWN and new_direc == Direc.LEFT):
            old_head_type = PointType.BODY_LU
        elif (old_direc == Direc.LEFT and new_direc == Direc.UP) or \
             (old_direc == Direc.DOWN and new_direc == Direc.RIGHT):
            old_head_type = PointType.BODY_UR
        elif (old_direc == Direc.LEFT and new_direc == Direc.DOWN) or \
             (old_direc == Direc.UP and new_direc == Direc.RIGHT):
            old_head_type = PointType.BODY_RD
        elif (old_direc == Direc.RIGHT and new_direc == Direc.DOWN) or \
             (old_direc == Direc.UP and new_direc == Direc.LEFT):
            old_head_type = PointType.BODY_DL
        return old_head_type, new_head_type
