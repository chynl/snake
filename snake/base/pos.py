#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definitions of class Pos."""

from snake.base.direc import Direc


class Pos:
    """Integer coordinate in 2D plane.

    The origin of the coordinate system is at the top-left corner,
    with x-axis extends downward and y-axis extends rightward.

    """
    def __init__(self, x=0, y=0):
        self.__x = x
        self.__y = y

    def __str__(self):
        return 'Pos(%d,%d)' % (self.__x, self.__y)
    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__x == other.x and self.__y == other.y
        return NotImplemented

    def __pos__(self):
        return Pos(self.__x, self.__y)

    def __neg__(self):
        return Pos(-self.__x, -self.__y)

    def __add__(self, other):
        if isinstance(self, other.__class__):
            return Pos(self.__x + other.x, self.__y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(self, other.__class__):
            return self + (-other)
        return NotImplemented

    def __hash__(self):
        return hash((self.x, self.y))

    @staticmethod
    def manhattan_dist(p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def direc_to(self, adj_pos):
        """Return the direction of an adjacent Pos relative to self."""
        if self.__x == adj_pos.x:
            diff = self.__y - adj_pos.y
            if diff == 1:
                return Direc.LEFT
            elif diff == -1:
                return Direc.RIGHT
        elif self.__y == adj_pos.y:
            diff = self.__x - adj_pos.x
            if diff == 1:
                return Direc.UP
            elif diff == -1:
                return Direc.DOWN
        return Direc.NONE

    def adj(self, direc):
        """Return the adjacent Pos in a given direction."""
        if direc == Direc.LEFT:
            return Pos(self.__x, self.__y - 1)
        elif direc == Direc.RIGHT:
            return Pos(self.__x, self.__y + 1)
        elif direc == Direc.UP:
            return Pos(self.__x - 1, self.__y)
        elif direc == Direc.DOWN:
            return Pos(self.__x + 1, self.__y)
        else:
            return None

    def all_adj(self):
        """Return a list of all the adjacent Pos."""
        adjs = []
        for direc in Direc:
            if direc != Direc.NONE:
                adjs.append(self.adj(direc))
        return adjs

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, val):
        self.__x = val

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, val):
        self.__y = val
