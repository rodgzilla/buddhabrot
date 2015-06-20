from PIL import Image
import multiprocessing
import math
import sys
import random

sequence_function = lambda z_n, c : z_n ** 2 + c

def decompose_pixel_into_complex_numbers_list(width, height, x, y,
                                              complex_number_by_pixel):
    """This function computes the complex_number_by_pixel ** 2 pixels
    that corresponds to the (x, y) pixel in the complex plane.

    """
    for i in range(complex_number_by_pixel):
        for j in range(complex_number_by_pixel):
            real = (3. * complex_number_by_pixel * x + i) / \
                   (complex_number_by_pixel * width) - 2
            imag = (2. * complex_number_by_pixel * y + j) / \
                   (complex_number_by_pixel * height) - 1
            yield complex(real, imag)

def is_in_cardoid_or_bulb(z):
    """Algorithm for the test:
    https://en.wikipedia.org/wiki/Mandelbrot_set#Optimizations

    """
    p = math.sqrt((z.real - 1. / 4) ** 2 + z.imag ** 2)
    return z.real < p - 2 * (p ** 2) + 1. / 4 and \
        ((z.real + 1) ** 2) + (z.imag ** 2) < 1. / 16

def iterate_over_region(args):
    """Compute the sequences on a given region. args is a 5-tuple composed
    as follows (width, height, min_iter, max_iter,
    complex_number_by_pixel, slice). It returns a 2 dimensionnal array
    of size width * height containing the number of occurences of a
    given pixel in the complex sequences.

    """
    width, height, min_iter, max_iter, complex_number_by_pixel, slice = args
    complex_plane = [[0] * height for _ in range(width)]

    for x, y in slice:
        for c in decompose_pixel_into_complex_numbers_list(width,
                                                           height, x, y, 
                                                           complex_number_by_pixel):
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

    print "Computation from (" + str(slice[0][0]) + ', ' + \
        str(slice[0][1]) + ') to (' + str(slice[-1][0]) + ', ' + \
        str(slice[-1][1]) + ')'
    return complex_plane

def find_black_pixels(image):
    """This function returns the list of the black pixels of a given
    image.

    """
    black_pixels = set()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if image.getpixel((x, y)) == (0, 0, 0, 255):
                black_pixels.add((x, y))

    return list(black_pixels)

def slice_entry_image(width, height, min_iter, max_iter, cpu_number,
                      slice_per_cpu, complex_number_by_pixel, image,
                      sample_percent):
    """This function compute the list of argument tuples that will be used
    to call iterate_over_region. It computes the list of black pixels
    of the input image, slice this list according to its arguments and
    then build the list of argument tuples.

    """
    black_pixels_full = find_black_pixels(image)
    print len(black_pixels_full), "black pixels found on the input image."
    sample_size = int((sample_percent * len(black_pixels_full)) / 100.)
    black_pixels = random.sample(black_pixels_full, sample_size)
    print len(black_pixels), "black pixels selected"
    slice_size = len(black_pixels) / (cpu_number * slice_per_cpu)
    argument_list = []

    print "Beggining of the slicing of the entry image"
    for i in range((cpu_number * slice_per_cpu) - 1):
        slice = black_pixels[i * slice_size:(i + 1) * slice_size]
        argument_list.append((width, height, min_iter, max_iter,
                              complex_number_by_pixel, slice))
    final_slice = black_pixels[i * slice_size:]
    argument_list.append((width, height, min_iter, max_iter,
                          complex_number_by_pixel, final_slice))

    print "Slicing done"
    return argument_list

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
                        slice_per_cpu, complex_number_by_pixel, image,
                        sample_percent):
    """This function uses the other functions to : create the process
    pool, compute the size of the different slices of the screen, use
    Pool.map to compute the orbits of the different complexe sequences
    and then fusion all the results together.

    """
    cpu_number = multiprocessing.cpu_count()
    sliced_image = slice_entry_image(width, height, min_iter,
                                     max_iter, cpu_number,
                                     slice_per_cpu,
                                     complex_number_by_pixel, image,
                                     sample_percent)

    print "Launching computation on", cpu_number, "cores"
    print "The image is decomposed in", len(sliced_image), "sections"
    print complex_number_by_pixel ** 2, \
        "sequences will be computed for each pixel selected"
    process_pool = multiprocessing.Pool(cpu_number)
    res = process_pool.map(iterate_over_region, sliced_image)
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
    img.save('test_bulb_zone_sample.bmp')
    print "Rendering done"

if __name__ == '__main__':
    # Height should be (2/3) * width.
    width = 600
    height = 400
    # The minimal number of iterations is used to remove the noise in
    # the picture.
    min_iter = 100
    max_iter = 1000
    # In order to speed up the computation, we use more slices than
    # the number of cpu. This allows the program to begin new
    # calculation if a slice takes a long time. The memory used by the
    # program is linear in this variable, be careful.
    slice_per_cpu = 6
    # The number of complex number associated to each pixel of the
    # entry image on which the sequence will be iterated. Actually,
    # this is size of the square shape of complex number.
    complex_number_by_pixel = 8
    # Percent of the pixel that will be used to generate the fractal.
    random_sample_percent = 50

    print "Start"
    print "Opening image file"
    filename = sys.argv[1]
    image = Image.open(filename)
    print "Image opened"
    res = iterate_over_screen(width, height, min_iter, max_iter,
                              slice_per_cpu, complex_number_by_pixel,
                              image, random_sample_percent)
    print "All computation done"
    render_picture(width, height, res)
