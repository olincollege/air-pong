from air_pong_view import PongView

# from air_pong_controller import PongController
from air_pong_model import PongModel
import pygame

screen = pygame.display.set_mode((1200, 700))
screen.fill((255, 255, 255))


def draw():
    pygame.draw.rect(
        screen,
        (0, 0, 255),
        (700 * 0.2, 1200 - (1200 * 0.1), 700 * 0.6, 1200 * 0.01),
    )


def main():
    # particle = PongModel()
    # view = PongView()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw()
        # particle.trajectory()
        # view.display(particle, screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
