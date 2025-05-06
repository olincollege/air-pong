"""Main file to run the air-pong game"""

import pygame
from air_pong_view import PongView
from air_pong_controller import PongController
from air_pong_model import PongModel


def main():
    """Run the air-pong game"""

    # initialize MVCC (2 controllers)
    model = PongModel(2, 11)
    controller = PongController(model)
    screen = pygame.display.set_mode((1500, 600))
    view = PongView(screen, model)
    view.prepare_images()

    # main loop to run code
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # pylint: disable=no-member
                running = False

        controller.update_hand()
        model.trajectory()
        view.display()
        if model.check_win() is not False:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # pylint: disable=no-member
                        running = False
                view.win(model.check_win())
        pygame.display.flip()


if __name__ == "__main__":
    main()
