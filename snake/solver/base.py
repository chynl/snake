#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111


class BaseSolver:
    """Super class of all the solvers."""

    def __init__(self, snake):
        self.__snake = snake
        self.__map = snake.map

    @property
    def map(self):
        return self.__map

    @property
    def snake(self):
        return self.__snake

    @snake.setter
    def snake(self, val):
        self.__snake = val
        self.__map = val.map

    def next_direc(self):
        """Generate the next direction of the snake."""
        return NotImplemented

    def close(self):
        """Release resources."""
        pass
