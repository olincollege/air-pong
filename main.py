import pygame
from vpython import vector

from air_pong_view import PongView
from air_pong_controller import PongController
from air_pong_model import PongModel

screen = pygame.display.set_mode((1200, 700))
screen.fill((255, 255, 255))


def main():
    """Run the air-pong game"""

    # intialize MVCC (2 controllers)
    model = PongModel(2, 11)
    controller1 = PongController(model, 1, "Left")
    controller2 = PongController(model, 2, "Right")
    view = PongView()
    view.prepare_images(model, screen)

    # main loop to run code
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controller1.release()
                controller2.release()
                running = False

        controller1.update_hand()
        controller2.update_hand()
        model.trajectory()
        view.display(model, screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
