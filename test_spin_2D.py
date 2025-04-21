import math
from vpython import vector
import pygame
from air_pong_model import PongModel

background_colour = (255, 255, 255)
(width, height) = (1800, 800)


class Particle(PongModel):

    time_step = 0.01
    acc_gravity = vector(0, 9.8, 0)

    def __init__(self, x, y, size):
        super(PongModel, self).__init__()
        self.x = x
        self.y = y
        self.size = size
        self.colour = (0, 0, 0)
        self.thickness = 1
        self.angle = 0

    def display(self):
        pygame.draw.circle(
            screen,
            self.colour,
            (self.x, self.y),
            self.size,
            self.thickness,
        )
        pygame.draw.rect(
            screen,
            (0, 0, 255),
            (width * 0.2, height - (height * 0.1), width * 0.6, height * 0.01),
        )
        pygame.draw.rect(
            screen,
            self.colour,
            (
                width * 0.5,
                height - (height * 0.18),
                width * 0.005,
                height * 0.08,
            ),
        )

    def move(self):
        self.x += (self.ball_velocity * Particle.time_step).x
        self.y += (self.ball_velocity * Particle.time_step).y
        self.ball_velocity += (
            Particle.acc_gravity * Particle.time_step
            + self.compute_magnus_force() / Particle._ball_mass
        )
        self.angle = vector.diff_angle(self.ball_velocity, vector(1, 0, 0))

    def bounce(self):
        if (
            self.x >= width * 0.2 - self.size
            and self.x <= width * 0.8 - self.size
            and self.y >= height - (height * 0.1) - self.size
        ):
            self.ball_velocity = vector.rotate(
                self.ball_velocity,
                angle=-2 * self.angle,
                axis=vector(0, 0, 1),
            )
            # self.y = 2 * self.size - self.y

        elif self.y > height - self.size:
            self.y = 2 * (height - self.size) - self.y
            self.ball_velocity = vector.rotate(
                self.ball_velocity,
                angle=-2 * self.angle,
                axis=vector(0, 0, 1),
            )
        self.angle = vector.diff_angle(self.ball_velocity, vector(1, 0, 0))


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tutorial 5")

number_of_particles = 1
my_particles = []

for n in range(number_of_particles):
    size = 15
    # x = random.randint(size, width - size)
    y = height * 0.7
    x = width * 0.2
    # y = height - size

    particle = Particle(x, y, size)
    particle.ball_velocity = vector(0, 0, 0)
    particle._ball_spin = vector(0, 0, -0.05)

    particle.angle = vector.diff_angle(particle.ball_velocity, vector(1, 0, 0))

    my_particles.append(particle)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_colour)

    for particle in my_particles:
        particle.move()
        particle.bounce()
        particle.display()

    pygame.display.flip()
