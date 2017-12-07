#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Unit tests for class Snake."""

from snake.base import Direc, Pos, PointType, Map, Snake


def test_init():
    m = Map(5, 5)
    s = Snake(m, Direc.RIGHT,
              [Pos(1, 3), Pos(1, 2), Pos(1, 1)],
              [PointType.HEAD_R, PointType.BODY_HOR, PointType.BODY_HOR])
    assert not s.dead
    assert s.direc is Direc.RIGHT
    assert s.len() == 3
    assert s.head() == Pos(1, 3)
    assert s.tail() == Pos(1, 1)
    assert m.point(Pos(1, 1)).type == PointType.BODY_HOR
    assert m.point(Pos(1, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(1, 3)).type == PointType.HEAD_R


def test_move():
    m = Map(5, 5)
    s = Snake(m, Direc.RIGHT,
              [Pos(1, 2), Pos(1, 1)],
              [PointType.HEAD_R, PointType.BODY_HOR])
    assert s.len() == 2
    s.move(Direc.RIGHT)
    assert s.head() == Pos(1, 3)
    assert s.tail() == Pos(1, 2)
    assert m.point(Pos(1, 1)).type == PointType.EMPTY
    assert m.point(Pos(1, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(1, 3)).type == PointType.HEAD_R
    m.add_food(Pos(2, 3))
    assert m.has_food()
    s.move(Direc.DOWN)
    assert not m.has_food()
    assert s.len() == 3
    assert s.head() == Pos(2, 3)
    assert s.tail() == Pos(1, 2)
    assert m.point(Pos(1, 1)).type == PointType.EMPTY
    assert m.point(Pos(1, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(1, 3)).type == PointType.BODY_DL
    assert m.point(Pos(2, 3)).type == PointType.HEAD_D
    s.move(Direc.LEFT)
    assert m.point(Pos(1, 2)).type == PointType.EMPTY
    assert m.point(Pos(1, 3)).type == PointType.BODY_DL
    assert m.point(Pos(2, 3)).type == PointType.BODY_LU
    assert m.point(Pos(2, 2)).type == PointType.HEAD_L
    s.move(Direc.LEFT)
    assert m.point(Pos(2, 3)).type == PointType.BODY_LU
    assert m.point(Pos(2, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(2, 1)).type == PointType.HEAD_L
    s.move(Direc.DOWN)
    assert m.point(Pos(2, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(2, 1)).type == PointType.BODY_RD
    assert m.point(Pos(3, 1)).type == PointType.HEAD_D
    s.move(Direc.RIGHT)
    assert m.point(Pos(2, 1)).type == PointType.BODY_RD
    assert m.point(Pos(3, 1)).type == PointType.BODY_UR
    assert m.point(Pos(3, 2)).type == PointType.HEAD_R
    s.move(Direc.RIGHT)
    assert m.point(Pos(3, 1)).type == PointType.BODY_UR
    assert m.point(Pos(3, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(3, 3)).type == PointType.HEAD_R
    s.move(Direc.UP)
    assert m.point(Pos(3, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(3, 3)).type == PointType.BODY_LU
    assert m.point(Pos(2, 3)).type == PointType.HEAD_U
    s.move(Direc.LEFT)
    assert m.point(Pos(3, 3)).type == PointType.BODY_LU
    assert m.point(Pos(2, 3)).type == PointType.BODY_DL
    assert m.point(Pos(2, 2)).type == PointType.HEAD_L
    s.move(Direc.LEFT)
    assert m.point(Pos(2, 3)).type == PointType.BODY_DL
    assert m.point(Pos(2, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(2, 1)).type == PointType.HEAD_L
    s.move(Direc.UP)
    assert m.point(Pos(2, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(2, 1)).type == PointType.BODY_UR
    assert m.point(Pos(1, 1)).type == PointType.HEAD_U
    s.move(Direc.RIGHT)
    assert m.point(Pos(2, 1)).type == PointType.BODY_UR
    assert m.point(Pos(1, 1)).type == PointType.BODY_RD
    assert m.point(Pos(1, 2)).type == PointType.HEAD_R
    s.move(Direc.RIGHT)
    assert m.point(Pos(1, 1)).type == PointType.BODY_RD
    assert m.point(Pos(1, 2)).type == PointType.BODY_HOR
    assert m.point(Pos(1, 3)).type == PointType.HEAD_R
    s.move(Direc.DOWN)
    s.move(Direc.DOWN)
    assert m.point(Pos(1, 3)).type == PointType.BODY_DL
    assert m.point(Pos(2, 3)).type == PointType.BODY_VER
    assert m.point(Pos(3, 3)).type == PointType.HEAD_D
    s.move(Direc.LEFT)
    s.move(Direc.LEFT)
    s.move(Direc.UP)
    s.move(Direc.UP)
    assert m.point(Pos(3, 1)).type == PointType.BODY_UR
    assert m.point(Pos(2, 1)).type == PointType.BODY_VER
    assert m.point(Pos(1, 1)).type == PointType.HEAD_U
    assert s.len() == 3
