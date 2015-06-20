import sys
import pygame
from pygame import gfxdraw
from pygame import Color
import cmath

pygame.init()

maxIter = 100
width = 1800
height = 1200

def draw_mandel(window, sequence_function, width, height, max_iter,
                threshold):
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
                    if color_ratio >= threshold:
                        gfxdraw.pixel(window, x, y, Color(0, 0, 0, 255))
                    else:
                        gfxdraw.pixel(window, x, y, Color(255, 255, 255, 255))
                    break
            else:
                gfxdraw.pixel(window, x, y, Color(255,255,255,255))

    pygame.display.flip()
    pygame.image.save(window, 'render_border.png')

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "width, height, max_iter, threshold"
        sys.exit(1)

    width, height, max_iter, threshold = [int(x) for x in sys.argv[1:]]
    window = pygame.display.set_mode((width, height))

    draw_mandel(window, lambda z, c: z**2 + c, width, height,
                max_iter, threshold)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
