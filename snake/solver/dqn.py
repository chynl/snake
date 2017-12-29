#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101

import numpy as np
import tensorflow as tf
from snake.base import Direc, PointType
from snake.solver.base import BaseSolver


class DQNSolver(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)

        self.__lr = 0.01      # Learning rate
        self.__gamma = 0.9    # Reward decay
        self.__epsilon = 0.1  # Epsilon-greedy
        self.__mem_size = 100
        self.__mem_batch = 16
        self.__replace_target_iter = 300

        self.__actions = [Direc.LEFT, Direc.UP, Direc.RIGHT, Direc.DOWN]
        self.__num_actions = len(self.__actions)
        self.__num_features = snake.map.capacity
        self.__learn_steps = 0

        # Replay memory
        self.__mem = np.zeros((self.__mem_size, self.__num_features * 2 + 2))
        self.__mem_cnt = 0

        # Build two networks and get parameters
        target_params, eval_params = self.__build_net()

        # Replace target network parameters
        self.__replace_target = [tf.assign(t, e) for t, e in zip(target_params, eval_params)]

        # Create tensorflow session
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())

        # Write graph logs
        tf.summary.FileWriter("logs", self.__sess.graph)

    def __build_net(self):

        def __build_layers(state, scope, w_init_, b_init_):
            with tf.variable_scope(scope):
                l1 = tf.layers.dense(inputs=state,
                                     units=100,
                                     activation=tf.nn.relu,
                                     kernel_initializer=w_init_,
                                     bias_initializer=b_init_,
                                     name="l1")
                v = tf.layers.dense(inputs=l1,
                                    units=1,
                                    kernel_initializer=w_init_,
                                    bias_initializer=b_init_,
                                    name="v")
                a = tf.layers.dense(inputs=l1,
                                    units=self.__num_actions,
                                    kernel_initializer=w_init_,
                                    bias_initializer=b_init_,
                                    name="a")
                a_mean = tf.reduce_mean(a, axis=1, keep_dims=True, name="reduce_mean")
                return v + a - a_mean  # Shape: (None, num_actions)

        # Inputs
        self.__state = tf.placeholder(tf.float32, [None, self.__num_features], name="state")
        self.__state_nxt = tf.placeholder(tf.float32, [None, self.__num_features], name="state_nxt")
        self.__reward = tf.placeholder(tf.float32, [None, ], name="reward")
        self.__action = tf.placeholder(tf.int32, [None, ], name="action")

        w_init = tf.random_normal_initializer(mean=0, stddev=0.3)
        b_init = tf.constant_initializer(0.1)
        indices = tf.range(tf.shape(self.__action)[0], dtype=tf.int32)

        # Eval net
        self.__q_eval_all = __build_layers(self.__state, "eval_net", w_init, b_init)

        with tf.variable_scope("q_eval"):
            action_indices = tf.stack([indices, self.__action], axis=1)
            # Shape: (None, )
            self.__q_eval = tf.gather_nd(self.__q_eval_all, action_indices, name="gather_nd")

        # Target net
        self.__q_nxt_all = __build_layers(self.__state_nxt, "target_net", w_init, b_init)

        with tf.variable_scope("q_target"):
            max_actions = tf.argmax(self.__q_eval_all, axis=1, output_type=tf.int32, name="max_actions")
            action_indices = tf.stack([indices, max_actions], axis=1)
            # Shape: (None, )
            q_target = self.__reward + self.__gamma * \
                       tf.gather_nd(self.__q_nxt_all, action_indices, name="gather_nd")
            self.__q_target = tf.stop_gradient(q_target)

        with tf.variable_scope("loss"):
            self.__loss = tf.reduce_mean(tf.squared_difference(
                self.__q_target, self.__q_eval, name="TD-error"))

        with tf.variable_scope("train"):
            self.__train = tf.train.RMSPropOptimizer(self.__lr).minimize(self.__loss)

        target_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope="target_net")
        eval_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope="eval_net")
        return target_params, eval_params

    def next_direc(self):
        return self.__actions[self.__choose_action()]

    def train(self):
        action = self.__choose_action()
        state_cur = self.map.state()
        state_nxt, reward = self.__step(action)
        self.__store_transition(state_cur, action, reward, state_nxt)
        if self.snake.steps > 5:
            self.__learn()

    def __choose_action(self):
        state = self.map.state()
        state = state[np.newaxis, :]
        oppo_direc = Direc.opposite(self.snake.direc)

        if np.random.uniform() < self.__epsilon:
            while True:
                action_idx = np.random.randint(0, self.__num_actions)
                if self.__actions[action_idx] != oppo_direc:
                    break
        else:
            # Select an action with max value
            actions_val = self.__sess.run(self.__q_eval_all, feed_dict={self.__state: state})
            max_val = None
            for i, val in enumerate(actions_val[0]):
                direc = self.__actions[i]
                if direc != oppo_direc and (max_val is None or val > max_val):
                    max_val = val
                    action_idx = i

        return action_idx

    def __step(self, action_idx):
        direc = self.__actions[action_idx]
        nxt_pos = self.snake.head().adj(direc)
        nxt_type = self.map.point(nxt_pos).type
        if nxt_type == PointType.EMPTY:
            reward = -0.1
        elif nxt_type == PointType.FOOD:
            reward = 0.1
        else:
            reward = -0.5

        self.snake.move(direc)
        if self.map.is_full():
            reward = 0.5

        return self.map.state(), reward

    def __store_transition(self, s_cur, a, r, s_nxt):
        idx = self.__mem_cnt % self.__mem_size
        self.__mem[idx, :] = np.hstack((s_cur, a, r, s_nxt))
        self.__mem_cnt += 1

    def __learn(self):
        # Replace target
        if self.__learn_steps % self.__replace_target_iter == 0:
            self.__sess.run(self.__replace_target)
            print("Target net params replaced.")

        # Sample batch from memory
        sample_indices = np.random.choice(
            min(self.__mem_size, self.__mem_cnt), size=self.__mem_batch)
        batch_mem = self.__mem[sample_indices, :]

        # Learn
        self.__sess.run(
            [self.__train, self.__loss],
            feed_dict={
                self.__state: batch_mem[:, :self.__num_features],
                self.__action: batch_mem[:, self.__num_features],
                self.__reward: batch_mem[:, self.__num_features + 1],
                self.__state_nxt: batch_mem[:, -self.__num_features:]
            }
        )

        self.__learn_steps += 1
