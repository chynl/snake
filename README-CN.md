[:uk: English](./README.md) / :cn: 中文

# Snake

贪吃蛇游戏的人工智能算法实现。

我们希望这条蛇**尽快的**吃掉食物从而使它的身子铺满整个地图，因此它不应该总是按照一个特定的路径（比如“之”字形）行走。

## Build 状态

| Linux | Windows |
|:-----:|:-------:|
|[![Build Status](https://travis-ci.org/stevennL/Snake.svg?branch=master)](https://travis-ci.org/stevennL/Snake)|[![Build Status](https://ci.appveyor.com/api/projects/status/bryir507227d0i1q?svg=true)](https://ci.appveyor.com/project/stevennL/snake)|

## 效果展示

![](img/AI.gif)

## 安装

1. 安装 [CMake](https://cmake.org/download/)。

2. 输入以下命令得到用于build这个项目的文件:

    ```bash
    $ mkdir build
    $ cd build
    $ cmake ..
    ```

3. 一些文件将会根据你的操作系统在`build`目录中生成，利用这些文件可以build这个项目：

    | Linux | OS X | Windows |
    |:-----:|:----:|:-------:|
    |Makefile|Makefile|Visual Studio Project|

## 键盘控制

| 按键 | 功能 |
|:---:|:-------:|
|W|上移|
|A|左移|
|S|下移|
|D|右移|
|空格|（暂停/恢复）蛇的移动|
|Esc|退出游戏|

**提示：**当蛇在移动时，你可以按下`空格键`来暂停它，然后使用`W/A/S/D`键以单步的方式移动蛇。任何时候如果你想让蛇恢复移动，再次按下`空格键`即可。

## AI策略

* 函数[Snake.decideNext()](./src/model/Snake.cpp#L103): 计算蛇***S1***的下一个移动方向***D***

    1. 计算从蛇***S1***的头部到达食物的最短路径***P1***。如果路径***P1***存在，进行步骤2。否则，进行步骤4。

    2. 派一条与蛇***S1***完全一样的虚拟蛇***S2***沿路径***P1***吃掉食物。

    3. 计算从蛇***S2***的头部到其尾部的最长路径***P2***。如果路径***P2***存在，将移动方向***D***设置为路径***P1***的第一个方向，否则进行步骤4。

    4. 计算从蛇***S1***的头部到达其尾部的最长路径***P3***。如果***P3***存在，将移动方向***D***设置为路径***P3***的第一个方向，否则进行步骤5。

    5. 将移动方向***D***设置为离食物最远的方向。

* 函数[Snake.findMinPath()](./src/model/Snake.cpp#L176): 计算两个位置间的最短路径

    算法建立在BFS的基础上。为了使路径尽可能直，每次遍历邻接点时，在当前搜索方向上的位置会被优先遍历。

    效果展示:

    ![](img/shortest_path.gif)

    （绿色区域为搜索算法扫描到的区域，红色区域为最后计算出的最短路径，每个位置上的数字表示了从起始位置开始到该位置的最短距离）
  
* 函数[Snake.findMaxPath()](./src/model/Snake.cpp#L220): 计算两个位置间的最长路径

    算法建立在DFS与贪心算法的基础上。每次遍历邻接点时，离目标位置最远（使用曼哈顿距离估计）的位置将会被优先遍历到。另外，为了使路径尽可能直，如果两个位置到目标位置的距离相等，在当前搜索方向上的位置将被优先遍历到。这个问题是一个NP完全问题，此算法得出的结果路径只是一个近似最长路径。

    效果展示:
    
    ![](img/longest_path.gif)

    （绿色区域为搜索算法扫描到的区域，红色区域为最后计算出的最长路径，每个位置上的数字表示了从该位置开始到目标位置的估计距离）

## 讨论

在[reddit](https://www.reddit.com/r/programming/comments/5ly972/ai_algorithm_of_snake_game_share_opinions_if_you/)上有关于这个项目的一些讨论。

## License

See the [LICENSE](./LICENSE) file for license rights and limitations.
