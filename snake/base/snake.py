#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,W0201,W0212

"""Definition of class Snake."""

import random
from collections import deque
from snake.base.direc import Direc
from snake.base.pos import Pos
from snake.base.point import PointType


class Snake:
    """Snake of the game."""

    def __init__(self, m, init_direc=Direc.RIGHT, init_bodies=None, init_types=None):
        """Initialize a Snake object.

        Args:
            m (base.map.Map): The map that the snake moves on.
            init_direc (base.direc.Direc): Initial direction.
            init_bodies (list of base.pos.Pos): Initial snake bodies positions.
            init_types (list of base.point.PointType): Types of each position in init_bodies.

        """
        self.__map = m
        self.__init_direc = init_direc
        self.__init_bodies = init_bodies
        self.__init_types = init_types
        self.reset()

    def reset(self):
        rand_init = False
        if self.__init_bodies is None:  # Randomly initialize
            rand_init = True
            head_row = random.randrange(1, self.__map.num_rows - 1)
            head_col = random.randrange(3, self.__map.num_cols - 1)
            self.__init_bodies = [Pos(head_row, head_col),
                                  Pos(head_row, head_col - 1),
                                  Pos(head_row, head_col - 2)]
            self.__init_types = [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR]

        self.__steps = 0
        self.__dead = False
        self.__direc = self.__init_direc
        self.__direc_next = Direc.NONE
        self.__map.reset()
        self.__bodies = deque(self.__init_bodies)
        for i, pos in enumerate(self.__init_bodies):
            self.__map.point(pos).type = self.__init_types[i]

        if rand_init:
            self.__init_bodies = self.__init_types = None

    def copy(self):
        m_copy = self.__map.copy()
        s_copy = Snake(m_copy, Direc.NONE, [], [])
        s_copy.__steps = self.__steps
        s_copy.__dead = self.__dead
        s_copy.__direc = self.__direc
        s_copy.__direc_next = self.__direc_next
        s_copy.__bodies = deque(self.__bodies)
        return s_copy, m_copy

    @property
    def steps(self):
        return self.__steps

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

    @property
    def bodies(self):
        return self.__bodies

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
        self.__steps += 1

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
