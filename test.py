import pygame
import random
import math

background_colour = (255, 255, 255)
(width, height) = (1800, 800)


class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.colour = (0, 0, 0)
        self.thickness = 1
        self.speed = 0
        self.angle = 0

    def display(self):
        pygame.draw.circle(
            screen,
            self.colour,
            (int(self.x), int(self.y)),
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
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def bounce(self):
        if (
            self.x >= width * 0.2 - self.size
            and self.x <= width * 0.8 - self.size
            and self.y >= height - (height * 0.1) - self.size
        ):
            self.angle = -self.angle
            self.y = 2 * self.size - self.y

        if self.x > width - self.size:
            self.x = 2 * (width - self.size) - self.x
            self.angle = -self.angle

        elif self.x < self.size:
            self.x = 2 * self.size - self.x
            self.angle = -self.angle

        if self.y > height - self.size:
            self.y = 2 * (height - self.size) - self.y
            self.angle = math.pi - self.angle

        elif self.y < self.size:
            self.y = 2 * self.size - self.y
            self.angle = math.pi - self.angle


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tutorial 5")

number_of_particles = 1
my_particles = []

for n in range(number_of_particles):
    size = 15
    # x = random.randint(size, width - size)
    y = random.randint(size, height - size)
    x = width * 0.2
    # y = height - size

    particle = Particle(x, y, size)
    particle.speed = 0.5
    # particle.angle = random.uniform(0, math.pi * 2)
    particle.angle = 200 * (math.pi / 180)

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
