:uk: English / [:cn: 中文](./README-CN.md)

# Snake

[![Build Status](https://travis-ci.org/stevennL/Snake.svg?branch=master)](https://travis-ci.org/stevennL/Snake) [![Build status](https://ci.appveyor.com/api/projects/status/bryir507227d0i1q?svg=true)](https://ci.appveyor.com/project/stevennL/snake)

AI version of the snake game.

The AI's goal is to direct the snake to eat the food and fill the map with its body **as quickly as possible**, so it **should not** just follow a fixed zigzag pattern.

## Demo

![Image of Snake AI](img/AI.gif)

## Installation

1. Install [CMake](https://cmake.org/).

2. Build this project using the commands below:

    ```bash
    $ mkdir build
    $ cd build
    $ cmake ..
    ```

3. The `build` directory has:

    * A Makefile for Linux
    * A Visual Studio project for Windows
    * An Xcode project for OS X

## Keyboard Controls

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

    1. Compute the shortest path ***P1*** from snake ***S1***'s head to the food.

    2. Direct a virtual snake, ***S2*** (the same as ***S1***), to eat the food along path ***P1***.

    3. Compute the longest path ***P2*** from snake ***S2***'s head to its tail. If ***P2*** exists, let ***D*** be the first direction in path ***P1***. Otherwise go to step 4.

    4. Compute the longest path ***P3*** from snake ***S1***'s head to its tail. If ***P3*** exists, let ***D*** be the first direction in path ***P3***. Otherwise go to step 5.

    5. Let ***D*** be the direction that moves the snake along the longest path to the food.

* [Map.findMinPath()](./src/Map.cpp): compute the shortest path between two positions

    The algorithm is based on BFS. In order to make the result path as straight as possible, each time the adjacent positions are traversed, the position at the current searching direction will be traversed first.

    Here is a vivid description of how it works:

    ![](img/shortest_path.gif)

    (The green area is scanned when searching and the red area is the **shortest** path. Each number on the point denotes its **minimum** distance to the starting point.)
  
* [Map.findMaxPath()](./src/Map.cpp): compute the longest path between two positions

    The algorithm is based on DFS and the greedy algorithm. Each time the adjacent positions are traversed, the position that is the farthest from the destination (estimated by the Manhatten distance) will be traversed first. In addition, in order to make the result path as straight as possible, if two positions have the same distance to the destination, the position at the current searching direction will be traversed first. Since this is an NP-hard problem, this method is only approximate.

    Here is a vivid description of how it works:
    
    ![](img/longest_path.gif)

    (The green area is scanned when searching and the red area is the **longest** path. Each number on the point denotes its **estimated** distance to the destination.)

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
