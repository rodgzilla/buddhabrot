import math
import sys
import pygame
from pygame import gfxdraw
from pygame import Color
pygame.init()

# maxIter = 500
# width = 1500
# height = 1000

maxIter = 1000
# width = 900
# height = 600

width = 450
height = 300


def draw_mandel():
    screen = [[0] * height for i in range(width)]
    
    for x in range(width):
        for y in range(height):
            c = complex(((x * 3.) / width) - 2, ((y * 2.0) / height) - 1)
            z = c
            complex_sequence = set([])
            for i in range(maxIter):
                complex_sequence.add(z)
                z = z ** 2 + c
                if (z.real * z.real + z.imag * z.imag) > 4:
                    complex_sequence.add(z)
                    for term in complex_sequence:
                        pixel_x = math.floor(((term.real + 2) * width) / 3.)
                        pixel_y = math.floor(((term.imag + 1) * height) / 2.)
                        if 0 <= pixel_x < width and 0 <= pixel_y < height:
                            screen[int(pixel_x)][int(pixel_y)] += 1
                    break

    minimum = screen[0][0]
    maximum = screen[0][0]
    for x in range(width):
        for y in range(height):
            if screen[x][y] < minimum:
                minimum = screen[x][y]
            if screen[x][y] > maximum:
                maximum = screen[x][y]

    for x in range(width):
        for y in range(height):
            color_value = ((screen[x][y] - minimum) * 255) / (maximum - minimum)
            gfxdraw.pixel(window, x, y, Color(color_value, color_value,  color_value, 255))

    print "maximum :", maximum
    print "minimum :", minimum

    print "done !"
    pygame.display.flip()

if __name__ == '__main__':
    window = pygame.display.set_mode((width, height))

    draw_mandel()
    pygame.image.save(window, "rendu_medium.bmp")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
