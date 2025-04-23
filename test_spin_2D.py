import pygame
from air_pong_model import PongModel

background_colour = (255, 255, 255)
UNIT_SCALING = 350
X_SHIFT = -200
Z_SHIFT = 200
colour = (0, 0, 0)
THICKNESS = 1


def display(pong_instance):
    pygame.draw.circle(
        screen,
        colour,
        (
            UNIT_SCALING * pong_instance.ball_position.x + X_SHIFT,
            UNIT_SCALING * pong_instance.ball_position.y + Z_SHIFT,
        ),
        UNIT_SCALING * pong_instance.ball_radius,
        THICKNESS,
    )
    pygame.draw.rect(
        screen,
        (0, 0, 255),
        (
            UNIT_SCALING * pong_instance.table_front + X_SHIFT,
            UNIT_SCALING * pong_instance.table_dim.z + Z_SHIFT,
            UNIT_SCALING * pong_instance.table_dim.x,
            UNIT_SCALING * pong_instance.table_dim.z * 0.02,
        ),
    )
    pygame.draw.rect(
        screen,
        colour,
        (
            UNIT_SCALING
            * (pong_instance.table_front + pong_instance.table_dim.x / 2)
            + X_SHIFT,
            UNIT_SCALING * (pong_instance.table_dim.z)
            - UNIT_SCALING * 0.1525
            + Z_SHIFT,
            UNIT_SCALING * 0.003,  # Width of the net
            UNIT_SCALING * 0.1525,  # Height of the net
        ),
    )
    # pygame.draw.line(
    #     screen,
    #     colour,
    #     (pong_instance._ball_position.x, pong_instance._ball_position.y),
    #     (
    #         (
    #             100000 * pong_instance._mag_force.x
    #             + pong_instance._ball_position.x
    #         ),
    #         (
    #             100000 * pong_instance._mag_force.y
    #             + pong_instance._ball_position.y
    #         ),
    #     ),
    # )


screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Tutorial 5")
particle = PongModel()
# particle.angle = vector.diff_angle(particle.ball_velocity, vector(1, 0, 0))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(background_colour)
    particle.trajectory()
    display(particle)
    pygame.display.flip()
