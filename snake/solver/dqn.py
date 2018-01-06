#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101

from datetime import datetime
import numpy as np
import tensorflow as tf
from snake.base import Direc, PointType
from snake.solver.base import BaseSolver


def _log(*msgs):
    msg_str = ""
    for msg in msgs:
        msg_str += str(msg)
    print("[%s]" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg_str)


class DQNSolver(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)

        # Learning rate
        self.__lr = 0.00025

        # Gradient momemtum
        self.__momentum = 0.95

        # Reward decay
        self.__gamma = 0.99

        # Epsilon-greedy
        self.__epsilon_max = 1
        self.__epsilon_min = 0.1
        self.__epsilon_decreasement = 1e-6
        self.__epsilon = self.__epsilon_max

        # Frequency (snake steps) for SGD update
        self.__learn_frequency = 4

        # Frequency (learn steps) for replacement of target net parameters
        self.__replace_target_iter = 10000

        # Number of actions and features
        self.__actions = [Direc.LEFT, Direc.UP, Direc.RIGHT, Direc.DOWN]
        self.__num_actions = len(self.__actions)
        self.__num_features = snake.map.capacity

        # Reward values
        self.__reward_dict = {
            "EMPTY": -0.001,
            "DEAD": -0.1,
            "FOOD": 0.1,
            "FULL": 1.0
        }

        # Replay memory
        self.__mem_size = 1000000
        self.__mem_batch = 32
        self.__mem_cnt = 0
        self.__mem = np.zeros((self.__mem_size, self.__num_features * 2 + 2))

        # Current learning step
        self.__learn_steps = 0

        # Build two networks and get parameters
        eval_params, target_params = self.__build_net()

        # Replace target network parameters
        self.__replace_target = [tf.assign(t, e) for t, e in zip(target_params, eval_params)]

        # Create tensorflow session
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())

        # Write graph logs
        log_dir = "./logs"
        tf.summary.FileWriter(log_dir, self.__sess.graph)
        _log("logdir: %s" % log_dir)

    def __build_net(self):

        def __build_layers(x, scope, w_init_, b_init_):
            with tf.variable_scope(scope):
                x_2d = tf.reshape(x, [-1, 10, 10, 1])
                conv1 = tf.layers.conv2d(inputs=x_2d,
                                         filters=32,
                                         kernel_size=3,
                                         strides=1,
                                         padding='valid',
                                         activation=tf.nn.relu,
                                         kernel_initializer=w_init_,
                                         bias_initializer=b_init_,
                                         name="conv1")
                conv2 = tf.layers.conv2d(inputs=conv1,
                                         filters=64,
                                         kernel_size=3,
                                         strides=1,
                                         padding='valid',
                                         activation=tf.nn.relu,
                                         kernel_initializer=w_init_,
                                         bias_initializer=b_init_,
                                         name="conv2")
                conv3 = tf.layers.conv2d(inputs=conv2,
                                         filters=64,
                                         kernel_size=3,
                                         strides=1,
                                         padding='valid',
                                         activation=tf.nn.relu,
                                         kernel_initializer=w_init_,
                                         bias_initializer=b_init_,
                                         name="conv3")
                conv3_flat = tf.reshape(conv3, [-1, 4 * 4 * 64])
                fc1 = tf.layers.dense(inputs=conv3_flat,
                                      units=512,
                                      activation=tf.nn.relu,
                                      kernel_initializer=w_init_,
                                      bias_initializer=b_init_,
                                      name="fc1")
                q = tf.layers.dense(inputs=fc1,
                                    units=self.__num_actions,
                                    kernel_initializer=w_init_,
                                    bias_initializer=b_init_,
                                    name="q")
                return q  # Shape: (None, num_actions)

        # Input tensor for eval net
        self.__state_eval = tf.placeholder(
            tf.float32, [None, self.__num_features], name="state_eval")

        # Input tensor for target net
        self.__state_target = tf.placeholder(
            tf.float32, [None, self.__num_features], name="state_target")

        # Input tensor for actions taken by agent
        self.__actions_taken = tf.placeholder(
            tf.int32, [None, ], name="actions_taken")

        # Input tensor for calculated q target
        self.__q_target = tf.placeholder(
            tf.float32, [None, ], name="q_target")

        scope_eval, scope_target = "eval_net", "target_net"
        w_init = tf.truncated_normal_initializer(mean=0, stddev=0.1)
        b_init = tf.constant_initializer(0.1)

        # Eval net output / Shape: (None, num_actions)
        self.__q_eval_all = __build_layers(self.__state_eval, scope_eval, w_init, b_init)

        with tf.variable_scope("q_eval"):
            indices = tf.range(tf.shape(self.__state_eval)[0], dtype=tf.int32)
            action_indices = tf.stack([indices, self.__actions_taken], axis=1)
            # Shape: (None, )
            self.__q_eval = tf.gather_nd(self.__q_eval_all, action_indices)

        # Target net output / Shape: (None, num_actions)
        self.__q_nxt_all = __build_layers(self.__state_target, scope_target, w_init, b_init)

        with tf.variable_scope("loss"):
            self.__loss = tf.reduce_mean(tf.squared_difference(self.__q_target, self.__q_eval))

        with tf.variable_scope("train"):
            self.__train = tf.train.RMSPropOptimizer(
                learning_rate=self.__lr, momentum=self.__momentum).minimize(self.__loss)

        eval_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=scope_eval)
        target_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=scope_target)

        return eval_params, target_params

    def next_direc(self):
        return self.__actions[self.__choose_action()]

    def train(self):
        action = self.__choose_action()
        state_cur = self.map.state()
        state_nxt, reward = self.__step(action)
        self.__store_transition(state_cur, action, reward, state_nxt)
        if self.snake.steps % self.__learn_frequency == 0:
            self.__learn()
        if self.__epsilon > self.__epsilon_min:
            self.__epsilon -= self.__epsilon_decreasement

    def __choose_action(self):
        oppo_direc = Direc.opposite(self.snake.direc)

        if np.random.uniform() < self.__epsilon:
            while True:
                action_idx = np.random.randint(0, self.__num_actions)
                if self.__actions[action_idx] != oppo_direc:
                    break
        else:
            state = self.map.state()
            state = state[np.newaxis, :]
            q_eval_all = self.__sess.run(
                self.__q_eval_all,
                feed_dict={
                    self.__state_eval: state
                }
            )
            # Select an action with max value
            max_val = None
            for i, val in enumerate(q_eval_all[0]):
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
            reward = self.__reward_dict["EMPTY"]
        elif nxt_type == PointType.FOOD:
            reward = self.__reward_dict["FOOD"]
        else:
            reward = self.__reward_dict["DEAD"]

        self.snake.move(direc)
        if self.map.is_full():
            reward = self.__reward_dict["FULL"]

        return self.map.state(), reward

    def __store_transition(self, s_cur, a, r, s_nxt):
        idx = self.__mem_cnt % self.__mem_size
        self.__mem[idx, :] = np.hstack((s_cur, a, r, s_nxt))
        self.__mem_cnt += 1

    def __learn(self):
        log_msg = "Learning step %d | Epsilon: %f" % (self.__learn_steps, self.__epsilon)

        # Replace target
        if self.__learn_steps % self.__replace_target_iter == 0:
            self.__sess.run(self.__replace_target)
            log_msg += " | Target net params replaced"

        # Sample batch from memory
        num_available = min(self.__mem_size, self.__mem_cnt)
        sample_indices = np.random.choice(
            num_available, size=min(num_available, self.__mem_batch), replace=False)
        batch = self.__mem[sample_indices, :]
        batch_indices = np.arange(batch.shape[0], dtype=np.int32)
        batch_state_cur = batch[:, :self.__num_features]
        batch_action = batch[:, self.__num_features].astype(np.int32)
        batch_reward = batch[:, self.__num_features + 1]
        batch_state_nxt = batch[:, -self.__num_features:]

        # Compute q target
        q_nxt_all, q_eval_all_nxt = self.__sess.run(
            [self.__q_nxt_all, self.__q_eval_all],
            feed_dict={
                self.__state_eval: batch_state_nxt,
                self.__state_target: batch_state_nxt
            }
        )
        max_actions = np.argmax(q_eval_all_nxt, axis=1)
        q_nxt = q_nxt_all[batch_indices, max_actions]
        q_target = batch_reward + self.__gamma * q_nxt

        # Learn
        _, loss = self.__sess.run(
            [self.__train, self.__loss],
            feed_dict={
                self.__state_eval: batch_state_cur,
                self.__actions_taken: batch_action,
                self.__q_target: q_target
            }
        )
        log_msg += " | Loss: %f" % loss

        _log(log_msg)
        self.__learn_steps += 1
