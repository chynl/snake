from src.direc import Direction


class Pos:
    def __init__(self, row: int, col: int):
        self.row: int = row
        self.col: int = col

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pos):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def adj(self, direc: Direction) -> "Pos":
        return Pos(self.row + direc.value[0], self.col + direc.value[1])
