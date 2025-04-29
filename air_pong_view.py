import pygame
from vpython import vector
from air_pong_model import PongModel


class PongView:
    """view class for air-pong game"""

    def __init__(self):
        self.background_colour = (255, 255, 255)
        self.UNIT_SCALING = 350
        self.X_SHIFT = -200
        self.Z_SHIFT = 200
        self.colour = (0, 0, 0)
        self.THICKNESS = 1
        # self.screen = pygame.display.set_mode((1200, 700))

    def display(self, pong_instance, screen):
        self.screen = screen
        screen.fill((self.background_colour))
        # ball
        pygame.draw.circle(
            screen,
            (
                17 * min(pong_instance.ball_spin.mag, 15),
                17 * min(pong_instance.ball_spin.mag, 15),
                17 * min(pong_instance.ball_spin.mag, 15),
            ),
            (
                self.UNIT_SCALING * pong_instance.ball_position.x
                + self.X_SHIFT,
                self.UNIT_SCALING * pong_instance.ball_position.y
                + self.Z_SHIFT,
            ),
            self.UNIT_SCALING * pong_instance.ball_radius,
            # THICKNESS,
            width=0,
        )
        # table
        pygame.draw.rect(
            screen,
            (0, 0, 255),
            (
                self.UNIT_SCALING * pong_instance.table_front + self.X_SHIFT,
                self.UNIT_SCALING * pong_instance.table_dim.z + self.Z_SHIFT,
                self.UNIT_SCALING * pong_instance.table_dim.x,
                self.UNIT_SCALING * pong_instance.table_dim.z * 0.02,
            ),
        )
        # table net
        pygame.draw.rect(
            screen,
            self.colour,
            (
                self.UNIT_SCALING
                * (pong_instance.table_front + pong_instance.table_dim.x / 2)
                + self.X_SHIFT,
                self.UNIT_SCALING * (pong_instance.table_dim.z)
                - self.UNIT_SCALING * 0.1525
                + self.Z_SHIFT,
                self.UNIT_SCALING * 0.003,  # Width of the net
                self.UNIT_SCALING * 0.1525,  # Height of the net
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
