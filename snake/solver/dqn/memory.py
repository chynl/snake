#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101,W0201

import json
import os

import numpy as np

from snake.solver.dqn.logger import log
from snake.util.sumtree import SumTree

_DIR_LOG = "logs"


class _SumTree(SumTree):

    PATH_TREE = os.path.join(_DIR_LOG, "sumtree-tree-%d.npy")
    PATH_DATA = os.path.join(_DIR_LOG, "sumtree-data-%d.npy")
    PATH_VAR = os.path.join(_DIR_LOG, "sumtree-var-%d.json")

    def save(self, steps):
        np.save(_SumTree.PATH_TREE % steps, self._SumTree__tree)
        np.save(_SumTree.PATH_DATA % steps, self._SumTree__data)
        with open(_SumTree.PATH_VAR % steps, "w") as f:
            json.dump({
                "capacity": self._SumTree__capacity,
                "data_idx": self._SumTree__data_idx,
            }, f, indent=2)

    def load(self, steps):
        self._SumTree__tree = np.load(_SumTree.PATH_TREE % steps)
        self._SumTree__data = np.load(_SumTree.PATH_DATA % steps)
        with open(_SumTree.PATH_VAR % steps, "r") as f:
            var = json.load(f)
        self._SumTree__capacity = var["capacity"]
        self._SumTree__data_idx = var["data_idx"]
        log("sum tree loaded | tree shape: {} | data shape: {} | capacity: {} | data_idx: {}"
            .format(self._SumTree__tree.shape, self._SumTree__data.shape,
                    self._SumTree__capacity, self._SumTree__data_idx))


class Memory:

    PATH_VAR = os.path.join(_DIR_LOG, "mem-var-%d.json")

    def __init__(self, mem_size, alpha, beta_min, beta_inc, pri_epsilon, abs_err_upper):
        self.__MEM_SIZE = mem_size
        self.__ALPHA = alpha
        self.__BETA_MIN = beta_min
        self.__BETA_INC = beta_inc
        self.__PRI_EPSILON = pri_epsilon
        self.__ABS_ERR_UPPER = abs_err_upper

        self.__beta = self.__BETA_MIN
        self.__tree = _SumTree(self.__MEM_SIZE)

    @property
    def beta(self):
        return self.__beta

    def save(self, steps):
        self.__tree.save(steps)
        with open(Memory.PATH_VAR % steps, "w") as f:
            json.dump({
                "beta": self.__beta,
            }, f, indent=2)

    def load(self, steps):
        self.__tree.load(steps)
        with open(Memory.PATH_VAR % steps, "r") as f:
            var = json.load(f)
        self.__beta = var["beta"]
        log("memory loaded | beta: %.6f" % (self.__beta))

    def store(self, transition):
        max_priority = self.__tree.max_leaf()
        if max_priority == 0:
            max_priority = self.__ABS_ERR_UPPER
        self.__tree.insert(transition, max_priority)

    def sample(self, num_samples):
        tree_indices = np.zeros((num_samples, ), dtype=np.int32)
        batch_mem = np.zeros((num_samples, self.__tree.data[0].size))
        IS_weights = np.zeros((num_samples, ))  # Importance-sampling (IS) weights

        len_seg = self.__tree.sum() / num_samples
        min_prob = self.__tree.min_leaf() / self.__tree.sum()

        for i in range(num_samples):
            val = np.random.uniform(len_seg * i, len_seg * (i + 1))
            tree_indices[i], priority, batch_mem[i, :] = self.__tree.retrieve(val)
            prob = priority / self.__tree.sum()
            IS_weights[i] = np.power(prob / min_prob, -self.__beta)  # Simplified formula

        self.__beta = min(1.0, self.__beta + self.__BETA_INC)

        return tree_indices, batch_mem, IS_weights

    def update(self, tree_indices, abs_errs):
        abs_errs += self.__PRI_EPSILON
        clipped_errors = np.minimum(abs_errs, self.__ABS_ERR_UPPER)
        priorities = np.power(clipped_errors, self.__ALPHA)
        for idx, priority in zip(tree_indices, priorities):
            self.__tree.update(idx, priority)
