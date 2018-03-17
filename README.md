# Snake

[![][travis-badge]][travis-build] [![][appveyor-badge]][appveyor-build] ![][python-badge]

This project focuses on the artificial intelligence of the [Snake][snake-wiki] game. The snake's goal is to eat the food continuously and fill the map with its bodies ASAP. The [old version][snake-proj-old] of this project is written in C++. Now it has been rewritten using Python for a user-friendly GUI and the simplicity in the implementations of algorithms.

***[Algorithm Details >][algorithms-doc]***

## Experiments

We use two metrics to evaluate the performance of an AI:

1. **Average Length:** Average length the snake has grown to (*max:* 64).
2. **Average Steps:** Average steps the snake has moved.

Test results (averaged over 1000 episodes):

| Solver | Demo | Average Length | Average Steps |
| :----: | :--: | :------------: | :-----------: |
|[Hamilton][hamilton-doc]|![][demo-hamilton]|63.93|717.83|
|[Greedy][greedy-doc]|![][demo-greedy]|60.15|904.56|
|[DQN][dqn-doc]|![][demo-dqn]|22.59|119.93|

## Installation

Requirements: Python 3.5+ (64-bit) with [Tkinter][tkinter-doc] installed.

```
$ pip3 install -r requirements.txt

# Use -h for more details
$ python3 run.py [-h]
```

Run unit tests:

```
$ python3 -m pytest -v
```

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.


[snake-proj-old]: https://github.com/chuyangliu/Snake/tree/7227f5e0f3185b07e9e3de1ac5c19a17b9de3e3c

[travis-build]: https://travis-ci.org/chuyangliu/Snake
[travis-badge]: https://travis-ci.org/chuyangliu/Snake.svg?branch=dev_refactor
[appveyor-build]: https://ci.appveyor.com/project/chuyangliu/snake/branch/master
[appveyor-badge]: https://ci.appveyor.com/api/projects/status/d4agff8ef7d9tfxh/branch/master?svg=true
[python-badge]: https://img.shields.io/badge/python-3.5%2C%203.6-blue.svg

[snake-wiki]: https://en.wikipedia.org/wiki/Snake_(video_game)
[tkinter-doc]: https://docs.python.org/3.6/library/tkinter.html
[algorithms-doc]: ./docs/algorithms.md
[greedy-doc]: ./docs/algorithms.md#greedy-solver
[hamilton-doc]: ./docs/algorithms.md#hamilton-solver
[dqn-doc]: ./docs/algorithms.md#dqn-solver

[demo-hamilton]: ./docs/images/solver_hamilton.gif
[demo-greedy]: ./docs/images/solver_greedy.gif
[demo-dqn]: ./docs/images/solver_dqn.gif
