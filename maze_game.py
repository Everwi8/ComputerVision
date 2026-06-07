import pygame
import sys
import random

CELL = 40
COLS = 21   # must be odd for the maze generator
ROWS = 15   # must be odd for the maze generator
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 44   # +44 for status bar
SPEED = 3
PLAYER_RADIUS = CELL // 2 - 5

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
BLUE   = (60,  130, 220)
GOLD   = (220, 180, 20)
DARK   = (25,  25,  35)
WALL   = (55,  60,  80)
PATH   = (215, 215, 225)
BAR    = (15,  15,  25)


def generate_maze(cols, rows):
    maze = [[1] * cols for _ in range(rows)]

    def carve(r, c):
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and maze[nr][nc] == 1:
                maze[r + dr // 2][c + dc // 2] = 0
                maze[nr][nc] = 0
                carve(nr, nc)

    maze[1][1] = 0
    carve(1, 1)
    return maze


def is_wall(maze, x, y):
    col = int(x) // CELL
    row = int(y) // CELL
    if not (0 <= row < ROWS and 0 <= col < COLS):
        return True
    return maze[row][col] == 1


def can_move(maze, px, py, dx, dy):
    nx, ny = px + dx, py + dy
    r = PLAYER_RADIUS
    for cx, cy in [(nx-r, ny-r), (nx+r, ny-r), (nx-r, ny+r), (nx+r, ny+r)]:
        if is_wall(maze, cx, cy):
            return False
    return True


def new_game():
    return {
        "maze": generate_maze(COLS, ROWS),
        "px": float(CELL + CELL // 2),
        "py": float(CELL + CELL // 2),
        "won": False,
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze — WASD / Hand Controller")
    clock = pygame.time.Clock()
    font     = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 80)

    state = new_game()
    goal_cell = (COLS - 2, ROWS - 2)   # bottom-right open cell

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN):
                    state = new_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Movement (axes handled independently so the player slides along walls)
        if not state["won"]:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = SPEED

            if dx and can_move(state["maze"], state["px"], state["py"], dx, 0):
                state["px"] += dx
            if dy and can_move(state["maze"], state["px"], state["py"], 0, dy):
                state["py"] += dy

            # Win when player centre enters the goal cell
            gc, gr = goal_cell
            if gc * CELL < state["px"] < (gc + 1) * CELL and \
               gr * CELL < state["py"] < (gr + 1) * CELL:
                state["won"] = True

        # ── Draw ──────────────────────────────────────────────────────────
        screen.fill(DARK)

        maze = state["maze"]
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
                pygame.draw.rect(screen, WALL if maze[row][col] else PATH, rect)

        # Goal tile
        gc, gr = goal_cell
        goal_rect = pygame.Rect(gc * CELL, gr * CELL, CELL, CELL)
        pygame.draw.rect(screen, GOLD, goal_rect)
        label = font.render("EXIT", True, BLACK)
        screen.blit(label, (goal_rect.x + (CELL - label.get_width()) // 2,
                             goal_rect.y + (CELL - label.get_height()) // 2))

        # Player
        pygame.draw.circle(screen, BLUE,
                            (int(state["px"]), int(state["py"])), PLAYER_RADIUS)

        # Status bar
        pygame.draw.rect(screen, BAR, (0, ROWS * CELL, WIDTH, 44))
        hint = font.render("WASD / hand to move     R = new maze     ESC = quit", True, WHITE)
        screen.blit(hint, (10, ROWS * CELL + 8))

        # Win overlay
        if state["won"]:
            overlay = pygame.Surface((WIDTH, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("YOU WIN!", True, GOLD)
            sub = font.render("Press R for a new maze", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2,
                               ROWS * CELL // 2 - 60))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2,
                               ROWS * CELL // 2 + 30))

        pygame.display.flip()


if __name__ == "__main__":
    main()
