#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101

import os
import json
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

        self.__PARAMS = {
            "lr": 0.00025,  # Learning rate
            "momentum": 0.95,  # SGD momentum

            "freq_learn": 4,  # Frequency (snake steps) for SGD update
            "freq_replace": 10000,  # Frequency (learn steps) for target net replacement
            "freq_save": 10000,  # Frequency (learn steps) for saving model parameters

            "gamma": 0.99,  # Reward discount

            # Reward table
            "reward_tbl": {
                "empty": -0.001,
                "dead": -0.1,
                "food": 0.5,
                "full": 1.0
            },

            # Epsilon-greedy
            "epsilon_max": 0.9,
            "epsilon_min": 0.1,
            "epsilon_dec": 1e-6,

            # Replay memory
            "mem_size": 1000000,
            "mem_batch": 32
        }

        self.__DIR_LOG = "logs"
        self.__PATH_VAR = os.path.join(self.__DIR_LOG, "var-{0}.json")
        self.__PATH_MEM = os.path.join(self.__DIR_LOG, "mem-{0}.npy")
        self.__PATH_NET = os.path.join(self.__DIR_LOG, "net-{0}")

        self.__SNAKE_ACTIONS = [Direc.LEFT, Direc.UP, Direc.RIGHT, Direc.DOWN]
        self.__NUM_ACTIONS = len(self.__SNAKE_ACTIONS)
        self.__NUM_FEATURES = snake.map.capacity

        self.__RESTORE_STEPS = None

        self.__mem = np.zeros((self.__PARAMS["mem_size"], self.__NUM_FEATURES * 2 + 2))
        self.__mem_cnt = 0
        self.__epsilon = self.__PARAMS["epsilon_max"]
        self.__learn_steps = 1

        self.__build_net()
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())
        tf.summary.FileWriter(self.__DIR_LOG, self.__sess.graph)

        self.__net_saver = tf.train.Saver(self.__eval_params + self.__target_params)
        if self.__RESTORE_STEPS is not None:
            self.__load_model()

        _log("Parameters: ", self.__PARAMS)

    def __load_model(self):
        _log("Loading model ...")

        with open(self.__PATH_VAR.format(self.__RESTORE_STEPS), "r") as f:
            var = json.load(f)
        self.__mem_cnt = var["mem_cnt"]
        self.__epsilon = var["epsilon"]
        self.__mem = np.load(self.__PATH_MEM.format(self.__RESTORE_STEPS))
        self.__net_saver.restore(self.__sess, self.__PATH_NET.format(self.__RESTORE_STEPS))
        self.__learn_steps = self.__RESTORE_STEPS + 1

        _log("epsilon: ", self.__epsilon)
        _log("mem cnt: {0} | mem shape: {1}".format(self.__mem_cnt, self.__mem.shape))
        _log("Model loaded")

    def __save_model(self):
        with open(self.__PATH_VAR.format(self.__learn_steps), "w") as f:
            json.dump({
                "mem_cnt": self.__mem_cnt,
                "epsilon": self.__epsilon,
            }, f, indent=2)
        np.save(self.__PATH_MEM.format(self.__learn_steps), self.__mem)
        self.__net_saver.save(self.__sess,
                              self.__PATH_NET.format(self.__learn_steps),
                              write_meta_graph=False)

    def __build_net(self):

        def __build_layers(x, name, w_init_, b_init_):
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
            q_all = tf.layers.dense(inputs=fc1,
                                    units=self.__NUM_ACTIONS,
                                    kernel_initializer=w_init_,
                                    bias_initializer=b_init_,
                                    name=name)
            return q_all  # Shape: (None, num_actions)

        def __filter_actions(q_all, actions):
            indices = tf.range(tf.shape(q_all)[0], dtype=tf.int32)
            action_indices = tf.stack([indices, actions], axis=1)
            q = tf.gather_nd(q_all, action_indices)
            return q  # Shape: (None, )

        # Input tensor for eval net
        self.__state_eval = tf.placeholder(
            tf.float32, [None, self.__NUM_FEATURES], name="state_eval")

        # Input tensor for target net
        self.__state_target = tf.placeholder(
            tf.float32, [None, self.__NUM_FEATURES], name="state_target")

        # Input tensor for actions taken by agent
        self.__action = tf.placeholder(
            tf.int32, [None, ], name="action")

        # Input tensor for rewards received by agent
        self.__reward = tf.placeholder(
            tf.float32, [None, ], name="reward")

        # Input tensor for calculated eval net output for next state
        self.__q_eval_all_nxt = tf.placeholder(
            tf.float32, [None, self.__NUM_ACTIONS], name="q_eval_all_nxt")

        SCOPE_EVAL_NET = "eval_net"
        SCOPE_TARGET_NET = "target_net"

        w_init = tf.truncated_normal_initializer(mean=0, stddev=0.1)
        b_init = tf.constant_initializer(0.1)

        with tf.variable_scope(SCOPE_EVAL_NET):
            # Eval net output
            self.__q_eval_all = __build_layers(self.__state_eval, "q_eval_all", w_init, b_init)

        with tf.variable_scope("q_eval"):
            q_eval = __filter_actions(self.__q_eval_all, self.__action)

        with tf.variable_scope(SCOPE_TARGET_NET):
            # Target net output
            q_nxt_all = __build_layers(self.__state_target, "q_nxt_all", w_init, b_init)

        with tf.variable_scope("q_target"):
            max_actions = tf.argmax(self.__q_eval_all_nxt, axis=1, output_type=tf.int32)
            q_nxt = __filter_actions(q_nxt_all, max_actions)
            q_target = self.__reward + self.__PARAMS["gamma"] * q_nxt
            q_target = tf.stop_gradient(q_target)

        with tf.variable_scope("loss"):
            self.__loss = tf.reduce_mean(tf.squared_difference(q_eval, q_target))

        with tf.variable_scope("train"):
            self.__train = tf.train.RMSPropOptimizer(
                learning_rate=self.__PARAMS["lr"], momentum=self.__PARAMS["momentum"]
            ).minimize(self.__loss)

        # Replace target net params with eval net's
        with tf.variable_scope("replace"):
            self.__eval_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_EVAL_NET)
            self.__target_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_TARGET_NET)
            self.__replace_target = [
                tf.assign(t, e) for t, e in zip(self.__target_params, self.__eval_params)
            ]

    def next_direc(self):
        action_idx = self.__choose_action(use_e_greedy=False)
        return self.__SNAKE_ACTIONS[action_idx]

    def train(self):
        action = self.__choose_action()
        state_cur = self.map.state()
        state_nxt, reward = self.__step(action)
        self.__store_transition(state_cur, action, reward, state_nxt)
        if self.snake.steps % self.__PARAMS["freq_learn"] == 0:
            self.__learn()
        if self.__epsilon > self.__PARAMS["epsilon_min"]:
            self.__epsilon -= self.__PARAMS["epsilon_dec"]

    def __choose_action(self, use_e_greedy=True):
        if use_e_greedy and np.random.uniform() < self.__epsilon:
            action_idx = np.random.randint(0, self.__NUM_ACTIONS)
        else:
            state = self.map.state()[np.newaxis, :]
            q_eval_all = self.__sess.run(
                self.__q_eval_all,
                feed_dict={
                    self.__state_eval: state
                }
            )
            action_idx = np.argmax(q_eval_all, axis=1)[0]
        return action_idx

    def __step(self, action_idx):
        direc = self.__SNAKE_ACTIONS[action_idx]
        nxt_pos = self.snake.head().adj(direc)
        nxt_type = self.map.point(nxt_pos).type

        if nxt_type == PointType.EMPTY:
            reward = self.__PARAMS["reward_tbl"]["empty"]
        elif nxt_type == PointType.FOOD:
            reward = self.__PARAMS["reward_tbl"]["food"]
        else:
            reward = self.__PARAMS["reward_tbl"]["dead"]

        self.snake.move(direc)

        if self.map.is_full():
            reward = self.__PARAMS["reward_tbl"]["full"]

        return self.map.state(), reward

    def __store_transition(self, s_cur, a, r, s_nxt):
        idx = self.__mem_cnt % self.__PARAMS["mem_size"]
        self.__mem[idx, :] = np.hstack((s_cur, a, r, s_nxt))
        self.__mem_cnt += 1

    def __learn(self):
        log_msg = "Learning step %d | Epsilon: %f" % (self.__learn_steps, self.__epsilon)

        # Replace target
        if self.__learn_steps == 1 or self.__learn_steps % self.__PARAMS["freq_replace"] == 0:
            self.__sess.run(self.__replace_target)
            log_msg += " | Target net params replaced"

        # Save model
        if self.__learn_steps % self.__PARAMS["freq_save"] == 0:
            self.__save_model()
            log_msg += " | Model saved"

        # Sample batch from memory
        num_available = min(self.__mem_cnt, self.__PARAMS["mem_size"])
        num_sample = min(num_available, self.__PARAMS["mem_batch"])
        sample_indices = np.random.choice(num_available, size=num_sample, replace=False)
        batch = self.__mem[sample_indices, :]
        batch_state_cur = batch[:, :self.__NUM_FEATURES]
        batch_action = batch[:, self.__NUM_FEATURES].astype(np.int32)
        batch_reward = batch[:, self.__NUM_FEATURES + 1]
        batch_state_nxt = batch[:, -self.__NUM_FEATURES:]

        # Compute eval net output for next state (to compute q target)
        q_eval_all_nxt = self.__sess.run(
            self.__q_eval_all,
            feed_dict={
                self.__state_eval: batch_state_nxt,
            }
        )

        # Learn
        _, loss = self.__sess.run(
            [self.__train, self.__loss],
            feed_dict={
                self.__state_eval: batch_state_cur,
                self.__state_target: batch_state_nxt,
                self.__action: batch_action,
                self.__reward: batch_reward,
                self.__q_eval_all_nxt: q_eval_all_nxt
            }
        )
        log_msg += " | Loss: %f" % loss

        self.__learn_steps += 1
        _log(log_msg)
