#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103

from enum import Enum, unique

from snake.base.direc import Direc


@unique
class SnakeAction(Enum):
    """Snake actions for DQN."""
    LEFT = 0
    FORWARD = 1
    RIGHT = 2

    @staticmethod
    def to_direc(action, cur_direc):
        """Return the direction wrt the action."""
        if action == SnakeAction.FORWARD:
            return cur_direc
        elif action == SnakeAction.LEFT:
            if cur_direc == Direc.LEFT:
                return Direc.DOWN
            elif cur_direc == Direc.UP:
                return Direc.LEFT
            elif cur_direc == Direc.RIGHT:
                return Direc.UP
            elif cur_direc == Direc.DOWN:
                return Direc.RIGHT
        elif action == SnakeAction.RIGHT:
            if cur_direc == Direc.LEFT:
                return Direc.UP
            elif cur_direc == Direc.UP:
                return Direc.RIGHT
            elif cur_direc == Direc.RIGHT:
                return Direc.DOWN
            elif cur_direc == Direc.DOWN:
                return Direc.LEFT
