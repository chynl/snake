import random
from collections import deque

from src.agents.base import Agent
from src.direc import Direction
from src.pos import Pos
from src.snake import Snake


class GraphAgent(Agent):
    HAMILTON_SEARCH_LIMIT: int = 10_000
    HAMILTON_THRESHOLD: int = 16

    def __init__(self):
        self.rand = random.Random()

        self.snake: Snake | None
        self.hamilton_index: list[list[int]]
        self.hamilton_search_count: int
        self.reset()

    def reset(self, snake: Snake | None = None) -> None:
        self.snake = snake
        self.hamilton_index = []
        self.hamilton_search_count = 0

    def next_direc(self, snake: Snake) -> Direction:
        if self.snake != snake:
            self.reset(snake)

        food = snake.food
        assert food is not None

        neighbors = self.neighbors(snake.head(), snake, set())
        if not neighbors:
            # snake is trapped, move in current direction to end the game
            return snake.direc

        # follow hamiltonian cycle if exists
        if self.hamilton_index:
            return self.hamilton_direc(neighbors, snake)

        # try building hamiltonian cycle if snake is long enough
        if snake.len() >= GraphAgent.HAMILTON_THRESHOLD:
            path_to_tail = self.hamilton_path(snake.tail(), snake)
            if path_to_tail:
                self.build_hamilton_index(path_to_tail, snake)
                return self.hamilton_direc(neighbors, snake)

        # search shortest path to food
        path_to_food = self.shortest_path(food, snake)
        if path_to_food:
            # try moving the snake along the shortest path to eat the food
            snake_copy = snake.copy()
            for direc in path_to_food:
                snake_copy.move(direc)
            path_to_tail = self.shortest_path(snake_copy.tail(), snake_copy)
            # if after eating the food the snake can still reach its tail, follow the path to food
            if path_to_tail:
                return path_to_food[0]

        # no safe path to food, try moving along a longer path to tail
        path_to_tail = self.longer_path(snake.tail(), snake)
        if path_to_tail:
            return path_to_tail[0]

        # no path to tail either, just move further away from the food
        neighbors.sort(
            key=lambda x: self.manhattan_dist(x[1], food),
            reverse=True,
        )
        return neighbors[0][0]

    def shortest_path(self, dst: Pos, snake: Snake) -> list[Direction]:
        src = snake.head()
        visited = {src}
        queue: deque[tuple[Pos, list[Direction]]] = deque([(src, [])])
        while queue:
            pos, path = queue.popleft()
            if pos == dst:
                return path
            for direc, pos in self.neighbors(pos, snake, visited):
                queue.append((pos, path + [direc]))
                visited.add(pos)
        return []

    def longer_path(self, dst: Pos, snake: Snake) -> list[Direction]:
        """Build a path slightly longer than the shortest path."""
        shortest = self.shortest_path(dst, snake)
        longest: list[Direction] = []
        cur = snake.head()

        for direc in shortest:
            nxt = cur.adj(direc)
            extended = False

            test_direcs = []
            if direc in (Direction.UP, Direction.DOWN):
                test_direcs = [Direction.LEFT, Direction.RIGHT]
            else:
                test_direcs = [Direction.UP, Direction.DOWN]

            for test_direc in test_direcs:
                cur_extended = cur.adj(test_direc)
                nxt_extended = nxt.adj(test_direc)

                cur_extendable = (
                    self.is_reachable(cur_extended, snake)
                    # eating the food might trap the snake, so we don't extend if there's food
                    and not snake.is_food(cur_extended)
                )

                nxt_extendable = (
                    self.is_reachable(nxt_extended, snake)
                    # coords[1] is the second last snake body which will become
                    # the new tail after the move, so it's safe to extend
                    or nxt_extended == snake.coords[1]
                )

                if cur_extendable and nxt_extendable:
                    longest.append(test_direc)
                    longest.append(direc)
                    longest.append(test_direc.opposite())
                    extended = True
                    break

            if not extended:
                longest.append(direc)

            cur = nxt

        return longest

    def build_hamilton_index(self, path: list[Direction], snake: Snake) -> None:
        self.hamilton_index = [list(row) for row in snake.grid]
        cur = snake.head()
        val = snake.grid_size**2
        for direc in path:
            nxt = cur.adj(direc)
            self.hamilton_index[nxt.row][nxt.col] = val
            cur = nxt
            val -= 1

    def hamilton_direc(
        self,
        neighbors: list[tuple[Direction, Pos]],
        snake: Snake,
    ) -> Direction:
        assert self.hamilton_index
        head = snake.head()
        head_index = self.hamilton_index[head.row][head.col]
        target_index = head_index - 1 if head_index > 1 else len(snake.grid) ** 2
        for direc, nbr in neighbors:
            if self.hamilton_index[nbr.row][nbr.col] == target_index:
                return direc
        assert False, "Invalid hamilton index"

    def hamilton_path(self, dst: Pos, snake: Snake) -> list[Direction]:
        self.hamilton_search_count = 0
        src = snake.head()
        visited = {src}
        path: list[Direction] = []
        target_len = self.num_reachable(snake)
        if self.hamilton_backtrack(src, dst, snake, visited, path, target_len):
            return path
        return []

    def hamilton_backtrack(
        self,
        cur: Pos,
        dst: Pos,
        snake: Snake,
        visited: set[Pos],
        path: list[Direction],
        target_len: int,
    ) -> bool:
        if len(path) == target_len:
            return cur == dst

        if self.hamilton_search_count >= GraphAgent.HAMILTON_SEARCH_LIMIT:
            return False
        self.hamilton_search_count += 1

        # explore neighbors with fewer onward moves first (Warnsdorf's heuristic)
        neighbors = self.neighbors(cur, snake, visited)
        neighbors.sort(key=lambda x: self.hamilton_heuristic(x[1], snake, visited))

        for direc, nbr in neighbors:
            # don't visit dst early unless it completes the path (pruning)
            if nbr == dst and len(path) < target_len - 1:
                continue

            visited.add(nbr)
            path.append(direc)

            if self.hamilton_backtrack(nbr, dst, snake, visited, path, target_len):
                return True

            path.pop()
            visited.remove(nbr)

        return False

    def hamilton_heuristic(self, pos: Pos, snake: Snake, visited: set[Pos]) -> int:
        return len(self.neighbors(pos, snake, visited))

    def manhattan_dist(self, p1: Pos, p2: Pos) -> int:
        return abs(p1.row - p2.row) + abs(p1.col - p2.col)

    def neighbors(
        self,
        pos: Pos,
        snake: Snake,
        visited: set[Pos],
    ) -> list[tuple[Direction, Pos]]:
        result: list[tuple[Direction, Pos]] = []
        for direc in Direction:
            nbr = pos.adj(direc)
            if self.is_reachable(nbr, snake) and nbr not in visited:
                result.append((direc, nbr))
        self.rand.shuffle(result)  # randomize to reduce bias in path selection
        return result

    def num_reachable(self, snake: Snake) -> int:
        m, n = len(snake.grid), len(snake.grid[0])
        cnt = 0
        for row in range(m):
            for col in range(n):
                if self.is_reachable(Pos(row, col), snake):
                    cnt += 1
        return cnt

    def is_reachable(self, pos: Pos, snake: Snake) -> bool:
        # fmt: off
        return (
            not snake.is_out_of_bound(pos)
            and (snake.is_empty(pos) or snake.is_food(pos) or snake.is_tail(pos))
        )
        # fmt: on
