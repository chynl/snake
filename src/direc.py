from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)
    RIGHT = (0, 1)

    def is_opposite(self, other: "Direction") -> bool:
        if self == Direction.UP and other == Direction.DOWN:
            return True
        if self == Direction.LEFT and other == Direction.RIGHT:
            return True
        if self == Direction.DOWN and other == Direction.UP:
            return True
        if self == Direction.RIGHT and other == Direction.LEFT:
            return True
        return False

    def opposite(self) -> "Direction":
        if self == Direction.UP:
            return Direction.DOWN
        if self == Direction.LEFT:
            return Direction.RIGHT
        if self == Direction.DOWN:
            return Direction.UP
        if self == Direction.RIGHT:
            return Direction.LEFT
        assert False, "Invalid direction"

    def left(self) -> "Direction":
        if self == Direction.UP:
            return Direction.LEFT
        if self == Direction.LEFT:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.RIGHT
        if self == Direction.RIGHT:
            return Direction.UP
        assert False, "Invalid direction"

    def right(self) -> "Direction":
        if self == Direction.UP:
            return Direction.RIGHT
        if self == Direction.LEFT:
            return Direction.UP
        if self == Direction.DOWN:
            return Direction.LEFT
        if self == Direction.RIGHT:
            return Direction.DOWN
        assert False, "Invalid direction"

    def index(self) -> int:
        if self == Direction.UP:
            return 0
        if self == Direction.LEFT:
            return 1
        if self == Direction.DOWN:
            return 2
        if self == Direction.RIGHT:
            return 3
        assert False, "Invalid direction"
