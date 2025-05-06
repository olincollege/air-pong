import pygame
from vpython import vector
from air_pong_model import PongModel


class PongView:
    """view class for air-pong game"""

    def __init__(self):
        pygame.font.init()
        self.background_colour = (255, 255, 255)
        self.unit_scaling = 0
        self.x_shift = 0.5 * (5 - 2.74)
        self.y_shift = 2
        self.colour = (0, 0, 0)
        self.screen = pygame.display.set_mode((1500, 600))  # 5x2
        self.ping_pong_table = pygame.image.load("models/ping_pong_table.png")
        self.scoreboard = pygame.image.load("models/scoreboard.png")
        self.win_screen = pygame.image.load("models/win_screen.png")
        self.score_font = pygame.font.Font("models/monofonto_rg.otf", 0)
        self.win_font = pygame.font.Font("models/monofonto_rg.otf", 0)

    def prepare_images(self, pong_instance, screen):
        self.screen = screen
        self.unit_scaling = screen.get_width() / 5
        self.ping_pong_table = pygame.transform.scale(
            self.ping_pong_table,
            (
                self.unit_scaling * pong_instance.table_dim.x,
                self.unit_scaling * pong_instance.table_dim.z,
            ),
        )
        self.scoreboard = pygame.transform.scale(
            self.scoreboard,
            (
                self.unit_scaling * pong_instance.table_dim.x,
                self.unit_scaling * 0.1875,
            ),
        )
        self.score_font = pygame.font.Font(
            "models/monofonto_rg.otf", int(self.unit_scaling * 0.18)
        )
        self.win_font = pygame.font.Font(
            "models/monofonto_rg.otf", int(self.unit_scaling * 0.18)
        )
        self.win_screen = pygame.transform.scale(
            self.win_screen, (self.unit_scaling * 5, self.unit_scaling * 2)
        )

    def display(self, pong_instance, screen):
        self.screen = screen
        screen.fill((self.background_colour))
        # Ball
        spin_color = 17 * min(pong_instance.ball_spin.mag, 15)
        pygame.draw.circle(
            screen,
            (spin_color, spin_color, spin_color),
            (
                self.unit_scaling * pong_instance.ball_position.x,
                self.unit_scaling
                * (self.y_shift - pong_instance.ball_position.y),
            ),
            self.unit_scaling * pong_instance.ball_radius,
            width=0,
        )
        # Ball outline
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (
                self.unit_scaling * pong_instance.ball_position.x,
                self.unit_scaling
                * (self.y_shift - pong_instance.ball_position.y),
            ),
            self.unit_scaling * pong_instance.ball_radius,
            width=1,
        )

        # paddle
        pygame.draw.polygon(
            screen,
            (255, 0, 0),
            (
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][0][0],
                    self.unit_scaling
                    * (self.y_shift - pong_instance.paddle_edges[0][0][1]),
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][1][0],
                    self.unit_scaling
                    * (self.y_shift - pong_instance.paddle_edges[0][0][1]),
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][0][0],
                    self.unit_scaling
                    * (self.y_shift - pong_instance.paddle_edges[0][0][1]),
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][1][0],
                    self.unit_scaling
                    * (self.y_shift - pong_instance.paddle_edges[0][1][1]),
                ),
            ),
        )
        # table
        screen.blit(
            self.ping_pong_table,
            (
                self.unit_scaling * self.x_shift,
                self.unit_scaling * (self.y_shift - 0.653796),
            ),
        )
        # table net
        pygame.draw.rect(
            screen,
            self.colour,
            (
                self.unit_scaling
                * (self.x_shift + pong_instance.table_dim.x / 2),
                self.unit_scaling * (self.y_shift - 0.1525 - 0.653796),
                self.unit_scaling * 0.012,  # Width of the net
                self.unit_scaling * 0.1525,  # Height of the net
            ),
        )
        # scoreboard
        screen.blit(
            self.scoreboard,
            (
                self.unit_scaling * self.x_shift,
                0,
            ),
        )
        pygame.font.init()
        left_score = self.score_font.render(
            f"{pong_instance.player_score[0]}", True, (255, 255, 255)
        )
        left_score_rect = left_score.get_rect()
        left_score_rect.topleft = (
            self.unit_scaling * (self.x_shift + 0.085),
            -(
                self.unit_scaling * 0.017
            ),  # 0.017 is the space above the number in the font
        )  # .085 is the scoreboard arc radius
        screen.blit(left_score, left_score_rect)
        right_score = self.score_font.render(
            f"{pong_instance.player_score[1]}", True, (255, 255, 255)
        )
        right_score_rect = left_score.get_rect()
        right_score_rect.topright = (
            self.unit_scaling
            * (self.x_shift + pong_instance.table_dim.x - 0.085),
            -(
                self.unit_scaling * 0.017
            ),  # 0.017 is the space above the number in the font
        )  # .085 is the scoreboard arc radius
        screen.blit(left_score, left_score_rect)
        screen.blit(right_score, right_score_rect)

    def win(self, winner, screen):
        # if winner is not False:
        if winner == 0:
            screen.blit(self.win_screen, (0, 0))
        if winner == 1:
            self._win_screen = pygame.transform.flip(self.win_screen, 1, 0)
            screen.blit(self._win_screen, (0, 0))
