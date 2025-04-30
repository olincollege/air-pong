import pygame

from air_pong_view import PongView
from air_pong_controller import PongController
from air_pong_model import PongModel

screen = pygame.display.set_mode((1200, 700))
screen.fill((255, 255, 255))


def main():
    """Run the air-pong game"""

    # intialize MVCC (2 controllers)
    model = PongModel()
    controller1 = PongController(model, 1, "Left")
    controller2 = PongController(model, 2, "Right")
    view = PongView()

    # main loop to run code
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controller1.release()
                controller2.release()
                running = False
        controller1.hand_cv()
        model.trajectory()
        view.display(model, screen)
        pygame.display.flip()

        controller1.get_hand()


if __name__ == "__main__":
    main()
