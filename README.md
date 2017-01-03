:uk: English / [:cn: 中文](./README-CN.md)

# Snake-AI

AI of snake game.

The goal is to eat all the food and make the map fill with the snake's bodies. 

To contribute, please see [todos](#todos).

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

## Algorithm Description

* [Snake.decideNext()](./src/Snake.cpp): compute the next move direction ***D*** of the snake ***S1***

    1. Compute the shortest path ***P1*** from the snake ***S1***'s head to food.

    2. Move a virtual snake ***S2***(the same as ***S1***) to eat the food along path ***P1***.

    3. Compute the longest path ***P2*** from the snake ***S2***'s head to its tail. If ***P2*** exists, let ***D*** be the first direction in path ***P1***. Otherwise go to step 4.

    4. Compute the longest path ***P3*** from the snake ***S1***'s head to its tail. If ***P3*** exists, let ***D*** be the first direction in path ***P3***. Otherwise go to step 5.

    5. Let ***D*** be the direction that makes the snake the farthest from food.

* [Map.findMinPath()](./src/Map.cpp): compute the shortest path between two positions

    The algorithm is based on BFS. In order to make the result path as straight as possible, each time when traversing the adjacent positions, the position at the current direction will be traversed first.

    Here is a vivid description of how it works:

    (The green area is scanned when searching and the red area is the shortest path. Each number at the point stores its minimum distance from the start point.)

    ![Image of searching shortest path](img/shortest_path.gif)
  
* [Map.findMaxPath()](./src/Map.cpp): compute the longest path between two positions

    The algorithm is based on DFS and the greedy algorithm. Each time when traversing the adjacent positions, the position that is the farthest(estimated by Manhatten distance) from the destination will be traversed first. In addition, in order to make the result path as straight as possible, if two positions have the same distance to the destination, the position at the current direction will be traversed first. Since this is an NP-hard problem, this method is only approximate.

    Here is a vivid description of how it works:

    (The green area is scanned when searching and the red area is the longest path. Each number at the point stores its estimated distance to the destination.)

    ![Image of searching longest path](img/longest_path.gif)
 
## Todos

Optimize AI algorithm:

AI algorithm is imperfect since the snake sometimes moves to an insoluable situation(just run the program and you will see).

Some possible solutions:
  
| # | Solution | Implemented? | Comment |
|:-:|----------|:------------:|---------|
|1|~~Do not create food at the positions whose adjacent positions contain a snake's head and a snake's tail.~~|No|Although effective, this is a tricky solution since it modifies the game rules instead of the AI algorithm itself. Thus there is no need to implement it.|
|2|Make the search path contain as few corners as possible, namely as straight as possible.|Yes|Effective. If the path is as straight as possible, there will be much less scattered empty positions on the map, which makes it easier for the snake to eat as much food as possible.|
|3|When searching for the shortest path to food, take into account the fact that the snake frees squares as it moves.|No|Waiting for implementation.|

**You could contribute by commenting or implementing the solutions above or by adding new possible solutions.**

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
