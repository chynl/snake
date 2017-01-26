:uk: English / [:cn: 中文](./README-CN.md)

# Snake

AI version of the snake game.

The AI's goal is to direct the snake to eat the food and fill the map with its body **as quickly as possible**, so it **should not** just follow a fixed zigzag pattern.

## Build Status

| Linux | Windows |
|:-----:|:-------:|
|[![Build Status](https://travis-ci.org/stevennL/Snake.svg?branch=master)](https://travis-ci.org/stevennL/Snake)|[![Build Status](https://ci.appveyor.com/api/projects/status/bryir507227d0i1q?svg=true)](https://ci.appveyor.com/project/stevennL/snake)|

## Demo

![](img/AI.gif)

## Installation

1. Install [CMake](https://cmake.org/download/).

2. Generate build files using the commands below:

    ```bash
    $ mkdir build
    $ cd build
    $ cmake ..
    ```

3. Build files will be generated in the `build` directory based on your operating system. Use them to build this project:

    | Linux | OS X | Windows |
    |:-----:|:----:|:-------:|
    |Makefile|Makefile|Visual Studio Project|

## Keyboard Controls

| Key | Feature |
|:---:|:-------:|
|W|move up|
|A|move left|
|S|move down|
|D|move right|
|Space|pause/resume the snake|
|Esc|exit game|

**Tips:** When the snake is running, you could press the `Space` key to pause the snake and then press the `W/A/S/D` key to move the snake step by step. Anytime if you want the snake to start running again, just press the `Space` key again.

## AI Strategy

* [Snake.decideNext()](./src/model/Snake.cpp#L106): compute the next move direction ***D*** of the snake ***S1***.

    1. Compute the shortest path ***P1*** from snake ***S1***'s head to the food. If ***P1*** exists, go to step 2. Otherwise go to step 4.

    2. Direct a virtual snake, ***S2*** (the same as ***S1***), to eat the food along path ***P1***.

    3. Compute the longest path ***P2*** from snake ***S2***'s head to its tail. If ***P2*** exists, let ***D*** be the first direction in path ***P1***. Otherwise go to step 4.

    4. Compute the longest path ***P3*** from snake ***S1***'s head to its tail. If ***P3*** exists, let ***D*** be the first direction in path ***P3***. Otherwise go to step 5.

    5. Let ***D*** be the direction that makes the snake the farthest from the food.

* [Snake.findMinPath()](./src/model/Snake.cpp#L229): compute the shortest path between two positions.

    The algorithm is based on BFS. In order to make the result path as straight as possible, each time the adjacent positions are traversed, the position at the current searching direction will be traversed first.

    Here is a vivid description of how it works:

    ![](img/shortest_path.gif)

    (The green area is scanned when searching and the red area is the shortest path. Each number on the point denotes its minimum distance to the starting point.)
  
* [Snake.findMaxPath()](./src/model/Snake.cpp#L274): compute the longest path between two positions.

    The algorithm is based on DFS and the greedy algorithm. Each time the adjacent positions are traversed, the position that is the farthest from the destination (estimated by the Manhatten distance) will be traversed first. In addition, in order to make the result path as straight as possible, if two positions have the same distance to the destination, the position at the current searching direction will be traversed first. Since this is an NP-hard problem, this method is only approximate.

    Here is a vivid description of how it works:
    
    ![](img/longest_path.gif)

    (The green area is scanned when searching and the red area is the longest path. Each number on the point denotes its estimated distance to the destination.)

## Discuss

There are some discussions at [reddit](https://www.reddit.com/r/programming/comments/5ly972/ai_algorithm_of_snake_game_share_opinions_if_you/).

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
