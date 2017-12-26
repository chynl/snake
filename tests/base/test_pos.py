#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

"""Unit tests for class Pos."""

from snake.base import Direc, Pos


def test_init():
    p = Pos(-5, 5)
    assert p == Pos(-5, 5)
    p.x = -10
    p.y = 10
    assert p != Pos(-5, 5)
    assert p == Pos(-10, 10)


def test_arithmetic():
    p1 = Pos(-5, 10)
    p2 = Pos(5, -10)
    p3 = p1 + p2
    p4 = p1 - p2
    p5 = p2 - p1
    assert p3 == Pos(0, 0)
    assert p3 - p1 == p2
    assert p3 - p2 == p1
    assert p4 == Pos(-10, 20)
    assert p5 == -Pos(-10, 20)
    assert p4 + p2 == p1
    assert p5 + p1 == p2


def test_dist():
    p1 = Pos(-5, 20)
    p2 = Pos(10, 8)
    assert Pos.manhattan_dist(p1, p2) == 27


def test_adj():
    p = Pos(0, 0)
    adjs = p.all_adj()
    assert len(adjs) == 4
    hit = [False] * 4
    assert hit.count(False) == 4
    for adj in adjs:
        if adj == Pos(-1, 0):
            assert p.direc_to(adj) == Direc.UP
            hit[0] = True
        elif adj == Pos(1, 0):
            assert p.direc_to(adj) == Direc.DOWN
            hit[1] = True
        elif adj == Pos(0, 1):
            assert p.direc_to(adj) == Direc.RIGHT
            hit[2] = True
        elif adj == Pos(0, -1):
            assert p.direc_to(adj) == Direc.LEFT
            hit[3] = True
        else:
            raise ValueError("error adj Pos")
    assert hit.count(False) == 0
