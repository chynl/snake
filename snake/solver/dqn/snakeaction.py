#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

from enum import Enum, unique

from snake.base import Direc


@unique
class SnakeAction(Enum):
    """Type of snake actions."""
    FORWARD = 0
    LEFT = 1
    RIGHT = 2

    @staticmethod
    def to_direc(action, snake_direc):
        if action == SnakeAction.FORWARD:
            return snake_direc
        elif action == SnakeAction.LEFT:
            if snake_direc == Direc.LEFT:
                return Direc.DOWN
            elif snake_direc == Direc.UP:
                return Direc.LEFT
            elif snake_direc == Direc.RIGHT:
                return Direc.UP
            elif snake_direc == Direc.DOWN:
                return Direc.RIGHT
        elif action == SnakeAction.RIGHT:
            if snake_direc == Direc.LEFT:
                return Direc.UP
            elif snake_direc == Direc.UP:
                return Direc.RIGHT
            elif snake_direc == Direc.RIGHT:
                return Direc.DOWN
            elif snake_direc == Direc.DOWN:
                return Direc.LEFT
        raise ValueError("Unsupported params")
