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
        self._x = x
        self._y = y

    def __str__(self):
        return 'Pos(%d,%d)' % (self._x, self._y)
    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self._x == other.x and self._y == other.y
        return NotImplemented

    def __pos__(self):
        return Pos(self._x, self._y)

    def __neg__(self):
        return Pos(-self._x, -self._y)

    def __add__(self, other):
        if isinstance(self, other.__class__):
            return Pos(self._x + other.x, self._y + other.y)
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
        if self._x == adj_pos.x:
            diff = self._y - adj_pos.y
            if diff == 1:
                return Direc.LEFT
            elif diff == -1:
                return Direc.RIGHT
        elif self._y == adj_pos.y:
            diff = self._x - adj_pos.x
            if diff == 1:
                return Direc.UP
            elif diff == -1:
                return Direc.DOWN
        return Direc.NONE

    def adj(self, direc):
        """Return the adjacent Pos in a given direction."""
        if direc == Direc.LEFT:
            return Pos(self._x, self._y - 1)
        elif direc == Direc.RIGHT:
            return Pos(self._x, self._y + 1)
        elif direc == Direc.UP:
            return Pos(self._x - 1, self._y)
        elif direc == Direc.DOWN:
            return Pos(self._x + 1, self._y)
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
        return self._x

    @x.setter
    def x(self, val):
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
