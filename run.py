#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from snake.game import GameMode, GameConf, Game


# Available solvers
solvers = [
    "GreedySolver",
    "HamiltonSolver",
    "DQNSolver"
]

# Game configurations
conf = GameConf()
conf.mode = GameMode.TRAIN_DQN
conf.solver_name = solvers[2]

# Run the game
Game(conf).run()
