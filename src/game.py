import os
import time
from datetime import datetime, timezone

# pygame envs
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from PIL import Image

from src.agents import init_agent
from src.agents.base import Agent
from src.cell import CellColor, CellType
from src.cfg import Config
from src.direc import Direction
from src.mode import Mode
from src.pos import Pos
from src.snake import Snake


class Game:
    def __init__(
        self,
        mode: Mode,
        move_freq: int,
        show_grid: bool,
        record_frames: bool,
        rand_seed: int | None,
    ) -> None:
        self.mode: Mode = mode
        self.move_freq: int = move_freq
        self.show_grid: bool = show_grid
        self.record_frames: bool = record_frames
        self.rand_seed: int | None = rand_seed
        self.agent: Agent | None = init_agent(self.mode)

        self.snake: Snake
        self.paused: bool
        self.last_move_time: float
        self.next_direc: Direction | None
        self.log_path_pfx: str
        self.frames: list[Image.Image]
        self.reset()

        self.screen: pygame.Surface

    def reset(self) -> None:
        self.snake = Snake(
            Config.GRID_SIZE,
            Config.INIT_SNAKE_POS,
            Config.INIT_SNAKE_CELLS,
            Config.INIT_SNAKE_DIREC,
            Config.INIT_SNAKE_FOOD,
            self.rand_seed,
        )
        self.paused = False
        self.last_move_time = time.monotonic()
        self.next_direc = None
        self.log_path_pfx = self.init_logging()
        self.frames = []

    def init_logging(self) -> str:
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        pfx = os.path.join(Config.LOG_DIR, f"{Config.LOG_PFX}_{self.mode.name}_{ts}")
        with open(pfx + Config.STATES_EXT, "w") as f:
            f.write(f"Random seed for food generation: {self.snake.rand_seed}\n")
            f.write("-" * (Config.GRID_SIZE * 3) + "\n")
        return pfx

    def print_info(self) -> None:
        print("+--------------------------------+")
        print("| Esc    : Quit the game         |")
        print("| Space  : Pause/Resume the game |")
        print("| R      : Restart the game      |")
        print("| W/A/S/D: Move the snake        |")
        print("+--------------------------------+")
        print(f"Game started in {self.mode.name} mode. {self.mode.value}")

    def print_score(self) -> None:
        print(
            f"Score: {self.snake.len():>2} (length of the snake, max={Config.GRID_SIZE**2})"
        )

    def loop(self) -> None:
        self.print_info()

        pygame.init()
        self.screen = pygame.display.set_mode(Config.SCREEN_SIZE, pygame.NOFRAME)
        clock = pygame.time.Clock()

        while True:
            if not self.handle_events():
                break
            self.move()
            self.refresh_screen()
            self.capture_frame()
            clock.tick(Config.FPS)

        self.save_recording()
        pygame.quit()

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.save_recording()
                    self.reset()
                elif event.key == pygame.K_w:
                    self.next_direc = Direction.UP
                elif event.key == pygame.K_a:
                    self.next_direc = Direction.LEFT
                elif event.key == pygame.K_s:
                    self.next_direc = Direction.DOWN
                elif event.key == pygame.K_d:
                    self.next_direc = Direction.RIGHT
        return True

    def move(self) -> None:
        now = time.monotonic()
        if (now - self.last_move_time) * 1000 < self.move_freq:
            return

        self.last_move_time = now

        if self.game_over():
            return

        if not self.next_direc_valid():
            if self.paused:
                self.next_direc = None
            elif self.agent:
                self.next_direc = self.agent.next_direc(self.snake)
            else:
                self.next_direc = self.snake.direc
            if not self.next_direc_valid():
                return

        assert self.next_direc is not None
        self.snake.move(self.next_direc)
        self.next_direc = None
        self.save_states()

        if self.game_over():
            self.print_score()

    def game_over(self) -> bool:
        return self.snake.is_stopped()

    def next_direc_valid(self) -> bool:
        # fmt: off
        return (
            self.next_direc is not None
            and not self.snake.direc.is_opposite(self.next_direc)
        )
        # fmt: on

    def refresh_screen(self) -> None:
        self.screen.fill(CellColor.BACKGROUND.value)

        if self.show_grid:
            for row in range(Config.GRID_SIZE):
                for col in range(Config.GRID_SIZE):
                    self.draw(Pos(row, col), CellType.EMPTY)

        for i, pos in enumerate(self.snake.coords):
            if not self.snake.is_out_of_bound(pos):
                self.draw(pos, self.snake.cells[i])

        if self.snake.food:
            self.draw(self.snake.food, CellType.FOOD)

        pygame.display.flip()

    def draw(self, pos: Pos, cell_type: CellType) -> None:
        self.draw_empty(pos)
        if cell_type == CellType.FOOD:
            self.draw_food(pos)
        else:
            self.draw_snake(pos, cell_type)

    def draw_empty(self, pos: Pos) -> None:
        row, col = pos.row, pos.col
        x = col * Config.CELL_SIZE
        y = row * Config.CELL_SIZE
        w = h = Config.CELL_SIZE
        pygame.draw.rect(self.screen, CellColor.BACKGROUND.value, (x, y, w, h))
        if self.show_grid:
            pygame.draw.rect(self.screen, CellColor.GRID_LINE.value, (x, y, w, h), 1)

    def draw_food(self, pos: Pos) -> None:
        row, col = pos.row, pos.col
        x = col * Config.CELL_SIZE + Config.CELL_PADDING
        y = row * Config.CELL_SIZE + Config.CELL_PADDING
        w = h = Config.CELL_SIZE - 2 * Config.CELL_PADDING
        pygame.draw.rect(self.screen, CellColor.FOOD.value, (x, y, w, h))

    def draw_snake(self, pos: Pos, cell_type: CellType) -> None:
        row, col = pos.row, pos.col
        color = self.snake_color()
        x = y = w = h = 0

        if (
            cell_type == CellType.HEAD_UP
            or cell_type == CellType.BODY_TURN_DL
            or cell_type == CellType.BODY_TURN_DR
        ):
            x = col * Config.CELL_SIZE + Config.CELL_PADDING
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_SIZE - 2 * Config.CELL_PADDING
            h = Config.CELL_SIZE - Config.CELL_PADDING
        elif cell_type == CellType.HEAD_LEFT:
            x = col * Config.CELL_SIZE + Config.CELL_PADDING
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_SIZE - Config.CELL_PADDING
            h = Config.CELL_SIZE - 2 * Config.CELL_PADDING
        elif (
            cell_type == CellType.HEAD_DOWN
            or cell_type == CellType.BODY_TURN_UL
            or cell_type == CellType.BODY_TURN_UR
        ):
            x = col * Config.CELL_SIZE + Config.CELL_PADDING
            y = row * Config.CELL_SIZE
            w = Config.CELL_SIZE - 2 * Config.CELL_PADDING
            h = Config.CELL_SIZE - Config.CELL_PADDING
        elif cell_type == CellType.HEAD_RIGHT:
            x = col * Config.CELL_SIZE
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_SIZE - Config.CELL_PADDING
            h = Config.CELL_SIZE - 2 * Config.CELL_PADDING
        elif cell_type == CellType.BODY_HORZ:
            x = col * Config.CELL_SIZE
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_SIZE
            h = Config.CELL_SIZE - 2 * Config.CELL_PADDING
        elif cell_type == CellType.BODY_VERT:
            x = col * Config.CELL_SIZE + Config.CELL_PADDING
            y = row * Config.CELL_SIZE
            w = Config.CELL_SIZE - 2 * Config.CELL_PADDING
            h = Config.CELL_SIZE

        if w * h > 0:
            pygame.draw.rect(self.screen, color, (x, y, w, h))
            x = y = w = h = 0

        if cell_type == CellType.BODY_TURN_UL or cell_type == CellType.BODY_TURN_DL:
            x = col * Config.CELL_SIZE
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_PADDING
            h = Config.CELL_SIZE - 2 * Config.CELL_PADDING
        elif cell_type == CellType.BODY_TURN_UR or cell_type == CellType.BODY_TURN_DR:
            x = col * Config.CELL_SIZE + Config.CELL_SIZE - Config.CELL_PADDING
            y = row * Config.CELL_SIZE + Config.CELL_PADDING
            w = Config.CELL_PADDING
            h = Config.CELL_SIZE - 2 * Config.CELL_PADDING

        if w * h > 0:
            pygame.draw.rect(self.screen, color, (x, y, w, h))

    def snake_color(self) -> tuple[int, int, int]:
        if self.snake.state == Snake.State.WALKING:
            return CellColor.SNAKE_WALKING.value
        if self.snake.state == Snake.State.DEAD:
            return CellColor.SNAKE_DEAD.value
        if self.snake.state == Snake.State.FULL:
            return CellColor.SNAKE_FULL.value
        assert False, f"Unexpected snake state {self.snake.state.name}"

    def capture_frame(self) -> None:
        if not self.record_frames:
            return
        data = pygame.image.tobytes(self.screen, "RGB")
        size = self.screen.get_size()
        self.frames.append(Image.frombytes("RGB", size, data))

    def save_recording(self) -> None:
        if not self.record_frames or not self.frames:
            return
        self.frames[0].save(
            self.log_path_pfx + Config.RECORD_EXT,
            save_all=True,
            append_images=self.frames[1:],
            duration=int(1000 / Config.FPS),
            loop=0,
        )

    def save_states(self) -> None:
        with open(self.log_path_pfx + Config.STATES_EXT, "a") as f:
            f.write(self.snake.serialize_states() + "\n")
