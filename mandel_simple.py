import sys
import pygame
from pygame import gfxdraw
from pygame import Color
import cmath

pygame.init()

maxIter = 100
width = 600
height = 400

def draw_mandel(window, sequence_function):
    x_ratio = 3. / width
    y_ratio = 2. / height
    for x in xrange(width):
        for y in xrange(height):
            c = complex((x * x_ratio) - 2, (y * y_ratio) - 1)
            z = c
            for i in xrange(maxIter):
                z = sequence_function(z, c)
                if (z.real * z.real + z.imag * z.imag) > 4:
                    color_ratio = int((i * 255.) / maxIter)
                    gfxdraw.pixel(window, x, y, Color(color_ratio, 0, 0, 255))
                    break
            else:
                gfxdraw.pixel(window, x, y, Color(0,0,0,255))

    pygame.display.flip()
    pygame.image.save(window, 'render.png')

if __name__ == '__main__':
    window = pygame.display.set_mode((width, height))

    draw_mandel(window, lambda z, c: z**2 + c)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
