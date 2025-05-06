"""View module for the air-pong game"""

import pygame


class PongView:
    """view class for air-pong game

    Attributes:
        pong_instance (PongModel): instance of the PongModel class
        background_colour (tuple): background colour of the screen
        unit_scaling (float): conversion between the model and the screen
        x_shift (float): x shift for the game in meters
        y_shift (float): y shift for the game in meters
        colour (tuple): black color
        screen (pygame.Surface): pygame screen to display the game
        ping_pong_table (pygame.Surface): pygame surface containing the image of the ping pong table
        scoreboard (pygame.Surface): pygame surface containing the image of the scoreboard
        win_screen (pygame.Surface): pygame surface containing the image of the win screen
        score_font (pygame.font.Font): font and size for the score
    """

    def __init__(self, screen, pong_instance):
        """Initialize the PongView class
        Args:
            screen (pygame.Surface): pygame screen to display the game
            pong_instance (PongModel): instance of the PongModel class
        """
        pygame.font.init()  # Initialize pygame fonts
        self.pong_instance = pong_instance
        self.background_colour = (255, 255, 255)  # white background
        self.unit_scaling = 0  # conversion between model and screen, calculated in prepare_images
        self.x_shift = 0.5 * (
            5 - 2.74
        )  # 2.74 is the width of the table, 5 is the width of the screen
        self.y_shift = 2  # 2 is the height of the screen
        self.colour = (0, 0, 0)  # black color
        self.screen = screen  # 5 meter by 2 meter screen
        self.ping_pong_table = pygame.image.load("models/ping_pong_table.png")
        self.scoreboard = pygame.image.load("models/scoreboard.png")
        self.win_screen = pygame.image.load("models/win_screen.png")
        self.score_font = pygame.font.Font("models/monofonto_rg.otf", 0)

    def prepare_images(self):
        """prepare images for the game
        Args:
            pong_instance (PongModel): instance of the PongModel class
        """
        self.unit_scaling = (
            self.screen.get_width() / 5
        )  # 5 is the width of the table in meters
        self.ping_pong_table = pygame.transform.scale(
            self.ping_pong_table,
            (
                self.unit_scaling
                * self.pong_instance.table_dim.x,  # length of the table in meters
                self.unit_scaling
                * self.pong_instance.table_dim.z,  # width of the table in meters
            ),
        )
        self.scoreboard = pygame.transform.scale(
            self.scoreboard,
            (
                self.unit_scaling * self.pong_instance.table_dim.x,
                self.unit_scaling
                * 0.1875,  # height of the scoreboard in meters
            ),
        )
        self.score_font = pygame.font.Font(
            "models/monofonto_rg.otf",
            int(self.unit_scaling * 0.18),  # font size
        )
        self.win_screen = pygame.transform.scale(
            self.win_screen,
            (
                self.unit_scaling * 5,
                self.unit_scaling * 2,
            ),  # win screen fills the entire screen
        )

    def display(self):
        """display the game on the screen
        Args:
            pong_instance (PongModel): instance of the PongModel class
        """
        self.screen.fill(
            (self.background_colour)
        )  # fill the screen with white background
        # Ball
        spin_color = 17 * min(
            self.pong_instance.ball_spin.mag, 15
        )  # spin color, the ball is white at no spin and black at max spin
        pygame.draw.circle(
            self.screen,
            (spin_color, spin_color, spin_color),
            (
                self.unit_scaling * self.pong_instance.ball_position.x,
                self.unit_scaling
                * (self.y_shift - self.pong_instance.ball_position.y),
            ),
            self.unit_scaling * self.pong_instance.ball_radius,
            width=0,
        )
        # Ball outline
        pygame.draw.circle(
            self.screen,
            self.colour,
            (
                self.unit_scaling * self.pong_instance.ball_position.x,
                self.unit_scaling
                * (self.y_shift - self.pong_instance.ball_position.y),
            ),
            self.unit_scaling * self.pong_instance.ball_radius,
            width=1,
        )

        # paddle
        pygame.draw.line(
            self.screen,
            (255, 0, 0),
            (
                self.unit_scaling * self.pong_instance.paddle_edges[0][1][0],
                self.unit_scaling
                * (self.y_shift - self.pong_instance.paddle_edges[0][1][1]),
            ),
            (
                self.unit_scaling * self.pong_instance.paddle_edges[0][0][0],
                self.unit_scaling
                * (self.y_shift - self.pong_instance.paddle_edges[0][0][1]),
            ),
            width=int(self.unit_scaling * self.pong_instance.paddle_dim.z),
        )
        # paddle 2
        pygame.draw.line(
            self.screen,
            (0, 0, 255),
            (
                self.unit_scaling * self.pong_instance.paddle_edges[1][1][0],
                self.unit_scaling
                * (self.y_shift - self.pong_instance.paddle_edges[1][1][1]),
            ),
            (
                self.unit_scaling * self.pong_instance.paddle_edges[1][0][0],
                self.unit_scaling
                * (self.y_shift - self.pong_instance.paddle_edges[1][0][1]),
            ),
            width=int(self.unit_scaling * self.pong_instance.paddle_dim.z),
        )
        # table
        self.screen.blit(
            self.ping_pong_table,
            (
                self.unit_scaling * self.x_shift,
                self.unit_scaling
                * (self.y_shift - self.pong_instance.table_dim.z),
            ),
        )
        # table net
        pygame.draw.rect(
            self.screen,
            self.colour,
            (
                self.unit_scaling
                * (self.x_shift + self.pong_instance.table_dim.x / 2),
                self.unit_scaling
                * (
                    self.y_shift
                    - self.pong_instance.net_height
                    - self.pong_instance.table_dim.z
                ),
                self.unit_scaling * 0.012,  # Width of the net in meters
                self.unit_scaling * self.pong_instance.net_height,
            ),
        )
        # scoreboard
        self.screen.blit(
            self.scoreboard,
            (
                self.unit_scaling * self.x_shift,
                0,
            ),
        )
        pygame.font.init()
        left_score = self.score_font.render(
            f"{self.pong_instance.player_score[0]}", True, (255, 255, 255)
        )
        left_score_rect = left_score.get_rect()
        left_score_rect.topleft = (
            self.unit_scaling
            * (self.x_shift + 0.085),  # .085 is the scoreboard arc radius
            -(
                self.unit_scaling * 0.017
            ),  # 0.017 is the space above the number in the font
        )
        self.screen.blit(left_score, left_score_rect)
        right_score = self.score_font.render(
            f"{self.pong_instance.player_score[1]}", True, (255, 255, 255)
        )
        right_score_rect = left_score.get_rect()
        right_score_rect.topright = (
            self.unit_scaling
            * (
                self.x_shift + self.pong_instance.table_dim.x - 0.085
            ),  # .085 is the scoreboard arc radius
            -(
                self.unit_scaling * 0.017
            ),  # 0.017 is the space above the number in the font
        )
        self.screen.blit(left_score, left_score_rect)
        self.screen.blit(right_score, right_score_rect)

    def win(self, winner):
        """display the win screen
        Args:
            winner (int): 0 for left player, 1 for right player
        """
        if winner == 0:
            self.screen.blit(
                self.win_screen, (0, 0)
            )  # display the win screen, left player wins
        if winner == 1:

            self.screen.blit(
                pygame.transform.flip(self.win_screen, 1, 0), (0, 0)
            )  # flip and display the win screen, right player wins
