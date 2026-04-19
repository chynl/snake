import argparse

from src.bench import run_bench
from src.game import Game
from src.mode import Mode


def main() -> None:
    args = parse_args()
    mode = Mode[args.mode.upper()]

    if args.bench_rounds is None:
        game = Game(mode, args.move_freq, args.show_grid, args.record_frames, args.seed)
        game.loop()
    else:
        run_bench(mode, args.bench_rounds, args.seed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        choices=["human", "graph", "rl"],
        default="graph",
        help="set game mode (default: graph)",
        type=str,
        dest="mode",
    )

    parser.add_argument(
        "-f",
        metavar="<freq>",
        default=80,
        help="set snake move frequency in milliseconds (default: 80)",
        type=int,
        dest="move_freq",
    )

    parser.add_argument(
        "-g",
        help="show grid lines",
        action="store_true",
        dest="show_grid",
    )

    parser.add_argument(
        "-r",
        help="record game play",
        action="store_true",
        dest="record_frames",
    )

    parser.add_argument(
        "-s",
        metavar="<seed>",
        default=None,
        help="set random seed for food generation",
        type=int,
        dest="seed",
    )

    parser.add_argument(
        "-b",
        metavar="<rounds>",
        default=None,
        help="run benchmark for the given number of rounds",
        type=int,
        dest="bench_rounds",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
