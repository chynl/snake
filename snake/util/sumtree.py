#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

import numpy as np


class SumTree:

    def __init__(self, capacity):
        self.__capacity = capacity
        self.__tree = np.zeros(2 * self.__capacity - 1)
        self.__data = np.zeros(self.__capacity, dtype=object)
        self.__data_idx = 0

    @property
    def tree(self):
        return self.__tree

    @property
    def data(self):
        return self.__data

    def sum(self):
        return self.__tree[0]

    def insert(self, data, priority):
        self.__data[self.__data_idx] = data
        tree_idx = self.__data_idx + self.__capacity - 1
        self.update(tree_idx, priority)
        self.__data_idx += 1
        if self.__data_idx >= self.__capacity:
            self.__data_idx = 0

    def update(self, tree_idx, priority):
        delta = priority - self.__tree[tree_idx]
        self.__tree[tree_idx] = priority
        while tree_idx != 0:
            tree_idx = (tree_idx - 1) // 2  # Get parent
            self.__tree[tree_idx] += delta

    def retrieve(self, val):
        parent = 0
        while True:
            left = 2 * parent + 1
            right = left + 1
            if left >= len(self.__tree):
                tree_idx = parent
                break
            else:
                if val <= self.__tree[left]:
                    parent = left
                else:
                    val -= self.__tree[left]
                    parent = right
        data_idx = tree_idx - self.__capacity + 1
        return tree_idx, self.__tree[tree_idx], self.__data[data_idx]

    def leaves(self):
        return self.__tree[-self.__capacity:]
