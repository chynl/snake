#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

from snake.game import GameConf, Game


conf = GameConf()

conf.solver_name = "HamiltonSolver"
#conf.solver_name = "GreedySolver"

Game(conf).run()
