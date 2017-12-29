#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

from snake.base import Pos, PointType, Map
from snake.game import GameConf
from snake.gui import GameWindow


def test_game_window():
    game_conf = GameConf()
    game_conf.map_rows = 15
    game_conf.map_cols = game_conf.map_rows
    game_conf.show_grid_line = True
    game_conf.show_info_panel = False

    game_map = Map(game_conf.map_rows + 2, game_conf.map_cols + 2)
    contents = (
        # Walls
        (Pos(1, 6), PointType.WALL),
        (Pos(1, 7), PointType.WALL),
        (Pos(1, 8), PointType.WALL),
        (Pos(1, 9), PointType.WALL),
        (Pos(1, 10), PointType.WALL),
        (Pos(15, 6), PointType.WALL),
        (Pos(15, 7), PointType.WALL),
        (Pos(15, 8), PointType.WALL),
        (Pos(15, 9), PointType.WALL),
        (Pos(15, 10), PointType.WALL),
        (Pos(6, 1), PointType.WALL),
        (Pos(7, 1), PointType.WALL),
        (Pos(8, 1), PointType.WALL),
        (Pos(9, 1), PointType.WALL),
        (Pos(10, 1), PointType.WALL),
        (Pos(6, 15), PointType.WALL),
        (Pos(7, 15), PointType.WALL),
        (Pos(8, 15), PointType.WALL),
        (Pos(9, 15), PointType.WALL),
        (Pos(10, 15), PointType.WALL),
        # Food
        (Pos(4, 6), PointType.FOOD),
        (Pos(4, 10), PointType.FOOD),
        (Pos(6, 4), PointType.FOOD),
        (Pos(10, 4), PointType.FOOD),
        (Pos(6, 12), PointType.FOOD),
        (Pos(10, 12), PointType.FOOD),
        (Pos(12, 6), PointType.FOOD),
        (Pos(12, 10), PointType.FOOD),
        # Top-left
        (Pos(2, 2), PointType.BODY_VER),
        (Pos(3, 2), PointType.BODY_VER),
        (Pos(4, 2), PointType.BODY_UR),
        (Pos(4, 3), PointType.BODY_LU),
        (Pos(3, 3), PointType.BODY_VER),
        (Pos(2, 3), PointType.BODY_RD),
        (Pos(2, 4), PointType.BODY_DL),
        (Pos(2, 4), PointType.BODY_DL),
        (Pos(3, 4), PointType.BODY_VER),
        (Pos(4, 4), PointType.HEAD_D),
        # Top-right
        (Pos(2, 14), PointType.BODY_VER),
        (Pos(3, 14), PointType.BODY_VER),
        (Pos(4, 14), PointType.BODY_LU),
        (Pos(4, 13), PointType.BODY_UR),
        (Pos(3, 13), PointType.BODY_VER),
        (Pos(2, 13), PointType.BODY_DL),
        (Pos(2, 12), PointType.BODY_RD),
        (Pos(3, 12), PointType.BODY_VER),
        (Pos(4, 12), PointType.HEAD_D),
        # Bottom-left
        (Pos(14, 2), PointType.BODY_VER),
        (Pos(13, 2), PointType.BODY_VER),
        (Pos(12, 2), PointType.BODY_RD),
        (Pos(12, 3), PointType.BODY_DL),
        (Pos(13, 3), PointType.BODY_VER),
        (Pos(14, 3), PointType.BODY_UR),
        (Pos(14, 4), PointType.BODY_LU),
        (Pos(13, 4), PointType.BODY_VER),
        (Pos(12, 4), PointType.HEAD_U),
        # Bottom-right
        (Pos(14, 14), PointType.BODY_VER),
        (Pos(13, 14), PointType.BODY_VER),
        (Pos(12, 14), PointType.BODY_DL),
        (Pos(12, 13), PointType.BODY_RD),
        (Pos(13, 13), PointType.BODY_VER),
        (Pos(14, 13), PointType.BODY_LU),
        (Pos(14, 12), PointType.BODY_UR),
        (Pos(13, 12), PointType.BODY_VER),
        (Pos(12, 12), PointType.HEAD_U),
        # Middle
        (Pos(10, 6), PointType.HEAD_L),
        (Pos(10, 7), PointType.BODY_HOR),
        (Pos(10, 8), PointType.BODY_HOR),
        (Pos(10, 9), PointType.BODY_HOR),
        (Pos(10, 10), PointType.BODY_LU),
        (Pos(9, 10), PointType.BODY_VER),
        (Pos(8, 10), PointType.BODY_DL),
        (Pos(8, 9), PointType.BODY_HOR),
        (Pos(8, 8), PointType.BODY_HOR),
        (Pos(8, 7), PointType.BODY_HOR),
        (Pos(8, 6), PointType.BODY_UR),
        (Pos(7, 6), PointType.BODY_VER),
        (Pos(6, 6), PointType.BODY_RD),
        (Pos(6, 7), PointType.BODY_HOR),
        (Pos(6, 8), PointType.BODY_HOR),
        (Pos(6, 9), PointType.BODY_HOR),
        (Pos(6, 10), PointType.HEAD_R)
    )
    for content in contents:
        game_map.point(content[0]).type = content[1]

    GameWindow("Basic Elements", game_conf, game_map).show()
