# Snake



***[Algorithms >][doc-algorithms]***


Test results (averaged over 1000 episodes):

| Solver | Demo (optimal) | Average Length | Average Steps |
| :----: | :------------: | :------------: | :-----------: |
|[Hamilton][doc-hamilton]|![][demo-hamilton]|63.93|717.83|
|[Greedy][doc-greedy]|![][demo-greedy]|60.15|904.56|
|[DQN][doc-dqn]<br>(experimental)|![][demo-dqn]|24.44|131.69|

## Installation

Requirements: Python 3.6+ with [Tkinter][doc-tkinter] installed.

```
pip install -r requirements.txt
python run.py [-h]
```

Run unit tests:

```
python -m pytest
```

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.


[snake-wiki]: https://en.wikipedia.org/wiki/Snake_(video_game)
[snake-cpp]: https://github.com/chuyangliu/snake/tree/7227f5e0f3185b07e9e3de1ac5c19a17b9de3e3c

[doc-tkinter]: https://docs.python.org/3/library/tkinter.html
[doc-algorithms]: ./docs/algorithms.md
[doc-greedy]: ./docs/algorithms.md#greedy-solver
[doc-hamilton]: ./docs/algorithms.md#hamilton-solver
[doc-dqn]: ./docs/algorithms.md#dqn-solver

[demo-hamilton]: ./docs/images/solver_hamilton.gif
[demo-greedy]: ./docs/images/solver_greedy.gif
[demo-dqn]: ./docs/images/solver_dqn.gif
