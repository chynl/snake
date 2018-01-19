#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101

import json
import os
from datetime import datetime

import numpy as np
import tensorflow as tf

from snake.base import Direc, PointType
from snake.solver.base import BaseSolver


_DIR_LOG = "logs"


def _log(*msgs):
    msg_str = ""
    for msg in msgs:
        msg_str += str(msg)
    print("[%s]" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg_str)


class _SumTree:

    PATH_TREE = os.path.join(_DIR_LOG, "sumtree-tree-%d.npy")
    PATH_DATA = os.path.join(_DIR_LOG, "sumtree-data-%d.npy")
    PATH_VAR = os.path.join(_DIR_LOG, "sumtree-var-%d.json")

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

    def save(self, steps):
        np.save(_SumTree.PATH_TREE % steps, self.__tree)
        np.save(_SumTree.PATH_DATA % steps, self.__data)
        with open(_SumTree.PATH_VAR % steps, "w") as f:
            json.dump({
                "capacity": self.__capacity,
                "data_idx": self.__data_idx,
            }, f, indent=2)

    def load(self, steps):
        self.__tree = np.load(_SumTree.PATH_TREE % steps)
        self.__data = np.load(_SumTree.PATH_DATA % steps)
        with open(_SumTree.PATH_VAR % steps, "r") as f:
            var = json.load(f)
        self.__capacity = var["capacity"]
        self.__data_idx = var["data_idx"]
        _log("sum tree loaded | tree shape: {} | data shape: {} | capacity: {} | data_idx: {}"
             .format(self.__tree.shape, self.__data.shape, self.__capacity, self.__data_idx))

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


class _Memory:

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
        with open(_Memory.PATH_VAR % steps, "w") as f:
            json.dump({
                "beta": self.__beta,
            }, f, indent=2)

    def load(self, steps):
        self.__tree.load(steps)
        with open(_Memory.PATH_VAR % steps, "r") as f:
            var = json.load(f)
        self.__beta = var["beta"]
        _log("memory loaded | beta: %.6f" % (self.__beta))

    def store(self, transition):
        max_priority = np.max(self.__tree.leaves())
        if max_priority == 0:
            max_priority = self.__ABS_ERR_UPPER
        self.__tree.insert(transition, max_priority)

    def sample(self, num_samples):
        tree_indices = np.zeros((num_samples, ), dtype=np.int32)
        batch_mem = np.zeros((num_samples, self.__tree.data[0].size))
        IS_weights = np.zeros((num_samples, ))  # Importance-sampling (IS) weights

        len_seg = self.__tree.sum() / num_samples
        min_prob = min(self.__tree.leaves()) / self.__tree.sum()

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


class DQNSolver(BaseSolver):

    PATH_VAR = os.path.join(_DIR_LOG, "solver-var-%d.json")
    PATH_NET = os.path.join(_DIR_LOG, "solver-net-%d")

    def __init__(self, snake):
        super().__init__(snake)

        # Rewards
        self.__RWD_EMPTY = -0.001
        self.__RWD_DEAD = -0.1
        self.__RWD_FOOD = 0.5
        self.__RWD_FULL = 1.0

        # Epsilon-greedy
        self.__EPSILON_MAX = 1.0
        self.__EPSILON_MIN = 0.1
        self.__EPSILON_DEC = 1e-6

        # Memory
        self.__MEM_SIZE = 1000
        self.__MEM_BATCH = 32

        # Frequency
        self.__FREQ_LEARN = 4        # Number of new transitions
        self.__FREQ_REPLACE = 10000  # Learn steps
        self.__FREQ_SAVE = 10000     # Learn steps

        self.__LR = 0.00025 / 4      # Learning rate
        self.__MOMENTUM = 0.95       # SGD momentum
        self.__GAMMA = 0.99          # Reward discount

        self.__ALPHA = 0.6           # How much prioritization to use
        self.__BETA_MIN = 0.4        # Importance-sampling (IS)
        self.__BETA_INC = 1e-6
        self.__PRI_EPSILON = 1e-6    # Small positive value to avoid zero priority
        self.__ABS_ERR_UPPER = 1     # TD-error (absolute value) clip upperbound

        self.__RESTORE_STEP = None  # Which learn step to restore

        self.__SNAKE_ACTIONS = [Direc.LEFT, Direc.UP, Direc.RIGHT, Direc.DOWN]
        self.__NUM_ACTIONS = len(self.__SNAKE_ACTIONS)
        self.__NUM_FEATURES = snake.map.capacity

        self.__mem = _Memory(mem_size=self.__MEM_SIZE, alpha=self.__ALPHA,
                             beta_min=self.__BETA_MIN, beta_inc=self.__BETA_INC,
                             pri_epsilon=self.__PRI_EPSILON, abs_err_upper=self.__ABS_ERR_UPPER)
        self.__mem_cnt = 0
        self.__epsilon = self.__EPSILON_MAX
        self.__learn_step = 1

        eval_params, target_params = self.__build_net()
        self.__net_saver = tf.train.Saver(eval_params + target_params)

        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())
        tf.summary.FileWriter(_DIR_LOG, self.__sess.graph)

        if self.__RESTORE_STEP is not None:
            self.__load_model()

    def __save_model(self):
        self.__mem.save(self.__learn_step)
        self.__net_saver.save(self.__sess, DQNSolver.PATH_NET % self.__learn_step,
                              write_meta_graph=False)
        with open(DQNSolver.PATH_VAR % self.__learn_step, "w") as f:
            json.dump({
                "mem_cnt": self.__mem_cnt,
                "epsilon": self.__epsilon,
            }, f, indent=2)

    def __load_model(self):
        self.__mem.load(self.__RESTORE_STEP)
        self.__net_saver.restore(self.__sess, DQNSolver.PATH_NET % self.__RESTORE_STEP)
        with open(DQNSolver.PATH_VAR % self.__RESTORE_STEP, "r") as f:
            var = json.load(f)
        self.__mem_cnt = var["mem_cnt"]
        self.__epsilon = var["epsilon"]
        self.__learn_step = self.__RESTORE_STEP + 1
        _log("model loaded | RESTORE_STEP: %d | mem_cnt: %d | epsilon: %.6f"
             % (self.__RESTORE_STEP, self.__mem_cnt, self.__epsilon))

    def __build_net(self):

        def __build_layers(x, name, w_init_, b_init_):
            input_2d = tf.reshape(x, [-1, 10, 10, 1], name="input_2d")
            conv1 = tf.layers.conv2d(inputs=input_2d,
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
            conv3_flat = tf.reshape(conv3, [-1, 4 * 4 * 64], name="conv3_flat")
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
            return tf.gather_nd(q_all, action_indices)  # Shape: (None, )

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

        # Input tensor for eval net output of next state
        self.__q_eval_all_nxt = tf.placeholder(
            tf.float32, [None, self.__NUM_ACTIONS], name="q_eval_all_nxt")

        # Input tensor for importance-sampling weights
        self.__IS_weights = tf.placeholder(
            tf.float32, [None, ], name="IS_weights")

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
            # Double DQN: choose max reward actions using eval net
            max_actions = tf.argmax(self.__q_eval_all_nxt, axis=1, output_type=tf.int32)
            q_nxt = __filter_actions(q_nxt_all, max_actions)
            q_target = self.__reward + self.__GAMMA * q_nxt
            q_target = tf.stop_gradient(q_target)

        with tf.variable_scope("loss"):
            self.__loss = tf.reduce_mean(self.__IS_weights \
                * tf.squared_difference(q_eval, q_target), name="loss")
            self.__abs_errs = tf.abs(q_eval - q_target, name="abs_errs")  # To update sum tree

        with tf.variable_scope("train"):
            self.__train = tf.train.RMSPropOptimizer(
                learning_rate=self.__LR, momentum=self.__MOMENTUM
            ).minimize(self.__loss)

        # Replace target net params with eval net's
        with tf.variable_scope("replace"):
            eval_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_EVAL_NET)
            target_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_TARGET_NET)
            self.__replace_target = [
                tf.assign(t, e) for t, e in zip(target_params, eval_params)
            ]

        return eval_params, target_params

    def next_direc(self):
        return self.__SNAKE_ACTIONS[self.__choose_action(e_greedy=False)]

    def train(self):
        action = self.__choose_action()
        state_cur = self.map.state()
        reward, state_nxt = self.__step(action)
        self.__store_transition(state_cur, action, reward, state_nxt)

        if self.__mem_cnt >= self.__MEM_SIZE:
            if self.__mem_cnt % self.__FREQ_LEARN == 0:
                self.__learn()
        else:
            _log("mem_cnt: %d" % self.__mem_cnt)

        self.__epsilon = max(self.__EPSILON_MIN, self.__epsilon - self.__EPSILON_DEC)

    def __choose_action(self, e_greedy=True):
        if e_greedy and np.random.uniform() < self.__epsilon:
            action_idx = np.random.randint(0, self.__NUM_ACTIONS)
        else:
            state = self.map.state()[np.newaxis, :]
            q_eval_all = self.__sess.run(
                self.__q_eval_all,
                feed_dict={
                    self.__state_eval: state,
                }
            )
            action_idx = np.argmax(q_eval_all, axis=1)[0]
        return action_idx

    def __step(self, action_idx):
        direc = self.__SNAKE_ACTIONS[action_idx]
        nxt_pos = self.snake.head().adj(direc)
        nxt_type = self.map.point(nxt_pos).type

        if nxt_type == PointType.EMPTY:
            reward = self.__RWD_EMPTY
        elif nxt_type == PointType.FOOD:
            reward = self.__RWD_FOOD
        else:
            reward = self.__RWD_DEAD

        self.snake.move(direc)

        if self.map.is_full():
            reward = self.__RWD_FULL

        return reward, self.map.state()

    def __store_transition(self, state_cur, action, reward, state_nxt):
        self.__mem.store(np.hstack((state_cur, action, reward, state_nxt)))
        self.__mem_cnt += 1

    def __learn(self):
        log_msg = "step %d | mem_cnt: %d | epsilon: %.6f | beta: %.6f" % \
                  (self.__learn_step, self.__mem_cnt, self.__epsilon, self.__mem.beta)

        # Replace target
        if self.__learn_step == 1 or self.__learn_step % self.__FREQ_REPLACE == 0:
            self.__sess.run(self.__replace_target)
            log_msg += " | target net replaced"

        # Save model
        if self.__learn_step % self.__FREQ_SAVE == 0:
            self.__save_model()
            log_msg += " | model saved"

        # Sample batch from memory
        tree_indices, batch, IS_weights = self.__mem.sample(self.__MEM_BATCH)
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
        _, loss, abs_errs = self.__sess.run(
            [self.__train, self.__loss, self.__abs_errs],
            feed_dict={
                self.__state_eval: batch_state_cur,
                self.__state_target: batch_state_nxt,
                self.__action: batch_action,
                self.__reward: batch_reward,
                self.__q_eval_all_nxt: q_eval_all_nxt,
                self.__IS_weights: IS_weights,
            }
        )
        log_msg += " | loss: %.6f" % loss

        # Update sum tree
        self.__mem.update(tree_indices, abs_errs)

        self.__learn_step += 1
        _log(log_msg)
