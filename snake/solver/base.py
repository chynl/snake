#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111


class BaseSolver:
    """Super class of all the solvers."""

    def __init__(self, snake):
        self._snake = snake
        self._map = snake.map

    @property
    def map(self):
        return self._map

    @property
    def snake(self):
        return self._snake

    @snake.setter
    def snake(self, val):
        self._snake = val
        self._map = val.map

    def next_direc(self):
        """Generate the next direction of the snake."""
        return NotImplemented

    def close(self):
        """Release resources."""
        pass
