import pygame
from vpython import vector
from air_pong_model import PongModel


class PongView:
    """view class for air-pong game"""

    def __init__(self):
        self.background_colour = (255, 255, 255)
        self.unit_scaling = 350
        self.x_shift = -200
        self.z_shift = 200
        self.colour = (0, 0, 0)
        self.thickness = 1
        self.screen = pygame.display.set_mode((1200, 700))

    def display(self, pong_instance, screen):
        self.screen = screen
        screen.fill((self.background_colour))
        # paddle
        # pygame.draw.rect(
        #     screen,
        #     (255, 0, 0),
        #     (
        #         self.unit_scaling * pong_instance._paddle_edges[0].x
        #         + self.x_shift,
        #         self.unit_scaling * pong_instance._paddle_edges[0].y
        #         + self.z_shift,
        #         self.unit_scaling * 0.016,
        #         self.unit_scaling * pong_instance._paddle_width,
        #     ),
        # )
        # ball
        pygame.draw.circle(
            screen,
            (
                17 * min(pong_instance.ball_spin.mag, 15),
                17 * min(pong_instance.ball_spin.mag, 15),
                17 * min(pong_instance.ball_spin.mag, 15),
            ),
            (
                self.unit_scaling * pong_instance.ball_position.x
                + self.x_shift,
                self.unit_scaling * pong_instance.ball_position.y
                + self.z_shift,
            ),
            self.unit_scaling * pong_instance.ball_radius,
            # THICKNESS,
            width=0,
        )
        # table
        ping_pong_table = pygame.image.load("models/ping_pong_table.png")
        ping_pong_table = pygame.transform.scale(
            ping_pong_table,
            (
                self.unit_scaling * pong_instance.table_dim.x,
                self.unit_scaling * pong_instance.table_dim.z,
            ),
        )
        screen.blit(
            ping_pong_table,
            (
                self.unit_scaling * pong_instance.table_front + self.x_shift,
                self.unit_scaling * pong_instance.table_dim.z + self.z_shift,
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
                self.unit_scaling * (pong_instance.table_dim.z)
                - self.unit_scaling * 0.1525
                + self.z_shift,
                self.unit_scaling * 0.003,  # Width of the net
                self.unit_scaling * 0.1525,  # Height of the net
            ),
        )

        # pygame.draw.line(
        #     screen,
        #     colour,
        #     (pong_instance.ball_position.x, pong_instance.ball_position.y),
        #     (pong_instance._ball_spin.x, pong_instance._ball_spin.y),
        #     #     (pong_instance.ball_position.x, pong_instance.ball_position.y),
        #     #     (
        #     #         (
        #     #             100000 * pong_instance._mag_force.x
        #     #             + pong_instance.ball_position.x
        #     #         ),
        #     #         (
        #     #             100000 * pong_instance._mag_force.y
        #     #             + pong_instance.ball_position.y
        #     #         ),
        #     #     ),
        # )

    # def render(self):
    #     pygame.display.set_caption("Tutorial 5")
    #     particle = PongModel()
    #     # particle.angle = vector.diff_angle(particle.ball_velocity, vector(1, 0, 0))

    #     running = True
    #     while running:
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 running = False
    #         self.screen.fill(self.background_colour)
    #         particle.trajectory()
    #         PongView.display(self, particle)
    #         print(particle.ball_spin.mag)
    #         pygame.display.flip()
