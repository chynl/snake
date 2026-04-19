"""
Train the reinforcement learning agent.

Current model path: ./rl_model.pt
Current model size: 645,347 parameters (2.5 MB)

Current model was trained with NVIDIA GeForce RTX 5070 Ti Laptop GPU.

Training history:
-------------------------------------------------------------------------------------------------
Episode:    200 | Average rewards and scores:  -99.16 /  3.09 | Elapsed:    0 mins | Device: cuda
Episode:    400 | Average rewards and scores:  -98.87 /  3.12 | Elapsed:    0 mins | Device: cuda
Episode:    600 | Average rewards and scores:  -98.61 /  3.15 | Elapsed:    0 mins | Device: cuda
Episode:    800 | Average rewards and scores:  -98.61 /  3.15 | Elapsed:    0 mins | Device: cuda
Episode:   1000 | Average rewards and scores:  -98.71 /  3.13 | Elapsed:    0 mins | Device: cuda
...
Episode:  50000 | Average rewards and scores:   44.97 / 17.56 | Elapsed:   67 mins | Device: cuda
Episode:  50200 | Average rewards and scores:   52.84 / 18.36 | Elapsed:   69 mins | Device: cuda
Episode:  50400 | Average rewards and scores:   48.45 / 17.91 | Elapsed:   70 mins | Device: cuda
Episode:  50600 | Average rewards and scores:   50.46 / 18.11 | Elapsed:   72 mins | Device: cuda
Episode:  50800 | Average rewards and scores:   50.92 / 18.16 | Elapsed:   73 mins | Device: cuda
Episode:  51000 | Average rewards and scores:   43.76 / 17.44 | Elapsed:   75 mins | Device: cuda
...
Episode:  98000 | Average rewards and scores:  161.12 / 24.36 | Elapsed:  407 mins | Device: cuda
Episode:  98200 | Average rewards and scores:  148.50 / 23.09 | Elapsed:  408 mins | Device: cuda
Episode:  98400 | Average rewards and scores:  166.14 / 24.19 | Elapsed:  410 mins | Device: cuda
Episode:  98600 | Average rewards and scores:  160.11 / 23.77 | Elapsed:  411 mins | Device: cuda
Episode:  98800 | Average rewards and scores:  148.63 / 23.10 | Elapsed:  413 mins | Device: cuda
Episode:  99000 | Average rewards and scores:  161.09 / 24.35 | Elapsed:  414 mins | Device: cuda
Episode:  99200 | Average rewards and scores:  139.59 / 22.95 | Elapsed:  416 mins | Device: cuda
Episode:  99400 | Average rewards and scores:  132.68 / 22.26 | Elapsed:  417 mins | Device: cuda
Episode:  99600 | Average rewards and scores:  156.96 / 23.84 | Elapsed:  419 mins | Device: cuda
Episode:  99800 | Average rewards and scores:  134.21 / 22.51 | Elapsed:  420 mins | Device: cuda
Episode: 100000 | Average rewards and scores:  140.22 / 22.93 | Elapsed:  422 mins | Device: cuda
-------------------------------------------------------------------------------------------------
"""

from src.agents.rl import RLAgent


def main() -> None:
    agent = RLAgent()
    agent.train()


if __name__ == "__main__":
    main()
