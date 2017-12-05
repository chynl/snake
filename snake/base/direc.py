#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Definition of enum Direc."""

from enum import Enum, unique


@unique
class Direc(Enum):
    """Directions on the game plane."""
    NONE = 0
    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4

    @staticmethod
    def opposite(direc):
        """Return the opposite direction."""
        if direc == Direc.LEFT:
            return direc.RIGHT
        elif direc == Direc.RIGHT:
            return direc.LEFT
        elif direc == Direc.UP:
            return direc.DOWN
        elif direc == Direc.DOWN:
            return direc.UP
        else:
            return direc.NONE
