# Snake

[![][travis-badge]][travis-build] [![][appveyor-badge]][appveyor-build] ![][python-badge]

This project focuses on the artificial intelligence of the [Snake][snake-wiki] game. The snake's goal is to eat the food continuously and fill the map with its bodies ASAP. The [old version][snake-proj-old] of this project is written in C++. Now it has been rewritten using Python for a user-friendly GUI and the simplicity in the implementations of algorithms.

***[Algorithm Details >][algorithms-doc]***

## Experiments

We use three metrics to evaluate the performance of an AI:

1. **Success Rate:** Rate of success (i.e., the map is filled with the snake's bodies) after playing the game for N times.
2. **Average Steps:** Average steps the snake has moved to success.
3. **Average Length:** Average length the snake has grown to (max: 100).

Test results (N=1000):

| Solver | Demo | Success Rate | Average Steps | Average Length |
| :----: | :--: | :----------: | :-----------: | :------------: |
|[Hamilton][hamilton-doc]|![][demo-hamilton]|99.70%|1778.39|99.78|
|[Greedy][greedy-doc]|![][demo-greedy]|22.90%|1566.29|94.29|

## Installation

Requirements: Python 3.5+ (64-bit) with [Tkinter][tkinter-doc] installed.

```
$ pip3 install -r requirements.txt
$ python3 run.py
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

[demo-hamilton]: ./docs/images/solver_hamilton.gif
[demo-greedy]: ./docs/images/solver_greedy.gif
