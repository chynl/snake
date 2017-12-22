#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

"""Testing maze generation in HamiltonSovler."""

from snake.base import Direc, Pos, PointType, Map, Snake
from snake.game import GameConf
from snake.gui import GameWindow
from snake.solver.hamilton import HamiltonSolver


def test_maze():
    game_conf = GameConf()
    game_conf.map_rows = 6
    game_conf.map_cols = game_conf.map_rows
    game_conf.show_grid_line = True
    game_conf.show_info_panel = False

    game_map = Map(game_conf.map_rows + 2, game_conf.map_cols + 2)
    game_snake = Snake(game_map)

    solver = HamiltonSolver(game_snake)

    GameWindow(game_conf, solver.maze_map, "Maze for HamiltonSolver").show()
    GameWindow(game_conf, game_map, "Game Map").show()
