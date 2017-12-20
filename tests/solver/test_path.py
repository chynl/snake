#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Unit tests for PathSolver."""

from snake.base import Direc, Pos, PointType, Map, Snake
from snake.solver import PathSolver


def test_shortest():
    m = Map(7, 7)
    m.create_food(Pos(5, 5))
    s = Snake(m, Direc.RIGHT,
              [Pos(2, 3), Pos(2, 2), Pos(2, 1)],
              [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR])
    solver = PathSolver(s)
    act_path = solver.shortest_path_to_food()
    act_path = solver.shortest_path_to_food()  # Check idempotence
    expect_path = [
        Direc.RIGHT, Direc.RIGHT, Direc.DOWN, Direc.DOWN, Direc.DOWN
    ]
    assert len(act_path) == len(expect_path)
    for i, direc in enumerate(act_path):
        assert direc == expect_path[i]
    assert solver.table[5][1].dist == 5
    assert solver.table[5][1].dist == solver.table[5][5].dist
    # Empty path
    assert not solver.shortest_path_to(s.tail())


def test_longest():
    m = Map(6, 6)
    m.create_food(Pos(4, 4))
    s = Snake(m, Direc.RIGHT,
              [Pos(1, 3), Pos(1, 2), Pos(1, 1)],
              [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR])
    solver = PathSolver(s)
    act_path = solver.longest_path_to_tail()
    act_path = solver.longest_path_to_tail()  # Check idempotence
    expect_path = [
        Direc.RIGHT, Direc.DOWN, Direc.DOWN, Direc.DOWN, Direc.LEFT, Direc.LEFT, Direc.LEFT,
        Direc.UP, Direc.RIGHT, Direc.RIGHT, Direc.UP, Direc.LEFT, Direc.LEFT, Direc.UP
    ]
    assert m.point(s.tail()).type == PointType.BODY_HOR
    assert len(act_path) == len(expect_path)
    for i, direc in enumerate(act_path):
        assert direc == expect_path[i]
    # Empty path
    assert not solver.longest_path_to(s.tail())
