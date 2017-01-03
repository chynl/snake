:uk: English / [:cn: 中文](./README-CN.md)

# Snake

[![Build Status](https://travis-ci.org/stevennL/Snake.svg?branch=master)](https://travis-ci.org/stevennL/Snake)

AI of snake game.

The goal is to eat all the food and make the map filled with the snake's bodies. 

## Demo

![Image of Snake AI](img/AI.gif)

## Installation

1. Install [CMake](https://cmake.org/).

2. Build this project using below commands:

    ```bash
    $ mkdir build
    $ cd build
    $ cmake ..
    ```

3. In directory `build`, you could find:

    * A Makefile for Linux
    * A Visual Studio project for Windows
    * An Xcode project for OS X

## Keyboard Control

| Key | Feature |
|:---:|:-------:|
|W|move up|
|A|move left|
|S|move down|
|D|move right|
|Space|pause/resume the snake|
|Esc|exit game|

## AI Strategy

* [Snake.decideNext()](./src/Snake.cpp): compute the next move direction ***D*** of the snake ***S1***

    1. Compute the shortest path ***P1*** from the snake ***S1***'s head to food.

    2. Move a virtual snake ***S2***(the same as ***S1***) to eat the food along path ***P1***.

    3. Compute the longest path ***P2*** from the snake ***S2***'s head to its tail. If ***P2*** exists, let ***D*** be the first direction in path ***P1***. Otherwise go to step 4.

    4. Compute the longest path ***P3*** from the snake ***S1***'s head to its tail. If ***P3*** exists, let ***D*** be the first direction in path ***P3***. Otherwise go to step 5.

    5. Let ***D*** be the direction that makes the snake the farthest from food.

* [Map.findMinPath()](./src/Map.cpp): compute the shortest path between two positions

    The algorithm is based on BFS. In order to make the result path as straight as possible, each time when traversing the adjacent positions, the position at current searching direction will be traversed first.

    Here is a vivid description of how it works:

    ![](img/shortest_path.gif)

    (The green area is scanned when searching and the red area is the **shortest** path. Each number on the point denotes its **minimum** distance to the start point.)
  
* [Map.findMaxPath()](./src/Map.cpp): compute the longest path between two positions

    The algorithm is based on DFS and the greedy algorithm. Each time when traversing the adjacent positions, the position that is the farthest(estimated by Manhatten distance) from the destination will be traversed first. In addition, in order to make the result path as straight as possible, if two positions have the same distance to the destination, the position at current searching direction will be traversed first. Since this is an NP-hard problem, this method is only approximate.

    Here is a vivid description of how it works:
    
    ![](img/longest_path.gif)

    (The green area is scanned when searching and the red area is the **longest** path. Each number on the point denotes its **estimated** distance to the destination.)

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
