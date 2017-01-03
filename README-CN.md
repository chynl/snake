[:uk: English](./README.md) / :cn: 中文

# Snake

[![Build Status](https://travis-ci.org/stevennL/Snake.svg?branch=master)](https://travis-ci.org/stevennL/Snake)

贪吃蛇游戏的人工智能算法实现。

AI的目的是让蛇尽可能的吃更多的食物，直到吃满整个地图。

## 效果展示

![AI演示图](img/AI.gif)

## 安装

1. 安装 [CMake](https://cmake.org/)。

2. 输入以下命令build这个项目:

    ```bash
    $ mkdir build
    $ cd build
    $ cmake ..
    ```

3. 在build目录中，你可以找到：

    * 运行于Linux平台的Makefile
    * 运行于Windows平台的Visual Studio项目
    * 运行于OS X平台的Xcode项目

## 键盘控制

| Key | Feature |
|:---:|:-------:|
|W|上移|
|A|左移|
|S|下移|
|D|右移|
|Space|（暂停/恢复）蛇的移动|
|Esc|退出游戏|

## AI策略

* 函数[Snake.decideNext()](./src/Snake.cpp): 计算蛇***S1***的下一个移动方向***D***

    1. 计算从蛇***S1***的头部到达食物的最短路径***P1***。

    2. 派一条与蛇***S1***完全一样的虚拟蛇***S2***沿路径***P1***吃掉食物。

    3. 计算从蛇***S2***的头部到其尾部的最长路径***P2***。如果路径***P2***存在，将移动方向***D***设置为路径***P1***的第一个方向，否则进行步骤4。

    4. 计算从蛇***S1***的头部到达其尾部的最长路径***P3***。如果***P3***存在，将移动方向***D***设置为路径***P3***的第一个方向，否则进行步骤5。

    5. 将移动方向***D***设置为离食物最远的方向。

* 函数[Map.findMinPath()](./src/Map.cpp): 计算两个位置间的最短路径

    算法建立在BFS的基础上。为了使路径尽可能直，每次遍历邻接点时，在当前搜索方向上的位置会被优先遍历。

    效果展示:

    ![](img/shortest_path.gif)

    （绿色区域为搜索算法扫描到的区域，红色区域为最后计算出的最短路径，每个位置上的数字表示了从起始位置开始到该位置的最短距离）
  
* 函数[Map.findMaxPath()](./src/Map.cpp): 计算两个位置间的最长路径

    算法建立在DFS与贪心算法的基础上。每次遍历邻接点时，离目标位置最远（使用曼哈顿距离估计）的位置将会被优先遍历到。另外，为了使路径尽可能直，如果两个位置到目标位置的距离相等，在当前搜索方向上的位置将被优先遍历到。这个问题是一个NP完全问题，此算法得出的结果路径只是一个近似最长路径。

    效果展示:
    
    ![](img/longest_path.gif)

    （绿色区域为搜索算法扫描到的区域，红色区域为最后计算出的最长路径，每个位置上的数字表示了从该位置开始到目标位置的估计距离）

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
