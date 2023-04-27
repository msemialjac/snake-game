import pygame
import PySimpleGUI as sg
import random
import time

# Constants
WINDOW_SIZE = (800, 600)
GRID_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = WINDOW_SIZE[0] // GRID_SIZE, WINDOW_SIZE[1] // GRID_SIZE
SNAKE_COLORS = [(0, 255, 0), (0, 128, 255), (255, 255, 0), (255, 0, 128)]
CELL_SIZE = 20


class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (0, -1)

    def move(self):
        head = (
            self.body[0][0] + self.direction[0],
            self.body[0][1] + self.direction[1],
        )
        self.body.insert(0, head)
        self.body.pop()

    def grow(self):
        self.body.append(self.body[-1])

    def change_direction(self, new_direction):
        if (new_direction[0] != -self.direction[0]) and (
            new_direction[1] != -self.direction[1]
        ):
            self.direction = new_direction

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            color = SNAKE_COLORS[i % len(SNAKE_COLORS)]
            pygame.draw.rect(
                surface,
                color,
                (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )


class Food:
    def __init__(self, snake_body, obstacles):
        self.position = self.generate_new_position(snake_body, obstacles)

    def generate_new_position(self, snake_body, obstacles):
        while True:
            position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(1, GRID_HEIGHT - 2),
            )
            if position not in snake_body and position not in [
                o.position for o in obstacles
            ]:
                return position

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (255, 0, 0),
            (
                self.position[0] * GRID_SIZE,
                self.position[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            ),
        )


class Obstacle:
    def __init__(self, snake_body, food_position, obstacles):
        self.position = self.generate_new_position(snake_body, food_position, obstacles)

    def generate_new_position(self, snake_body, food_position, obstacles):
        while True:
            position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if (
                position not in snake_body
                and position != food_position
                and position not in [o.position for o in obstacles]
            ):
                return position

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (128, 128, 128),
            (
                self.position[0] * GRID_SIZE,
                self.position[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            ),
        )


class GameState:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body, [])
        self.obstacles = []

    def new_game(self, difficulty):
        self.snake = Snake()
        self.food = Food(self.snake.body, self.obstacles)
        self.obstacles = [
            Obstacle(self.snake.body, self.food.position, self.obstacles)
            for _ in range(difficulty * 5)
        ]


class SnakeGame:
    def __init__(self):
        pygame.init()
        sg.theme("DarkAmber")

        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.difficulty = 1
        self.start_time = time.time()
        self.score = 0
        self.rank = 1
        self.games_played = 0
        self.high_scores = []

        self.frame_padding = 20
        self.info_padding = 120
        self.window_width = GRID_WIDTH * CELL_SIZE + self.frame_padding * 2
        self.window_height = (
            GRID_HEIGHT * CELL_SIZE + self.frame_padding * 2 + self.info_padding
        )
        self.window = pygame.display.set_mode((self.window_width, self.window_height))

        pygame.display.set_caption("Snake Game")

    def main_menu(self):
        layout = [
            [
                sg.Text(
                    "Snake Game",
                    size=(30, 1),
                    font=("Helvetica", 25),
                    justification="center",
                )
            ],
            [sg.Text("Choose difficulty:")],
            [sg.Button(str(i)) for i in range(1, 6)],
            [sg.Button("Exit")],
        ]
        window = sg.Window("Snake Game", layout)
        while True:
            event, values = window.read()
            if event in [str(i) for i in range(1, 6)]:
                self.difficulty = int(event)
                window.close()
                self.new_game()
            elif event == sg.WIN_CLOSED or event == "Exit":
                window.close()
                pygame.quit()
                break

    def update_high_scores(self):
        new_score = {
            "play_no": self.games_played,
            "score": self.score,
            "rank": self.rank,
            "level": self.difficulty,
        }
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)

    def new_game(self):
        self.game_state.new_game(self.difficulty)
        self.start_time = time.time()
        self.score = 0
        self.rank = 1
        self.game_loop()

    def game_over(self):
        self.games_played += 1
        self.update_high_scores()

        layout = [
            [
                sg.Text(
                    f"Game Over! This was your {self.games_played}. attempt",
                    size=(30, 1),
                    font=("Helvetica", 25),
                    justification="center",
                )
            ],
            [sg.Text("High Scores:")],
        ]

        for i, score in enumerate(self.high_scores[:5], 1):
            layout.append(
                [
                    sg.Text(
                        f"{i}. Play no. {score['play_no']}   Scored points: {score['score']} Rank: {score['rank']} "
                        f"Level: {score['level']}"
                    )
                ]
            )

        layout.extend([[sg.Button("Main Menu"), sg.Button("Exit")]])

        window = sg.Window("Game Over", layout)
        while True:
            event, values = window.read()
            if event == "Main Menu":
                window.close()
                self.main_menu()
            elif event == sg.WIN_CLOSED or event == "Exit":
                window.close()
                pygame.quit()
                break

    def game_loop(self):
        running = True
        while running:
            self.window.fill((52, 58, 64))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.game_state.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.game_state.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.game_state.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.game_state.snake.change_direction((1, 0))

            self.game_state.snake.move()
            # if self.check_collision():
            #     self.new_game()
            #     break
            if self.check_collision():
                self.game_over()
                break

            self.game_state.snake.draw(self.window)
            self.game_state.food.draw(self.window)

            for obstacle in self.game_state.obstacles:
                obstacle.draw(self.window)

            self.update_score()
            self.draw_game()
            pygame.display.update()
            self.clock.tick(10)

    def update_score(self):
        elapsed_time = time.time() - self.start_time
        food_eaten = len(self.game_state.snake.body) - 1
        self.score = int(elapsed_time * 10) + food_eaten * 5
        self.rank = 1 + food_eaten // 5

    def draw_game(self):
        pygame.draw.rect(
            self.window,
            (0, 0, 0),
            (
                self.frame_padding - 2,
                self.frame_padding - 2,
                GRID_WIDTH * CELL_SIZE + 4,
                GRID_HEIGHT * CELL_SIZE + 4,
            ),
            2,
        )
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        time_text = font.render(
            f"Time: {int(time.time() - self.start_time)}", True, (255, 255, 255)
        )
        rank_text = font.render(f"Rank: {self.rank}", True, (255, 255, 255))

        self.window.blit(
            score_text, (10, GRID_HEIGHT * CELL_SIZE + self.frame_padding * 2)
        )
        self.window.blit(
            time_text, (10, GRID_HEIGHT * CELL_SIZE + self.frame_padding * 2 + 40)
        )
        self.window.blit(
            rank_text, (10, GRID_HEIGHT * CELL_SIZE + self.frame_padding * 2 + 80)
        )

    def check_collision(self):
        head = self.game_state.snake.body[0]

        # Check if the snake collides with the window borders
        if (
            head[0] < 0
            or head[0] >= GRID_WIDTH
            or head[1] < 0
            or head[1] >= GRID_HEIGHT
        ):
            return True

        # Check if the snake collides with itself
        if head in self.game_state.snake.body[1:]:
            return True

        # Check if the snake collides with food
        if head == self.game_state.food.position:
            self.game_state.snake.grow()
            self.game_state.food = Food(
                self.game_state.snake.body, self.game_state.obstacles
            )

        # Check if the snake collides with obstacles
        for obstacle in self.game_state.obstacles:
            if head == obstacle.position:
                return True

        return False


if __name__ == "__main__":
    game = SnakeGame()
    game.main_menu()
