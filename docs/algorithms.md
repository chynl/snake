# Algorithms

<!-- TOC -->

- [Overview](#overview)
- [Solvers](#solvers)
    - [Path Solver](#path-solver)
        - [Shortest Path](#shortest-path)
        - [Longest Path](#longest-path)
    - [Greedy Solver](#greedy-solver)
    - [Hamilton Solver](#hamilton-solver)
        - [Build a Hamiltonian Cycle](#build-a-hamiltonian-cycle)
        - [Take Shortcuts](#take-shortcuts)
- [References](#references)

<!-- /TOC -->

<a id="markdown-overview" name="overview"></a>
## Overview

The [Snake][snake-wiki] game was popularized by its appearance on Nokia cell phones in 1997 but has been recreated in several forms for multiple computing platforms since 1978. The game is very simple: the snake is controlled by the player and is allowed to move inside a 2-dimensional playing field surrounded by walls. At each discrete interval, called a time step or step, the snake must move forward, turn left, or turn right as the game requires that the snake cannot stop moving. The game will randomly generate and place one piece of food in the game field at a time. When the snake moves onto a piece of food, the food is eaten and the snake's length grows by one. The goal is to eat as many pieces of food without ending the game by colliding the snake into itself or the walls. [1]

In our game settings, the playing field will be 10 units tall and 10 units wide consisting of 100 available spaces. The snake will initially begin in the top-left corner, facing right, with an initial length of 2 units. Therefore, the snake can eat 98 pieces of food before filling up the entire playing field.

<a id="markdown-solvers" name="solvers"></a>
## Solvers

All the problem solvers are subclasses of [BaseSolver][basesolver-src]. The subclasses override `BaseSolver.next_direc()` to return the next moving direction of the snake.

<a id="markdown-path-solver" name="path-solver"></a>
### Path Solver

[Path Solver][pathsolver-src] provides methods to find the shortest path and the longest path between the snake's head to other points on the game map. This solver does not directly decide the next moving direction of the snake, but help other solvers to decide it.

<a id="markdown-shortest-path" name="shortest-path"></a>
#### Shortest Path

Path Solver uses breadth-first search to find the shortest path. Intuitively, we expect the path to be as straight as possible so there will be less scattered empty points on the map. In the implementation, the trick is that during each iteration, the adjacent point in the last traverse direction will be traversed first.

<a id="markdown-longest-path" name="longest-path"></a>
#### Longest Path

The [longest path problem][longest-path-wiki] in the game map (i.e., a cyclic, undirected and unweighted graph) is NP-hard. Path Solver uses a heuristic algorithm to find suboptimal solutions.

Suppose we want to find the longest path from point A to point B on a 4*4 game map. The algorithm first finds the shortest path between the two points and then extends each pair of points on the path until no extensions can be found:

![][build-longest-img]

<a id="markdown-greedy-solver" name="greedy-solver"></a>
### Greedy Solver

[Greedy Solver][greedysolver-src] lets the snake eat the food along the shortest path if it thinks it is safe. Otherwise, it makes the snake wander around until a safe path can be found. The solver depends on [Path Solver](#path-solver) to find the shortest path and the longest path on the game map.

Concretely, to find the snake **S1**'s next moving direction **D**, the solver follows the steps below:

1. Compute the shortest path **P1** from **S1**'s head to the food. If **P1** exists, go to step 2. Otherwise, go to step 4.
2. Move a virtual snake **S2** (the same as **S1**) to eat the food along path **P1**.
3. Compute the longest path **P2** from **S2**'s head to its tail. If **P2** exists, let **D** be the first direction in path **P1**. Otherwise, go to step 4.
4. Compute the longest path **P3** from **S1**'s head to its tail. If **P3** exists, let **D** be the first direction in path **P3**. Otherwise, go to step 5.
5. Let **D** be the direction that makes **S1** the farthest from the food.

<a id="markdown-hamilton-solver" name="hamilton-solver"></a>
### Hamilton Solver

[Hamilton Solver][hamiltonsolver-src] builds a hamiltonian cycle on the game map first and then directs the snake to eat the food along the cycle path. To reduce the average steps the snake takes to success, the solver enables the snake to take shortcuts if possible. The solver depends on [Path Solver](#path-solver) to find the longest path on the game map.

<a id="markdown-build-a-hamiltonian-cycle" name="build-a-hamiltonian-cycle"></a>
#### Build a Hamiltonian Cycle

Before the snake starts moving, Hamilton Solver finds the [longest path](#longest-path) from the snake's head to its tail, which forms a hamiltonian cycle on the map:

![][build-hamilton-img]

<a id="markdown-take-shortcuts" name="take-shortcuts"></a>
#### Take Shortcuts

Following a fixed cycle path all the time is tedious. Hamilton Solver directs the snake to take shortcuts according to the rules below. [2]

![][take-shortcuts-img]

<a id="markdown-references" name="references"></a>
## References

1. Lockhart, C., Application of temporal difference learning to the game of Snake. *Electronic Theses and Dissertations* 848 (2010). [[Link]][link-ref-1]
2. Tapsell, J., Nokia 6110 Part 3 – Algorithms. (2015). [[Link]][link-ref-2]

[snake-wiki]: https://en.wikipedia.org/wiki/Snake_(video_game)
[longest-path-wiki]: https://en.wikipedia.org/wiki/Longest_path_problem

[basesolver-src]: ../snake/solver/base.py
[pathsolver-src]: ../snake/solver/path.py
[greedysolver-src]: ../snake/solver/greedy.py
[hamiltonsolver-src]: ../snake/solver/hamilton.py

[build-longest-img]: ./images/build_longest.png
[build-hamilton-img]: ./images/build_hamilton.png
[take-shortcuts-img]: ./images/take_shortcuts.png

[link-ref-1]: https://doi.org/10.18297/etd/848
[link-ref-2]: https://johnflux.com/2015/05/02/nokia-6110-part-3-algorithms/
