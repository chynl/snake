#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101,W0201

import numpy as np

from snake.util.sumtree import SumTree


class Memory:

    def __init__(self, mem_size, alpha, epsilon):
        self._ALPHA = alpha
        self._EPSILON = epsilon

        self._tree = SumTree(mem_size)

    def store(self, transition):
        max_priority = self._tree.max_leaf()
        if max_priority == 0:
            max_priority = self._priority(0)
        self._tree.insert(transition, max_priority)

    def sample(self, num_samples, beta):
        batch = [None] * num_samples
        IS_weights = np.zeros((num_samples, ))  # Importance-sampling (IS) weights
        tree_indices = np.zeros((num_samples, ), dtype=np.int32)

        len_seg = self._tree.sum() / num_samples
        min_prob = self._tree.min_leaf() / self._tree.sum()

        for i in range(num_samples):
            val = np.random.uniform(len_seg * i, len_seg * (i + 1))
            tree_indices[i], priority, batch[i] = self._tree.retrieve(val)
            prob = priority / self._tree.sum()
            IS_weights[i] = np.power(prob / min_prob, -beta)  # Simplified formula

        return batch, IS_weights, tree_indices

    def update(self, tree_indices, abs_td_errs):
        priorities = self._priority(abs_td_errs)
        for idx, priority in zip(tree_indices, priorities):
            self._tree.update(idx, priority)

    def _priority(self, abs_td_err):
        return np.power(abs_td_err + self._EPSILON, self._ALPHA)
