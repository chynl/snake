#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Unit tests for class Point."""

from snake.base import PointType, Point


def test_init():
    p = Point()
    assert p.type == PointType.EMPTY
    p.type = PointType.FOOD
    assert p.type == PointType.FOOD
