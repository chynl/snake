#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Unit tests for class Map."""

import pytest

from snake.base import Map, PointType, Pos


def test_init():
    with pytest.raises(TypeError):
        m = Map(5, 1.5)
    with pytest.raises(ValueError):
        m = Map(4, 5)
    m = Map(12, 12)
    for i in range(m.num_rows):
        for j in range(m.num_cols):
            if i == 0 or i == m.num_rows - 1 or j == 0 or j == m.num_cols - 1:
                assert m.point(Pos(i, j)).type == PointType.WALL
            else:
                assert m.point(Pos(i, j)).type == PointType.EMPTY


def test_copy():
    m = Map(5, 5)
    m.point(Pos(1, 1)).type = PointType.FOOD
    m_copy = m.copy()
    assert id(m) != id(m_copy)
    assert m.num_rows == m_copy.num_rows
    assert m.num_cols == m_copy.num_cols
    assert m.capacity == m_copy.capacity
    for i in range(m.num_rows):
        for j in range(m.num_cols):
            assert m.point(Pos(i, j)).type == m_copy.point(Pos(i, j)).type


def test_predicate():
    m = Map(5, 5)
    assert not m.is_full()
    for i in range(m.num_rows):
        for j in range(m.num_cols):
            p = Pos(i, j)
            if i == 0 or i == m.num_rows - 1 or j == 0 or j == m.num_cols - 1:
                assert not m.is_inside(p) and not m.is_empty(p) \
                       and not m.is_safe(p)
            else:
                assert m.is_inside(p) and m.is_empty(p) and m.is_safe(p)
    p1, p2, p3 = Pos(1, 1), Pos(2, 2), Pos(3, 3)
    m.point(p1).type = PointType.HEAD_L
    m.point(p2).type = PointType.BODY_VER
    m.point(p3).type = PointType.FOOD
    assert m.is_inside(p1) and not m.is_empty(p1) and not m.is_safe(p1)
    assert m.is_inside(p2) and not m.is_empty(p2) and not m.is_safe(p2)
    assert m.is_inside(p3) and not m.is_empty(p3) and m.is_safe(p3)
    assert not m.is_full()
    for i in range(1, m.num_rows - 1):
        for j in range(1, m.num_cols - 1):
            if i < m.num_rows / 2:
                m.point(Pos(i, j)).type = PointType.HEAD_U
            else:
                m.point(Pos(i, j)).type = PointType.BODY_UR
    assert m.is_full()


def test_food():
    m = Map(5, 5)
    assert not m.has_food()
    m.create_food(Pos(1, 1))
    assert m.has_food()
    m.rm_food()
    assert not m.has_food()
    fd = m.create_rand_food()
    assert m.has_food()
    assert m.point(fd).type == PointType.FOOD
    m.rm_food()
    for i in range(1, m.num_rows - 1):
        for j in range(1, m.num_cols - 1):
            assert m.point(Pos(i, j)).type == PointType.EMPTY
