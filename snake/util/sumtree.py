#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

import numpy as np


class SumTree:

    def __init__(self, capacity):
        self._capacity = capacity
        self._tree = np.zeros(2 * self._capacity - 1)
        self._data = [None] * self._capacity
        self._data_idx = 0

    @property
    def capacity(self):
        return self._capacity

    @property
    def tree(self):
        return self._tree

    @property
    def data(self):
        return self._data

    def sum(self):
        return self._tree[0]

    def insert(self, data, priority):
        self._data[self._data_idx] = data
        tree_idx = self._data_idx + self._capacity - 1
        self.update(tree_idx, priority)
        self._data_idx += 1
        if self._data_idx >= self._capacity:
            self._data_idx = 0

    def update(self, tree_idx, priority):
        delta = priority - self._tree[tree_idx]
        self._tree[tree_idx] = priority
        while tree_idx != 0:
            tree_idx = (tree_idx - 1) // 2  # Get parent
            self._tree[tree_idx] += delta

    def retrieve(self, val):
        tree_idx, parent = None, 0
        while True:
            left = 2 * parent + 1
            right = left + 1
            if left >= len(self._tree):  # Leaf
                tree_idx = parent
                break
            else:
                if val <= self._tree[left]:
                    parent = left
                else:
                    val -= self._tree[left]
                    parent = right

        priority = self._tree[tree_idx]
        data = self._data[tree_idx - self._capacity + 1]

        return tree_idx, priority, data

    def max_leaf(self):
        return np.max(self.leaves())

    def min_leaf(self):
        return np.min(self.leaves())

    def leaves(self):
        return self._tree[-self._capacity:]
