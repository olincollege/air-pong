"""Main file to run the air-pong game"""

import pygame
from air_pong_view import PongView
from air_pong_controller import PongController
from air_pong_model import PongModel


def main():
    """Run the air-pong game"""

    # intialize MVCC (2 controllers)
    model = PongModel(2, 11)
<<<<<<< HEAD
    controller = PongController(model)
    screen = pygame.display.set_mode((1500, 600))
    view = PongView(screen, model)
    view.prepare_images()
=======
    controller1 = PongController(model)
    view = PongView()
    view.prepare_images(model, screen)
>>>>>>> 75f530476896b0aeb87710744f0a11ef025a49ee

    # main loop to run code
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # pylint: disable=no-member
                controller.release()
                running = False

<<<<<<< HEAD
        controller.update_hand()
=======
        controller1.update_hand()
>>>>>>> 75f530476896b0aeb87710744f0a11ef025a49ee
        model.trajectory()
        view.display()
        if model.check_win() is not False:
            controller.release()
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # pylint: disable=no-member
                        running = False
                view.win(model.check_win())
        pygame.display.flip()


if __name__ == "__main__":
    main()
