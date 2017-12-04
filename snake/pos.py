#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definitions of class Pos."""

import unittest
from direc import Direc


class Pos(object):
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
        else:
            raise TypeError("addition requires two Pos object")

    def __sub__(self, other):
        if isinstance(self, other.__class__):
            return self + (-other)
        else:
            raise TypeError("subtraction requires two Pos object")

    def __hash__(self):
        return hash((self.x, self.y))

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


class TestPos(unittest.TestCase):

    def test_init(self):
        p = Pos(-5, 5)
        self.assertEqual(p, Pos(-5, 5))
        p.x = -10
        p.y = 10
        self.assertNotEqual(p, Pos(-5, 5))
        self.assertEqual(p, Pos(-10, 10))

    def test_arithmetic(self):
        p1 = Pos(-5, 10)
        p2 = Pos(5, -10)
        p3 = p1 + p2
        p4 = p1 - p2
        p5 = p2 - p1
        self.assertEqual(p3, Pos(0, 0))
        self.assertEqual(p3 - p1, p2)
        self.assertEqual(p3 - p2, p1)
        self.assertEqual(p4, Pos(-10, 20))
        self.assertEqual(p5, -Pos(-10, 20))
        self.assertEqual(p4 + p2, p1)
        self.assertEqual(p5 + p1, p2)

    def test_adj(self):
        p = Pos(0, 0)
        adjs = p.all_adj()
        self.assertEqual(len(adjs), 4)
        hit = [False] * 4
        self.assertEqual(hit.count(False), 4)
        for adj in adjs:
            if adj == Pos(-1, 0):
                self.assertEqual(p.direc_to(adj), Direc.UP)
                hit[0] = True
            elif adj == Pos(1, 0):
                self.assertEqual(p.direc_to(adj), Direc.DOWN)
                hit[1] = True
            elif adj == Pos(0, 1):
                self.assertEqual(p.direc_to(adj), Direc.RIGHT)
                hit[2] = True
            elif adj == Pos(0, -1):
                self.assertEqual(p.direc_to(adj), Direc.LEFT)
                hit[3] = True
            else:
                raise ValueError("error adj Pos")
        self.assertEqual(hit.count(False), 0)


if __name__ == "__main__":
    unittest.main()
