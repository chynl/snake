#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definition of class Point."""

from enum import Enum, unique


@unique
class PointType(Enum):
    """Type of the points on the game map."""
    EMPTY = 0
    FOOD = 1
    SNAKE_HEAD = 2
    SNAKE_BODY = 3


class Point(object):
    """Point on the game map."""
    def __init__(self):
        self.__type = PointType.EMPTY

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, val):
        self.__type = val
