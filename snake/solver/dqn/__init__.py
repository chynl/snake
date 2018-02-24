#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,E1101

"""DQN Solver package."""

import json
import os

import numpy as np
import tensorflow as tf

import matplotlib.pyplot as plt

from snake.base import Direc, Pos, PointType
from snake.solver.base import BaseSolver
from snake.solver.dqn.memory import Memory
from snake.solver.dqn.logger import log
from snake.solver.dqn.snakeaction import SnakeAction

_DIR_LOG = "logs"


class DQNSolver(BaseSolver):

    PATH_VAR = os.path.join(_DIR_LOG, "solver-var-%d.json")
    PATH_NET = os.path.join(_DIR_LOG, "solver-net-%d")

    def __init__(self, snake):
        super().__init__(snake)

        self._MAX_LEARN_STEP = 1000000   # Expected maximum learning steps
        self._RESTORE_STEP = 0           # Which learning step to restore (0 means not restore)

        # Rewards
        self._RWD_EMPTY = -0.005
        self._RWD_DEAD = -0.5
        self._RWD_FOOD = 1.0

        # Memory
        self._MEM_SIZE = 100000
        self._MEM_BATCH = 32

        # Epsilon-greedy
        self._EPSILON_MAX = 1.0
        self._EPSILON_MIN = 0.01
        self._EPSILON_DEC = (self._EPSILON_MAX - self._EPSILON_MIN) / self._MAX_LEARN_STEP

        self._LR = 1e-6             # Learning rate
        self._MOMENTUM = 0.95       # SGD momentum
        self._GAMMA = 0.99          # Reward discount
        self._LEAKY_ALPHA = 0.01    # Leaky relu slope

        self._TD_UPPER = 1.0        # TD-error clip upper bound
        self._TD_LOWER = -1.0       # TD-error clip lower bound

        self._PRI_EPSILON = 0.001   # Small positive value to avoid zero priority
        self._ALPHA = 0.6           # How much prioritization to use
        self._BETA_MIN = 0.4        # How much to compensate for the non-uniform probabilities
        self._BETA_INC = (1.0 - self._BETA_MIN) / self._MAX_LEARN_STEP

        # Frequency
        self._FREQ_LEARN = 4        # Number of new transitions
        self._FREQ_REPLACE = 10000  # Learning steps
        self._FREQ_LOG = 500        # Learning steps
        self._FREQ_SAVE = 20000     # Learning steps

        self._NUM_AVG_RWD = 50      # How many latest reward history to compute average

        self._SNAKE_ACTIONS = [SnakeAction.LEFT, SnakeAction.FORWARD, SnakeAction.RIGHT]
        self._NUM_ACTIONS = len(self._SNAKE_ACTIONS)

        self._SHAPE_VISUAL_STATE = (self.map.num_rows - 2, self.map.num_cols - 2, 4)
        self._NUM_VISUAL_FEATURES = np.prod(self._SHAPE_VISUAL_STATE)
        self._NUM_IMPORTANT_FEATURES = 3
        self._NUM_ALL_FEATURES = self._NUM_VISUAL_FEATURES + self._NUM_IMPORTANT_FEATURES

        self._mem = Memory(mem_size=self._MEM_SIZE,
                            alpha=self._ALPHA,
                            epsilon=self._PRI_EPSILON)
        self._mem_cnt = 0

        self._learn_step = 1
        self._epsilon = self._EPSILON_MAX
        self._beta = self._BETA_MIN

        self._tot_reward = 0
        self._history_loss = []
        self._history_reward = []
        self._history_avg_reward = []
        self._max_avg_reward = -1.0

        eval_params, target_params = self._build_graph()
        self._net_saver = tf.train.Saver(var_list=eval_params + target_params,
                                          max_to_keep=200)

        self._sess = tf.Session()
        self._sess.run(tf.global_variables_initializer())
        self._summary_writer = tf.summary.FileWriter(_DIR_LOG, self._sess.graph)

        if self._RESTORE_STEP > 0:
            self._load_model()

    def _save_model(self):
        self._net_saver.save(self._sess, DQNSolver.PATH_NET % self._learn_step,
                              write_meta_graph=False)
        with open(DQNSolver.PATH_VAR % self._learn_step, "w") as f:
            json.dump({
                "epsilon": self._epsilon,
                "beta": self._beta,
            }, f, indent=2)

    def _load_model(self):
        self._net_saver.restore(self._sess, DQNSolver.PATH_NET % self._RESTORE_STEP)
        with open(DQNSolver.PATH_VAR % self._RESTORE_STEP, "r") as f:
            var = json.load(f)
        self._epsilon = var["epsilon"]
        self._beta = var["beta"]
        self._learn_step = self._RESTORE_STEP + 1
        log("model loaded | RESTORE_STEP: %d | epsilon: %.6f | beta: %.6f"
            % (self._RESTORE_STEP, self._epsilon, self._beta))

    def _build_graph(self):

        # Input tensor for eval net
        self._state_eval = tf.placeholder(
            tf.float32, [None, self._NUM_ALL_FEATURES], name="state_eval")

        # Input tensor for target net
        self._state_target = tf.placeholder(
            tf.float32, [None, self._NUM_ALL_FEATURES], name="state_target")

        # Input tensor for actions taken by agent
        self._action = tf.placeholder(
            tf.int32, [None, ], name="action")

        # Input tensor for rewards received by agent
        self._reward = tf.placeholder(
            tf.float32, [None, ], name="reward")

        # Input tensor for whether episodes are finished
        self._done = tf.placeholder(
            tf.bool, [None, ], name="done")

        # Input tensor for eval net output of next state
        self._q_eval_all_nxt = tf.placeholder(
            tf.float32, [None, self._NUM_ACTIONS], name="q_eval_all_nxt")

        # Input tensor for importance-sampling weights
        self._IS_weights = tf.placeholder(
            tf.float32, [None, ], name="IS_weights")

        SCOPE_EVAL_NET = "eval_net"
        SCOPE_TARGET_NET = "target_net"

        w_init = tf.keras.initializers.he_normal()
        b_init = tf.constant_initializer(0)

        with tf.variable_scope(SCOPE_EVAL_NET):
            # Eval net output
            self._q_eval_all = self._build_net(self._state_eval, "q_eval_all", w_init, b_init)

        with tf.variable_scope("q_eval"):
            q_eval = self._filter_actions(self._q_eval_all, self._action)

        with tf.variable_scope(SCOPE_TARGET_NET):
            # Target net output
            q_nxt_all = self._build_net(self._state_target, "q_nxt_all", w_init, b_init)

        with tf.variable_scope("q_target"):
            # Natural DQN
            #max_actions = tf.argmax(q_nxt_all, axis=1, output_type=tf.int32)
            # Double DQN: choose max reward actions using eval net
            max_actions = tf.argmax(self._q_eval_all_nxt, axis=1, output_type=tf.int32)
            q_nxt = self._filter_actions(q_nxt_all, max_actions)
            q_target = self._reward + self._GAMMA * q_nxt * \
                (1.0 - tf.cast(self._done, tf.float32))
            q_target = tf.stop_gradient(q_target)

        with tf.variable_scope("loss"):
            with tf.variable_scope("td_err"):
                td_err = tf.clip_by_value(
                    q_eval - q_target,
                    clip_value_min=self._TD_LOWER,
                    clip_value_max=self._TD_UPPER,
                )
            self._loss = tf.reduce_mean(self._IS_weights * tf.square(td_err))
            self._td_err_abs = tf.abs(td_err, name="td_err_abs")  # To update sum tree

        with tf.variable_scope("train"):
            self._train = tf.train.RMSPropOptimizer(
                learning_rate=self._LR, momentum=self._MOMENTUM
            ).minimize(self._loss)

        # Replace target net params with eval net's
        with tf.variable_scope("replace"):
            eval_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_EVAL_NET)
            target_params = tf.get_collection(
                tf.GraphKeys.GLOBAL_VARIABLES, scope=SCOPE_TARGET_NET)
            self._replace_target = [
                tf.assign(t, e) for t, e in zip(target_params, eval_params)
            ]

        return eval_params, target_params

    def _build_net(self, features, output_name, w_init_, b_init_):

        visual_state = tf.slice(features,
                                begin=[0, 0],
                                size=[-1, self._NUM_VISUAL_FEATURES],
                                name="visual_state")

        visual_state_2d = tf.reshape(tensor=visual_state,
                                     shape=[-1,
                                            self._SHAPE_VISUAL_STATE[0],
                                            self._SHAPE_VISUAL_STATE[1],
                                            self._SHAPE_VISUAL_STATE[2]],
                                     name="visual_state_2d")

        conv1 = tf.layers.conv2d(inputs=visual_state_2d,
                                 filters=32,
                                 kernel_size=3,
                                 strides=1,
                                 padding='valid',
                                 activation=self._leaky_relu,
                                 kernel_initializer=w_init_,
                                 bias_initializer=b_init_,
                                 name="conv1")

        conv2 = tf.layers.conv2d(inputs=conv1,
                                 filters=64,
                                 kernel_size=3,
                                 strides=1,
                                 padding='valid',
                                 activation=self._leaky_relu,
                                 kernel_initializer=w_init_,
                                 bias_initializer=b_init_,
                                 name="conv2")

        conv3 = tf.layers.conv2d(inputs=conv2,
                                 filters=128,
                                 kernel_size=2,
                                 strides=1,
                                 padding='valid',
                                 activation=self._leaky_relu,
                                 kernel_initializer=w_init_,
                                 bias_initializer=b_init_,
                                 name="conv3")

        conv4 = tf.layers.conv2d(inputs=conv3,
                                 filters=256,
                                 kernel_size=2,
                                 strides=1,
                                 padding='valid',
                                 activation=self._leaky_relu,
                                 kernel_initializer=w_init_,
                                 bias_initializer=b_init_,
                                 name="conv4")

        conv4_flat = tf.reshape(tensor=conv4,
                                shape=[-1, 2 * 2 * 256],
                                name="conv4_flat")

        important_state = tf.slice(features,
                                   begin=[0, self._NUM_VISUAL_FEATURES],
                                   size=[-1, self._NUM_IMPORTANT_FEATURES],
                                   name="important_state")

        combined_features = tf.concat([conv4_flat, important_state],
                                      axis=1,
                                      name="combined_features")

        fc1 = tf.layers.dense(inputs=combined_features,
                              units=1024,
                              activation=self._leaky_relu,
                              kernel_initializer=w_init_,
                              bias_initializer=b_init_,
                              name="fc1")

        fc2 = tf.layers.dense(inputs=fc1,
                              units=1024,
                              activation=self._leaky_relu,
                              kernel_initializer=w_init_,
                              bias_initializer=b_init_,
                              name="fc2")

        q_all = tf.layers.dense(inputs=fc2,
                                units=self._NUM_ACTIONS,
                                kernel_initializer=w_init_,
                                bias_initializer=b_init_,
                                name=output_name)

        return q_all  # Shape: (None, num_actions)

    def _leaky_relu(self, features):
        return tf.nn.leaky_relu(features, alpha=self._LEAKY_ALPHA)

    def _filter_actions(self, q_all, actions):
        with tf.variable_scope("action_filter"):
            indices = tf.range(tf.shape(q_all)[0], dtype=tf.int32)
            action_indices = tf.stack([indices, actions], axis=1)
            return tf.gather_nd(q_all, action_indices)  # Shape: (None, )

    def next_direc(self):
        """Override super class."""
        action = self._SNAKE_ACTIONS[self._choose_action(e_greedy=False)]
        return SnakeAction.to_direc(action, self.snake.direc)

    def plot(self):
        plt.figure()
        plt.plot(range(1, len(self._history_reward) + 1), self._history_reward)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Total Reward")

        plt.figure()
        steps = np.arange(len(self._history_loss)) + self._RESTORE_STEP + 1
        plt.plot(steps, self._history_loss)
        plt.xlabel("Learn Step")
        plt.ylabel("Loss")
        plt.title("Loss")

        plt.figure()
        steps = np.arange(len(self._history_avg_reward)) + self._RESTORE_STEP + 1
        plt.plot(steps, self._history_avg_reward)
        plt.xlabel("Learn Step")
        plt.ylabel("Reward")
        plt.title("Average Reward")

        plt.show()

    def close(self):
        """Override super class."""
        if self._summary_writer:
            self._summary_writer.close()
        if self._sess:
            self._sess.close()

    def train(self):
        state_cur = self._state()
        action = self._choose_action()
        reward, state_nxt, done = self._step(action)
        self._store_transition(state_cur, action, reward, state_nxt, done)

        self._tot_reward += reward
        if done:
            self._history_reward.append(self._tot_reward)
            self._tot_reward = 0

        if self._mem_cnt >= self._MEM_SIZE:
            if self._mem_cnt % self._FREQ_LEARN == 0:
                self._learn()
        elif self._mem_cnt % self._FREQ_LOG == 0:
            log("mem_cnt: %d" % self._mem_cnt)

        return done

    def _state(self):
        """Return a vector indicating current state."""

        # Visual state
        visual_state = np.zeros(self._SHAPE_VISUAL_STATE, dtype=np.int32)
        for i in range(1, self.map.num_rows - 1):
            for j in range(1, self.map.num_cols - 1):

                # Relative position
                pos = None
                if self.snake.direc == Direc.LEFT:
                    pos = Pos(self.map.num_rows - 1 - j, i)
                elif self.snake.direc == Direc.UP:
                    pos = Pos(i, j)
                elif self.snake.direc == Direc.RIGHT:
                    pos = Pos(j, self.map.num_cols - 1 - i)
                elif self.snake.direc == Direc.DOWN:
                    pos = Pos(self.map.num_rows - 1 - i, self.map.num_cols - 1 - j)

                t = self.map.point(pos).type
                if t == PointType.EMPTY:
                    visual_state[i - 1][j - 1][0] = 1
                elif t == PointType.FOOD:
                    visual_state[i - 1][j - 1][1] = 1
                elif t == PointType.HEAD_L or t == PointType.HEAD_U or \
                     t == PointType.HEAD_R or t == PointType.HEAD_D:
                    visual_state[i - 1][j - 1][2] = 1
                elif t == PointType.BODY_LU  or t == PointType.BODY_UR or \
                     t == PointType.BODY_RD  or t == PointType.BODY_DL or \
                     t == PointType.BODY_HOR or t == PointType.BODY_VER:
                    visual_state[i - 1][j - 1][3] = 1
                else:
                    raise ValueError("Unsupported PointType: {}".format(t))

        # return visual_state.flatten()

        # Important state
        important_state = np.zeros(self._NUM_IMPORTANT_FEATURES, dtype=np.int32)
        head = self.snake.head()
        for i, action in enumerate([SnakeAction.LEFT, SnakeAction.FORWARD, SnakeAction.RIGHT]):
            direc = SnakeAction.to_direc(action, self.snake.direc)
            if not self.map.is_safe(head.adj(direc)):
                important_state[i] = 1

        return np.hstack((visual_state.flatten(), important_state))

    def _choose_action(self, e_greedy=True):
        action_idx = None

        if e_greedy and np.random.uniform() < self._epsilon:
            while True:
                action_idx = np.random.randint(0, self._NUM_ACTIONS)
                if Direc.opposite(self.snake.direc) != self._SNAKE_ACTIONS[action_idx]:
                    break
        else:
            q_eval_all = self._sess.run(
                self._q_eval_all,
                feed_dict={
                    self._state_eval: self._state()[np.newaxis, :]
                }
            )
            q_eval_all = q_eval_all[0]
            # Find indices of actions with 1st and 2nd largest q value
            action_indices = np.argpartition(q_eval_all, q_eval_all.size - 2)
            action_idx = action_indices[-1]
            # If opposite direction, return direction with 2nd largest q value
            if Direc.opposite(self.snake.direc) == self._SNAKE_ACTIONS[action_idx]:
                action_idx = action_indices[-2]

        return action_idx

    def _step(self, action_idx):
        action = self._SNAKE_ACTIONS[action_idx]
        direc = SnakeAction.to_direc(action, self.snake.direc)
        nxt_pos = self.snake.head().adj(direc)
        nxt_type = self.map.point(nxt_pos).type
        self.snake.move(direc)

        reward = 0
        if nxt_type == PointType.EMPTY:
            reward = self._RWD_EMPTY
        elif nxt_type == PointType.FOOD:
            reward = self._RWD_FOOD
        else:
            reward = self._RWD_DEAD

        state_nxt = self._state()
        done = self.snake.dead or self.map.is_full()

        return reward, state_nxt, done

    def _store_transition(self, state_cur, action, reward, state_nxt, done):
        self._mem.store((state_cur, action, reward, state_nxt, done))
        self._mem_cnt += 1

    def _learn(self):
        log_msg = "step %d | mem_cnt: %d | epsilon: %.6f | beta: %.6f" % \
                  (self._learn_step, self._mem_cnt, self._epsilon, self._beta)

        # Compute average reward
        avg_reward = self._max_avg_reward
        if self._history_reward:
            avg_reward = np.mean(self._history_reward[-self._NUM_AVG_RWD:])
        self._history_avg_reward.append(avg_reward)
        log_msg += " | avg_reward: %.6f" % avg_reward

        # Save model
        saved = False
        if avg_reward > self._max_avg_reward or self._learn_step % self._FREQ_SAVE == 0:
            if avg_reward > self._max_avg_reward:
                self._max_avg_reward = avg_reward
            self._save_model()
            saved = True
            log_msg += " | model saved"

        # Sample batch from memory
        batch, IS_weights, tree_indices = self._mem.sample(self._MEM_BATCH, self._beta)
        batch_state_cur = [x[0] for x in batch]
        batch_action = [x[1] for x in batch]
        batch_reward = [x[2] for x in batch]
        batch_state_nxt = [x[3] for x in batch]
        batch_done = [x[4] for x in batch]

        # Compute eval net output for next state (to compute q target)
        q_eval_all_nxt = self._sess.run(
            self._q_eval_all,
            feed_dict={
                self._state_eval: batch_state_nxt,
            }
        )

        # Learn
        _, loss, abs_errs = self._sess.run(
            [self._train, self._loss, self._td_err_abs],
            feed_dict={
                self._state_eval: batch_state_cur,
                self._state_target: batch_state_nxt,
                self._action: batch_action,
                self._reward: batch_reward,
                self._done: batch_done,
                self._q_eval_all_nxt: q_eval_all_nxt,
                self._IS_weights: IS_weights,
            }
        )
        self._history_loss.append(loss)
        log_msg += " | loss: %.6f | avg_td_err: %.6f" % (loss, np.mean(abs_errs))

        # Update sum tree
        self._mem.update(tree_indices, abs_errs)

        # Replace target
        if self._learn_step == 1 or self._learn_step % self._FREQ_REPLACE == 0:
            self._sess.run(self._replace_target)
            log_msg += " | target net replaced"

        if saved or self._learn_step == 1 or self._learn_step % self._FREQ_LOG == 0:
            log(log_msg)

        self._learn_step += 1
        self._epsilon = max(self._EPSILON_MIN, self._epsilon - self._EPSILON_DEC)
        self._beta = min(1.0, self._beta + self._BETA_INC)
