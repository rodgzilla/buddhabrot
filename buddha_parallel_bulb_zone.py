from PIL import Image
import multiprocessing
import math

sequence_function = lambda z_n, c : z_n ** 2 + c

def is_in_cardoid_or_bulb(z):
    """Algorithm for the test:
    https://en.wikipedia.org/wiki/Mandelbrot_set#Optimizations

    """
    p = math.sqrt((z.real - 1. / 4) ** 2 + z.imag ** 2)
    return z.real < p - 2 * (p ** 2) + 1. / 4 and \
        ((z.real + 1) ** 2) + (z.imag ** 2) < 1. / 16

# def iterate_over_region(width, height, min_x, max_x, min_y, max_y):
def iterate_over_region(args):
    """Compute the sequences on a given region. args is a 6-tuple composed
    as follows (width, height, min_iter, max_iter, min_x, max_x,
    min_y, max_y).  It returns a 2 dimensionnal array of size width *
    height containing the number of occurences of a given pixel in the
    complex sequences.

    """
    width, height, min_iter, max_iter, min_x, max_x, min_y, max_y = args
    complex_plane = [[0] * height for _ in range(width)]

    # For each pixel of the screen:
    for x in xrange(min_x, max_x):
        for y in xrange(min_y, max_y):
            # Compute the corresponding complex number.
            c = complex(((x * 3.) / width) - 2, ((y * 2.0) / height) - 1)
            # We check if p is in the cardoid or the bulb (which means
            # that it automatically belongs to the mandelbrot set.
            if is_in_cardoid_or_bulb(c):
                continue
            z = c
            # Creation of the set of complex number that we will use
            # to remember de complex number sequence.
            complex_sequence = set([])
            # Compute at most max_iter terms of the complex number
            # sequence
            for i in xrange(max_iter):
                complex_sequence.add(z)
                z = sequence_function(z, c)
                # If |z| > 2, we are sure that the sequence diverges.
                if (z.real * z.real + z.imag * z.imag) > 4:
                    if len(complex_sequence) <= min_iter:
                        break
                    complex_sequence.add(z)
                    # For each diverging sequence, we increment the
                    # counter corresponding to the pixel of the screen
                    # through which it passed.
                    for term in complex_sequence:
                        pixel_x = math.floor(((term.real + 2) * width) / 3.)
                        pixel_y = math.floor(((term.imag + 1) * height) / 2.)
                        if 0 <= pixel_x < width and 0 <= pixel_y < height:
                            complex_plane[int(pixel_x)][int(pixel_y)] += 1
                    break

    print "Computation for x in [", min_x, ",", max_x, "] DONE"
    return complex_plane

def slice_screen(width, height, min_iter, max_iter, cpu_number,
                 slice_per_cpu):
    """We cut the screen in cpu_number slices of width (width /
    cpu_number). If the number of cpu does not divide the width, the
    last slices will contain the remaining pixels

    """
    screen_sections = []
    slice_size = width / (cpu_number * slice_per_cpu)

    for i in range((cpu_number * slice_per_cpu) - 1):
        screen_sections.append((width, height, min_iter, max_iter, i *
                                slice_size, (i + 1) * slice_size, 0, height))
    screen_sections.append((width, height, min_iter, max_iter, i *
                            slice_size, width, 0, height))
    return screen_sections

def fusion_results(width, height, results):
    """After the computation, we have to add the results of every
    different slice to get the final array.

    """
    final_result = [[0] * height for _ in range(width)]

    for x in xrange(width):
        for y in xrange(height):
            final_result[x][y] = sum((slice[x][y] for slice in results))

    return final_result

def iterate_over_screen(width, height, min_iter, max_iter,
                        slice_per_cpu):
    """This function uses the other functions to : create the process
    pool, compute the size of the different slices of the screen, use
    Pool.map to compute the orbits of the different complexe sequences
    and then fusion all the results together.

    """
    cpu_number = multiprocessing.cpu_count()
    print "Launching computation on", cpu_number, "cores"
    sliced_screen = slice_screen(width, height, min_iter, max_iter,
                                 cpu_number, slice_per_cpu)
    print "The screen is decomposed in", len(sliced_screen), "sections"
    process_pool = multiprocessing.Pool(cpu_number)
    res = process_pool.map(iterate_over_region, sliced_screen)
    process_pool.close()
    process_pool.join()
    final_result = fusion_results(width, height, res)

    return final_result

def render_picture(width, height, result):
    """This function renders the final picture and save it to
    'test.bmp'. To render the picture, the function computes the
    minimum and maximum values of the cells, the scale the range of
    values to the interval [0, 255]. The final picture is rendered
    using this value as a red component.

    """
    minimum = result[0][0]
    maximum = result[0][0]

    print "Starting rendering"
    print "The image size is", width, "x", height
    for x in range(width):
        for y in range(height):
            if result[x][y] < minimum:
                minimum = result[x][y]
            if result[x][y] > maximum:
                maximum = result[x][y]

    img = Image.new('RGB', (width, height))
    img.putdata([(((result[x][y] - minimum) * 255) / (maximum-minimum), 0, 0) \
                 for y in range(height) for x in range(width)])
    img.save('test_bulb.bmp')
    print "Rendering done"

if __name__ == '__main__':
    # Height should be (2/3) * width.
    width = 300
    height = 200
    # The minimal number of iterations is used to remove the noise in
    # the picture.
    min_iter = 300
    max_iter = 3000
    # In order to speed up the computation, we use more slices than
    # the number of cpu. This allows the program to begin new
    # calculation if a slice takes a long time. The memory used by the
    # program is linear in this variable, be careful.
    slice_per_cpu = 5

    print "start"
    res = iterate_over_screen(width, height, min_iter, max_iter, slice_per_cpu)
    print "All computation done"
    render_picture_bis(width, height, res)
