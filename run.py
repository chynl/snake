#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from snake.game import GameMode, GameConf, Game


# Available solvers
solvers = [
    "GreedySolver",
    "HamiltonSolver"
]

# Game configurations
conf = GameConf()
conf.mode = GameMode.NORMAL
conf.solver_name = solvers[1]

# Run the game
Game(conf).run()
