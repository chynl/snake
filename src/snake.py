import random
import time
from collections import deque
from enum import Enum, auto
from typing import Iterable

from src.cell import CellType, CellValue
from src.direc import Direction
from src.pos import Pos


class Snake:
    class State(Enum):
        WALKING = auto()
        DEAD = auto()
        FULL = auto()

    def __init__(
        self,
        grid_size: int,
        coords: Iterable[Pos],
        cells: Iterable[CellType],
        direc: Direction,
        food: Pos | None,
        rand_seed: int | None = None,
    ):
        self.grid_size: int = grid_size
        self.coords: deque[Pos] = deque(coords)
        self.cells: deque[CellType] = deque(cells)
        self.direc: Direction = direc
        self.food: Pos | None = food
        self.state: Snake.State = Snake.State.WALKING

        if rand_seed is None:
            rand_seed = int(time.monotonic() * 1000)
        self.rand_seed: int = rand_seed
        self.rand: random.Random = random.Random(rand_seed)

        self.grid: list[list[int]] = [
            [CellValue.EMPTY.value for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]
        self.refresh_grid()

    def refresh_grid(self) -> None:
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col] = CellValue.EMPTY.value
        for i, pos in enumerate(reversed(self.coords)):
            if not self.is_out_of_bound(pos):
                self.grid[pos.row][pos.col] = i + 1
        self.refresh_food(self.food)

    def copy(self) -> "Snake":
        return Snake(
            self.grid_size,
            self.coords,
            self.cells,
            self.direc,
            self.food,
            self.rand_seed,
        )

    def move(self, new_direc: Direction) -> None:
        if self.direc.is_opposite(new_direc):
            return  # snake can't move opposite to current direction

        new_head = self.new_head(new_direc)
        will_grow = self.will_grow(new_head)
        will_die = self.will_die(new_head)

        # update old head
        self.cells[-1] = self.old_head_cell_after_move(new_direc)

        # update new head
        new_head_cell = self.new_head_cell_after_move(new_direc)
        self.cells.append(new_head_cell)
        self.coords.append(new_head)

        # update tail and food
        if will_grow:
            self.new_food()
        else:
            self.cells.popleft()
            tail = self.coords.popleft()
            self.grid[tail.row][tail.col] = CellValue.EMPTY.value

        if will_die:
            self.state = Snake.State.DEAD
        elif self.max_len_reached():
            self.state = Snake.State.FULL

        self.refresh_grid()
        self.direc = new_direc

    def new_head(self, new_direc: Direction) -> Pos:
        return self.head().adj(new_direc)

    def will_grow(self, new_head: Pos) -> bool:
        return not self.is_out_of_bound(new_head) and self.is_food(new_head)

    def will_die(self, new_head: Pos) -> bool:
        # fmt: off
        return (
            self.is_out_of_bound(new_head)
            # moving to tail is allowed
            or (self.is_snake(new_head) and not self.is_tail(new_head))
        )
        # fmt: on

    def old_head_cell_after_move(self, new_direc: Direction) -> CellType:
        if self.direc == Direction.UP:
            if new_direc == Direction.UP:
                return CellType.BODY_VERT
            if new_direc == Direction.LEFT:
                return CellType.BODY_TURN_DL
            if new_direc == Direction.RIGHT:
                return CellType.BODY_TURN_DR
        if self.direc == Direction.LEFT:
            if new_direc == Direction.UP:
                return CellType.BODY_TURN_UR
            if new_direc == Direction.LEFT:
                return CellType.BODY_HORZ
            if new_direc == Direction.DOWN:
                return CellType.BODY_TURN_DR
        if self.direc == Direction.DOWN:
            if new_direc == Direction.LEFT:
                return CellType.BODY_TURN_UL
            if new_direc == Direction.DOWN:
                return CellType.BODY_VERT
            if new_direc == Direction.RIGHT:
                return CellType.BODY_TURN_UR
        if self.direc == Direction.RIGHT:
            if new_direc == Direction.UP:
                return CellType.BODY_TURN_UL
            if new_direc == Direction.DOWN:
                return CellType.BODY_TURN_DL
            if new_direc == Direction.RIGHT:
                return CellType.BODY_HORZ
        assert False, f"Unexpected direction from {self.direc} to {new_direc}"

    def new_head_cell_after_move(self, new_direc: Direction) -> CellType:
        if new_direc == Direction.UP:
            return CellType.HEAD_UP
        if new_direc == Direction.LEFT:
            return CellType.HEAD_LEFT
        if new_direc == Direction.DOWN:
            return CellType.HEAD_DOWN
        if new_direc == Direction.RIGHT:
            return CellType.HEAD_RIGHT
        assert False, f"Unexpected direction {new_direc}"

    def new_food(self) -> None:
        empty: list[Pos] = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == CellValue.EMPTY.value:
                    empty.append(Pos(row, col))
        self.refresh_food(self.rand.choice(empty) if empty else None)

    def refresh_food(self, pos: Pos | None) -> None:
        self.food = pos
        if pos:
            self.grid[pos.row][pos.col] = CellValue.FOOD.value

    def max_len_reached(self) -> bool:
        return self.len() >= self.grid_size**2

    def is_stopped(self) -> bool:
        return self.state != Snake.State.WALKING

    def is_empty(self, pos: Pos) -> bool:
        return self.grid[pos.row][pos.col] == CellValue.EMPTY.value

    def is_food(self, pos: Pos) -> bool:
        return self.grid[pos.row][pos.col] == CellValue.FOOD.value

    def is_snake(self, pos: Pos) -> bool:
        return self.grid[pos.row][pos.col] > 0

    def is_tail(self, pos: Pos) -> bool:
        return pos == self.tail()

    def is_out_of_bound(self, pos: Pos) -> bool:
        return (
            pos.row < 0
            or pos.row >= self.grid_size
            or pos.col < 0
            or pos.col >= self.grid_size
        )

    def head(self) -> Pos:
        return self.coords[-1]

    def tail(self) -> Pos:
        return self.coords[0]

    def len(self) -> int:
        return len(self.coords)

    def serialize_states(self) -> str:
        lines: list[str] = []
        for row in range(self.grid_size):
            lines.append(
                " ".join(f"{self.grid[row][col]:>2}" for col in range(self.grid_size))
            )
        lines.append("".join("-" * (self.grid_size * 3)) + f" Length: {self.len():>2}")
        return "\n".join(lines)
