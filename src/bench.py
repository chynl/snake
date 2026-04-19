import time

from src.agents import init_agent
from src.cfg import Config
from src.mode import Mode
from src.snake import Snake


def run_bench(
    mode: Mode,
    num_rounds: int,
    rand_seed: int | None = None,
    max_steps: int = 1000,
) -> None:
    if mode == Mode.HUMAN:
        print(f"Benchmark is not supported for {mode.name} mode")
        return
    if num_rounds <= 0:
        print("Number of benchmark rounds must be positive")
        return

    agent = init_agent(mode)
    assert agent is not None

    history_seeds: list[int] = []
    history_elapsed: list[float] = []
    history_steps: list[int] = []
    history_score: list[int] = []
    num_suc = 0

    for i in range(num_rounds):
        snake = Snake(
            Config.GRID_SIZE,
            Config.INIT_SNAKE_POS,
            Config.INIT_SNAKE_CELLS,
            Config.INIT_SNAKE_DIREC,
            Config.INIT_SNAKE_FOOD,
            rand_seed,
        )

        start_time = time.monotonic()
        steps = 0
        while not snake.is_stopped() and steps < max_steps:
            snake.move(agent.next_direc(snake))
            steps += 1
        elapsed = (time.monotonic() - start_time) * 1000

        print_round_stats(mode, i + 1, elapsed, steps, snake)

        history_seeds.append(snake.rand_seed)
        history_elapsed.append(elapsed)
        history_steps.append(steps)
        history_score.append(snake.len())

        if snake.state == Snake.State.FULL:
            num_suc += 1

    print_summary(
        num_rounds,
        history_seeds,
        history_elapsed,
        history_steps,
        history_score,
        num_suc,
    )


def print_round_stats(
    mode: Mode,
    round: int,
    elapsed: float,
    steps: int,
    snake: Snake,
) -> None:
    print(
        " | ".join(
            [
                f"Mode: {mode.name:>5}",
                f"Round: {round:>4}",
                f"Time: {int(elapsed):>5} ms",
                f"Steps: {steps:>4}",
                f"Score: {snake.len():>5}",
                f"Seed: {snake.rand_seed}",
            ]
        )
    )


def print_summary(
    num_rounds: int,
    history_seeds: list[int],
    history_elapsed: list[float],
    history_steps: list[int],
    history_score: list[int],
    num_suc: int,
) -> None:
    min_time = min(history_elapsed)
    min_steps = min(history_steps)
    min_score_idx, min_score = min(enumerate(history_score), key=lambda x: x[1])

    max_time = max(history_elapsed)
    max_steps = max(history_steps)
    max_score_idx, max_score = max(enumerate(history_score), key=lambda x: x[1])

    avg_time = sum(history_elapsed) / num_rounds
    avg_steps = sum(history_steps) / num_rounds
    avg_score = sum(history_score) / num_rounds

    suc_rate = num_suc / num_rounds * 100

    print("-" * 88)

    print(" " * 18, end="")
    print_summary_stats(
        "    Min", min_time, min_steps, min_score, history_seeds[min_score_idx]
    )

    print(" " * 18, end="")
    print_summary_stats(
        "    Max", max_time, max_steps, max_score, history_seeds[max_score_idx]
    )

    print(" " * 18, end="")
    print_summary_stats("Average", avg_time, avg_steps, avg_score)

    print("-" * 88)
    print(" " * 13, end="")
    print(f"Success Rate : {suc_rate:>4.2f}%")


def print_summary_stats(
    type: str,
    time: float,
    steps: float,
    score: float,
    seed: int | None = None,
) -> None:
    print(f"{type} | ", end="")
    print(
        " | ".join(
            [
                f"Time: {int(time):>5} ms",
                f"Steps: {int(steps):>4}",
                f"Score: {score:>5.2f}",
            ]
        ),
        end="",
    )
    if seed is None:
        print(" |")
    else:
        print(f" | Seed: {seed}")
