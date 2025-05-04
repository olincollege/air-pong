import pygame
from vpython import vector
from air_pong_model import PongModel


class PongView:
    """view class for air-pong game"""

    def __init__(self):
        self.background_colour = (255, 255, 255)
        self.unit_scaling = 350
        self.x_shift = -200
        self.z_shift = 600
        self.colour = (0, 0, 0)
        self.thickness = 1
        self.screen = pygame.display.set_mode((1200, 700))
        self.ping_pong_table = pygame.image.load("models/ping_pong_table.png")

    def prepare_table(self, pong_instance):
        self.ping_pong_table = pygame.transform.scale(
            self.ping_pong_table,
            (
                self.unit_scaling * pong_instance.table_dim.x,
                self.unit_scaling * pong_instance.table_dim.z,
            ),
        )

    def display(self, pong_instance, screen):
        self.screen = screen
        screen.fill((self.background_colour))
        # ball
        spin_color = 17 * min(pong_instance.ball_spin.mag, 15)
        pygame.draw.circle(
            screen,
            (spin_color, spin_color, spin_color),
            (
                self.unit_scaling * pong_instance.ball_position.x
                + self.x_shift,
                -self.unit_scaling * pong_instance.ball_position.y
                + self.z_shift,
            ),
            self.unit_scaling * pong_instance.ball_radius,
            # THICKNESS,
            width=0,
        )
        # ball outline
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (
                self.unit_scaling * pong_instance.ball_position.x
                + self.x_shift,
                -self.unit_scaling * pong_instance.ball_position.y
                + self.z_shift,
            ),
            self.unit_scaling * pong_instance.ball_radius,
            # THICKNESS,
            width=1,
        )
        # paddle
        pygame.draw.polygon(
            screen,
            (255, 0, 0),
            (
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][0]
                    + self.x_shift,
                    -self.unit_scaling * pong_instance.paddle_edges[0][1]
                    + self.z_shift,
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[1][0]
                    + self.x_shift,
                    -self.unit_scaling * pong_instance.paddle_edges[0][1]
                    + self.z_shift,
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[0][0]
                    + self.x_shift,
                    -self.unit_scaling * pong_instance.paddle_edges[0][1]
                    + self.z_shift,
                ),
                (
                    self.unit_scaling * pong_instance.paddle_edges[1][0]
                    + self.x_shift,
                    -self.unit_scaling * pong_instance.paddle_edges[1][1]
                    + self.z_shift,
                ),
            ),
        )
        screen.blit(
            self.ping_pong_table,
            (
                self.unit_scaling * pong_instance.table_front + self.x_shift,
                -self.unit_scaling * pong_instance.table_dim.z + self.z_shift,
            ),
        )
        # table net
        pygame.draw.rect(
            screen,
            self.colour,
            (
                self.unit_scaling
                * (pong_instance.table_front + pong_instance.table_dim.x / 2)
                + self.x_shift,
                -self.unit_scaling * (pong_instance.table_dim.z)
                - self.unit_scaling * 0.1525
                + self.z_shift,
                self.unit_scaling * 0.003,  # Width of the net
                self.unit_scaling * 0.1525,  # Height of the net
            ),
        )
