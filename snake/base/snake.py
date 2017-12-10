#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,W0201

"""Definition of class Snake."""

from collections import deque
from snake.base.direc import Direc
from snake.base.point import PointType


class Snake:
    """Snake of the game."""

    def __init__(self, m, init_direc, init_bodies, init_types):
        """Initialize a Snake object.

        Args:
            m (base.map.Map): The map that the snake moves on.
            init_direc (base.direc.Direc): Initial move direction.
            init_bodies (list of base.pos.Pos): Initial snake bodies positions.
            init_types (list of base.point.PointType): Types of each position in init_bodies.

        """
        self.__map = m
        self.__init_direc = init_direc
        self.__init_bodies = init_bodies
        self.__init_types = init_types
        self.reset()

    def reset(self):
        self.__dead = False
        self.__direc = self.__init_direc
        self.__direc_next = self.__init_direc
        self.__map.reset()
        self.__bodies = deque(self.__init_bodies)
        for i, pos in enumerate(self.__init_bodies):
            self.__map.point(pos).type = self.__init_types[i]

    @property
    def dead(self):
        return self.__dead

    @dead.setter
    def dead(self, val):
        self.__dead = val

    @property
    def direc(self):
        return self.__direc

    @property
    def direc_next(self):
        return self.__direc_next

    @direc_next.setter
    def direc_next(self, val):
        self.__direc_next = val

    def len(self):
        return len(self.__bodies)

    def head(self):
        if not self.__bodies:
            return None
        return self.__bodies[0]

    def tail(self):
        if not self.__bodies:
            return None
        return self.__bodies[-1]

    def move(self, new_direc=None):
        if new_direc is not None:
            self.__direc_next = new_direc
        if self.__dead or self.__direc_next == Direc.NONE:
            return
        old_head_type, new_head_type = self.__new_types()
        self.__map.point(self.head()).type = old_head_type
        new_head = self.head().adj(self.__direc_next)
        self.__bodies.appendleft(new_head)
        if not self.__map.is_safe(new_head):
            self.__dead = True
        if self.__map.point(new_head).type == PointType.FOOD:
            self.__map.rm_food()
        else:
            self.__rm_tail()
        self.__map.point(new_head).type = new_head_type
        self.__direc = self.__direc_next

    def __rm_tail(self):
        self.__map.point(self.tail()).type = PointType.EMPTY
        self.__bodies.pop()

    def __new_types(self):
        old_head_type, new_head_type = None, None
        # new_head_type
        if self.__direc_next == Direc.LEFT:
            new_head_type = PointType.HEAD_L
        elif self.__direc_next == Direc.UP:
            new_head_type = PointType.HEAD_U
        elif self.__direc_next == Direc.RIGHT:
            new_head_type = PointType.HEAD_R
        elif self.__direc_next == Direc.DOWN:
            new_head_type = PointType.HEAD_D
        # old_head_type
        if (self.__direc == Direc.LEFT and self.__direc_next == Direc.LEFT) or \
           (self.__direc == Direc.RIGHT and self.__direc_next == Direc.RIGHT):
            old_head_type = PointType.BODY_HOR
        elif (self.__direc == Direc.UP and self.__direc_next == Direc.UP) or \
             (self.__direc == Direc.DOWN and self.__direc_next == Direc.DOWN):
            old_head_type = PointType.BODY_VER
        elif (self.__direc == Direc.RIGHT and self.__direc_next == Direc.UP) or \
             (self.__direc == Direc.DOWN and self.__direc_next == Direc.LEFT):
            old_head_type = PointType.BODY_LU
        elif (self.__direc == Direc.LEFT and self.__direc_next == Direc.UP) or \
             (self.__direc == Direc.DOWN and self.__direc_next == Direc.RIGHT):
            old_head_type = PointType.BODY_UR
        elif (self.__direc == Direc.LEFT and self.__direc_next == Direc.DOWN) or \
             (self.__direc == Direc.UP and self.__direc_next == Direc.RIGHT):
            old_head_type = PointType.BODY_RD
        elif (self.__direc == Direc.RIGHT and self.__direc_next == Direc.DOWN) or \
             (self.__direc == Direc.UP and self.__direc_next == Direc.LEFT):
            old_head_type = PointType.BODY_DL
        return old_head_type, new_head_type
