import os
import random
import time
from collections import deque
from datetime import datetime, timezone
from typing import Iterable, Sequence

import numpy as np
import torch

from src.agents.base import Agent
from src.cell import CellValue
from src.cfg import Config
from src.direc import Direction
from src.snake import Snake


class RLParams:
    MODEL_PATH: str = os.path.join(".", "rl_model.pt")

    DEVICE_NAME: str = "cuda" if torch.cuda.is_available() else "cpu"
    DEVICE: torch.device = torch.device(DEVICE_NAME)

    NUM_GRID_CHANNELS: int = 4
    NUM_1D_FEATURES: int = 4 + 4 + 1
    NUM_ACTIONS: int = 3

    NUM_EPISODES: int = 100_000
    NUM_EPISODES_FOR_AVG: int = 200

    EPSILON_INIT: float = 1.0
    EPSILON_MIN: float = 0.01
    EPSILON_DECAY_EPISODES: int = 50_000

    NUM_STEPS_PER_EPISODE: int = 500
    NUM_STEPS_PER_LEARNING: int = 4

    MAX_STEPS_WITHOUT_FOOD_BEFORE_STOP: int = Config.GRID_SIZE**2

    MAX_MEM_SIZE: int = 100_000
    BATCH_SIZE: int = 64

    LEARNING_RATE: float = 0.001
    UPDATE_RATE: float = 0.005
    DISCOUNT: float = 0.99

    MAX_GRAD_NORM: float = 10.0


class RLNet(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()

        self.conv: torch.nn.Sequential = torch.nn.Sequential(
            torch.nn.Conv2d(RLParams.NUM_GRID_CHANNELS, 32, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv2d(32, 64, kernel_size=3, padding=1),
            torch.nn.ReLU(),
        )

        conv_out_size = 64 * Config.GRID_SIZE * Config.GRID_SIZE

        self.mlp: torch.nn.Sequential = torch.nn.Sequential(
            torch.nn.Linear(conv_out_size + RLParams.NUM_1D_FEATURES, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, RLParams.NUM_ACTIONS),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        grid_len = RLParams.NUM_GRID_CHANNELS * Config.GRID_SIZE * Config.GRID_SIZE

        if x.dim() == 1:  # single state for inference
            x = x.unsqueeze(0)
            squeeze = True
        else:  # batch of states for learning
            squeeze = False

        grid_flat = x[:, :grid_len]
        extra = x[:, grid_len:]

        grid_2d = grid_flat.view(
            -1,
            RLParams.NUM_GRID_CHANNELS,
            Config.GRID_SIZE,
            Config.GRID_SIZE,
        )

        conv_out: torch.Tensor = self.conv(grid_2d)
        conv_out_flat = conv_out.view(grid_2d.size(0), -1)

        combined = torch.cat((conv_out_flat, extra), dim=1)
        q_vals: torch.Tensor = self.mlp(combined)

        if squeeze:
            q_vals = q_vals.squeeze(0)

        return q_vals


class RLExperience:
    def __init__(
        self,
        state: torch.Tensor,
        action: torch.types.Number,
        reward: float,
        next_state: torch.Tensor,
        done_val: bool,
    ) -> None:
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done_val = done_val

    @staticmethod
    def tensorize(
        experiences: Iterable["RLExperience"],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:

        states = torch.stack([e.state for e in experiences]).to(RLParams.DEVICE)

        actions = torch.tensor([e.action for e in experiences]).to(RLParams.DEVICE)

        rewards = torch.tensor([e.reward for e in experiences]).to(RLParams.DEVICE)

        next_states = torch.stack([e.next_state for e in experiences]).to(
            RLParams.DEVICE
        )

        done_vals = torch.tensor(
            [e.done_val for e in experiences],
            dtype=torch.float,
        ).to(RLParams.DEVICE)

        return states, actions, rewards, next_states, done_vals


class RLAgent(Agent):
    def __init__(self):
        self.rand: random.Random = random.Random()
        self.eval_net: RLNet | None = None

        self.steps_without_food: int
        self.prev_len: int

    def next_direc(self, snake: Snake) -> Direction:
        if self.eval_net is None:
            self.eval_net = self.new_eval_net()
        state = self.state(snake)
        with torch.no_grad():
            q_vals = self.eval_net(state.to(RLParams.DEVICE))
        action = self.action(q_vals)
        return self.action_to_direc(action, snake)

    def train(self) -> None:
        q_net = self.new_train_net()
        q_net_target = self.new_train_net(q_net)
        optimizer = torch.optim.Adam(q_net.parameters(), lr=RLParams.LEARNING_RATE)

        mem: deque[RLExperience] = deque(maxlen=RLParams.MAX_MEM_SIZE)
        epsilon = RLParams.EPSILON_INIT

        tot_rewards_history: list[float] = []
        tot_scores_history: list[int] = []
        start_time = time.monotonic()

        self.print_model_info(q_net)
        self.print_delim()

        for episode in range(RLParams.NUM_EPISODES):
            snake = self.new_snake()
            state = self.state(snake)
            tot_rewards = 0.0

            self.steps_without_food = 0
            self.prev_len = snake.len()

            for step in range(RLParams.NUM_STEPS_PER_EPISODE):
                q_vals = q_net(state.to(RLParams.DEVICE))
                action = self.action(q_vals, epsilon)
                next_state, reward, done = self.move(snake, action)
                mem.append(RLExperience(state, action, reward, next_state, done))
                state = next_state
                tot_rewards += reward

                if self.should_learn(step, mem):
                    experiences = self.rand.sample(mem, RLParams.BATCH_SIZE)
                    self.learn(experiences, q_net, q_net_target, optimizer)

                if done:
                    break

            epsilon = self.next_epsilon(episode)

            tot_rewards_history.append(tot_rewards)
            tot_scores_history.append(snake.len())
            elapsed = time.monotonic() - start_time

            self.print_summary(
                episode,
                tot_rewards_history,
                tot_scores_history,
                elapsed,
            )

        self.print_delim()
        self.save(q_net)

    def new_eval_net(self) -> RLNet:
        if not os.path.isfile(RLParams.MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {RLParams.MODEL_PATH}")
        net = self.new_train_net()
        net.load_state_dict(
            torch.load(
                RLParams.MODEL_PATH,
                weights_only=True,
                map_location=RLParams.DEVICE,
            )
        )
        net.eval()
        return net

    def new_train_net(self, src: RLNet | None = None) -> RLNet:
        net = RLNet()
        if src is not None:
            net.load_state_dict(src.state_dict())
        return net.to(RLParams.DEVICE)

    def new_snake(self) -> Snake:
        return Snake(
            Config.GRID_SIZE,
            Config.INIT_SNAKE_POS,
            Config.INIT_SNAKE_CELLS,
            Config.INIT_SNAKE_DIREC,
            Config.INIT_SNAKE_FOOD,
        )

    def state(self, snake: Snake) -> torch.Tensor:
        food_ch = torch.zeros(Config.GRID_SIZE, Config.GRID_SIZE)
        body_ch = torch.zeros(Config.GRID_SIZE, Config.GRID_SIZE)
        head_ch = torch.zeros(Config.GRID_SIZE, Config.GRID_SIZE)
        danger_ch = torch.zeros(Config.GRID_SIZE, Config.GRID_SIZE)

        snake_len = snake.len()

        for row in range(Config.GRID_SIZE):
            for col in range(Config.GRID_SIZE):
                val = snake.grid[row][col]
                if val == CellValue.FOOD.value:
                    food_ch[row][col] = 1.0
                elif val > 0:
                    body_ch[row][col] = val / snake_len  # normalize by length
                    if val == 1:
                        head_ch[row][col] = 1.0
                    if val != snake_len:
                        danger_ch[row][col] = 1.0

        grid_channels = torch.stack((food_ch, body_ch, head_ch, danger_ch))

        snake_direc_vec = torch.zeros(4)
        snake_direc_vec[snake.direc.index()] = 1.0

        food_direc_vec = torch.zeros(4)
        food_dist_vec = torch.zeros(1)
        if snake.food is not None:
            head = snake.head()
            dr = snake.food.row - head.row
            dc = snake.food.col - head.col
            if dr < 0:
                food_direc_vec[0] = 1.0  # food is up
            if dc < 0:
                food_direc_vec[1] = 1.0  # food is left
            if dr > 0:
                food_direc_vec[2] = 1.0  # food is down
            if dc > 0:
                food_direc_vec[3] = 1.0  # food is right
            # Manhattan distance normalized by max distance
            food_dist_vec[0] = (abs(dr) + abs(dc)) / (2 * snake.grid_size)

        extra = torch.cat((snake_direc_vec, food_direc_vec, food_dist_vec))
        return torch.cat((grid_channels.flatten(), extra))

    def action(
        self,
        q_vals: torch.Tensor,
        epsilon: float | None = None,
    ) -> torch.types.Number:
        if epsilon is not None and torch.rand(1).item() < epsilon:
            return torch.randint(0, q_vals.shape[-1], (1,)).item()
        return q_vals.argmax().item()

    def move(
        self,
        snake: Snake,
        action: torch.types.Number,
    ) -> tuple[torch.Tensor, float, bool]:
        snake.move(self.action_to_direc(action, snake))
        next_state = self.state(snake)
        done = snake.is_stopped()

        reward = -0.01
        if snake.state == Snake.State.DEAD:
            reward = -100.0
        elif snake.state == Snake.State.FULL:
            reward = 100.0
        elif snake.len() > self.prev_len:
            reward = 10.0
            self.prev_len = snake.len()
            self.steps_without_food = 0
        else:
            self.steps_without_food += 1

        if self.steps_without_food >= self.timeout_steps(snake):
            reward = -100.0
            done = True

        return next_state, reward, done

    def action_to_direc(self, action: torch.types.Number, snake: Snake) -> Direction:
        if action == 0:
            return snake.direc  # go straight
        if action == 1:
            return snake.direc.left()  # turn left
        if action == 2:
            return snake.direc.right()  # turn right
        assert False, f"Unexpected action {action}"

    def timeout_steps(self, snake: Snake) -> int:
        return RLParams.MAX_STEPS_WITHOUT_FOOD_BEFORE_STOP + snake.len()

    def should_learn(self, step: int, mem: Sequence[RLExperience]) -> bool:
        # fmt: off
        return (
            (step + 1) % RLParams.NUM_STEPS_PER_LEARNING == 0
            and len(mem) >= RLParams.BATCH_SIZE
        )
        # fmt: on

    def next_epsilon(self, episode: int) -> float:
        linear_decay = (
            episode
            * (RLParams.EPSILON_INIT - RLParams.EPSILON_MIN)
            / RLParams.EPSILON_DECAY_EPISODES
        )
        return max(
            RLParams.EPSILON_MIN,
            RLParams.EPSILON_INIT - linear_decay,
        )

    def learn(
        self,
        experiences: Iterable[RLExperience],
        q_net: RLNet,
        q_net_target: RLNet,
        optimizer: torch.optim.Optimizer,
    ) -> None:
        loss = self.loss(experiences, q_net, q_net_target)
        optimizer.zero_grad()
        loss.backward()  # type: ignore[reportUnknownMemberType]
        torch.nn.utils.clip_grad_norm_(
            q_net.parameters(),
            max_norm=RLParams.MAX_GRAD_NORM,
        )
        optimizer.step()
        self.soft_update(q_net, q_net_target)

    def loss(
        self,
        experiences: Iterable[RLExperience],
        q_net: RLNet,
        q_net_target: RLNet,
    ) -> torch.Tensor:

        experiences_tensor = RLExperience.tensorize(experiences)
        states, actions, rewards, next_states, done_vals = experiences_tensor

        with torch.no_grad():
            # Double DQN
            q_vals_next: torch.Tensor = q_net(next_states)
            best_actions_next = q_vals_next.argmax(-1, True)
            q_target_vals: torch.Tensor = q_net_target(next_states)
            q_target_vals_max = q_target_vals.gather(1, best_actions_next).squeeze(1)

        y_targets = rewards + (RLParams.DISCOUNT * q_target_vals_max * (1 - done_vals))

        q_vals: torch.Tensor = q_net(states)
        q_vals = q_vals.gather(1, actions.long().unsqueeze(1)).squeeze(1)

        return torch.nn.functional.smooth_l1_loss(q_vals, y_targets)

    def soft_update(self, q_net: RLNet, q_net_target: RLNet) -> None:
        for q_net_params, target_params in zip(
            q_net.parameters(),
            q_net_target.parameters(),
        ):
            target_params.data.copy_(
                RLParams.UPDATE_RATE * q_net_params.data
                + (1.0 - RLParams.UPDATE_RATE) * target_params.data
            )

    def save(self, net: RLNet) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        path = RLParams.MODEL_PATH + f".tmp.{ts}"
        torch.save(net.state_dict(), path)
        print(f"Model saved to {path}")

    def print_model_info(self, net: RLNet) -> None:
        num_params = 0
        num_bytes = 0
        for p in net.parameters():
            num_params += p.numel()
            num_bytes += p.numel() * p.element_size()
        num_mbs = num_bytes / (1024 * 1024)
        print(f"Model has {num_params:,} parameters ({num_mbs:.1f} MB)")

    def print_summary(
        self,
        episode: int,
        tot_rewards_history: Sequence[float],
        tot_scores_history: Sequence[int],
        elapsed_secs: float,
    ) -> None:
        avg_rewards = np.mean(tot_rewards_history[-RLParams.NUM_EPISODES_FOR_AVG :])
        avg_scores = np.mean(tot_scores_history[-RLParams.NUM_EPISODES_FOR_AVG :])
        elapsed_mins = int(elapsed_secs / 60)

        print(
            "\r"
            + " | ".join(
                [
                    f"Episode: {episode + 1:>6}",
                    f"Average rewards and scores: {avg_rewards:>7.2f} / {avg_scores:>5.2f}",
                    f"Elapsed: {elapsed_mins:>4} mins",
                    f"Device: {RLParams.DEVICE_NAME:>4}",
                ]
            ),
            end="",
        )

        if (episode + 1) % RLParams.NUM_EPISODES_FOR_AVG == 0:
            print("")

    def print_delim(self) -> None:
        print("-" * 97)
