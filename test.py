import random
import polygons as poly
import sys
import math
from pytest import approx


def test_contains():
    num_points = 1000

    context = poly.new_context(0)

    poly.add_polygon(context, [(2.0, 1.0), (3.0, 1.5), (2.5, 2.0), (2.0, 1.0)], list(range(0, 4)), [1.0]*4)
    poly.add_polygon(context, [(0.0, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.0)], list(range(4, 8)), [1.0]*4)
    poly.add_polygon(context, [(0.0, 2.0), (1.0, 2.5), (0.5, 3.0), (0.0, 2.0)], list(range(7, 12)), [1.0]*4)

    random.seed(0)
    points = [(random.uniform(0.0, 3.0), random.uniform(0.0, 3.0)) for _ in range(num_points)]

    result = poly.contains_points(context, points)

    checksum = sum(i for i in range(num_points) if result[i])
    assert checksum == 63726

    poly.free_context(context)


def length_squared(x, y):
    return x * x + y * y


def dsegment(point, vertex1, vertex2):
    v = (vertex2[0] - vertex1[0], vertex2[1] - vertex1[1])
    w = (point[0] - vertex1[0], point[1] - vertex1[1])
    c1 = v[0] * w[0] + v[1] * w[1]

    if (c1 <= 0.0):
        return length_squared(point[0] - vertex1[0], point[1] - vertex1[1])

    c2 = v[0] * v[0] + v[1] * v[1]

    if (c1 >= c2):
        return length_squared(point[0] - vertex2[0], point[1] - vertex2[1])
    else:
        return length_squared(point[0] - (vertex1[0] + c1 / c2 * v[0]),
                              point[1] - (vertex1[1] + c1 / c2 * v[1]))


def vdsegment(points, polygons):
    huge = sys.float_info.max
    distances = []
    for point in points:
        d = huge
        for polygon in polygons:
            for i in range(len(polygon) - 1):
                _d = dsegment(point, polygon[i], polygon[i+1])
                d = min(d, _d)
        distances.append(math.sqrt(d))
    return distances


def get_distances_vertex_naive(points, polygons):
    huge = sys.float_info.max
    indices = []
    distances = []
    for point in points:
        d = huge
        index = -1
        i = 0
        for polygon in polygons:
            for vertex in polygon:
                _d = length_squared(point[0] - vertex[0], point[1] - vertex[1])
                if _d < d:
                    d = _d
                    index = i
                i += 1
        distances.append(math.sqrt(d))
        indices.append(index)
    return indices, distances


def read_polygon(file_name, xshift, yshift):
    vertices = []
    with open(file_name, 'r') as f:
        for line in f:
            x = float(line.split()[0]) + xshift
            y = float(line.split()[1]) + yshift
            vertices.append((x, y))
    return vertices


def init_bounds():
    large = sys.float_info.max
    bounds = [[large, -large],
              [large, -large]]
    return bounds


def adjust_bounds(bounds, point):
    (x, y) = point
    return [[min(bounds[0][0], x),
             max(bounds[0][1], x)],
            [min(bounds[1][0], y),
             max(bounds[1][1], y)]]


def generate_random_points(num_points, bounds):
    random.seed(1)
    points = [(random.uniform(bounds[0][0], bounds[0][1]),
               random.uniform(bounds[1][0], bounds[1][1])) for _ in range(num_points)]
    return points


def g_function(distance):
    scale_factor = 0.995792
    return scale_factor * distance


def h_function(coefficients):
    return coefficients[0] + coefficients[1]


def get_distances_vertex_custom_naive(points, polygons, coefficients, num_coefficients_per_point):
    huge = sys.float_info.max
    distances = []
    for k, point in enumerate(points):
        r = huge
        for i, polygon in enumerate(polygons):
            for j, vertex in enumerate(polygon):
                _d = math.sqrt(length_squared(point[0] - vertex[0], point[1] - vertex[1]))
                h_coefficients = coefficients[i][j*num_coefficients_per_point:j*num_coefficients_per_point + num_coefficients_per_point]
                _r = g_function(_d) + h_function(h_coefficients)
                r = min(r, _r)
        distances.append(r)
    return distances


def test_distances():
    num_points = 1000
    num_polygons = 5

    num_coefficients_per_point = 2
    context = poly.new_context(num_coefficients_per_point)

    random.seed(0)

    polygons = []
    polygons_coefficients = []
    index_offset = 0
    for i in range(num_polygons):
        vertices = read_polygon('data/polygon.txt', xshift=float(i) * 5.0, yshift=float(i) * 5.0)
        polygons.append(vertices)

        coefficients = [random.uniform(0.0, 1.0) for _ in range(num_coefficients_per_point*len(vertices))]

        indices = list(range(index_offset, index_offset + len(vertices)))
        index_offset += len(vertices)
        poly.add_polygon(context, vertices, indices, coefficients)
        polygons_coefficients.append(coefficients)

    bounds = init_bounds()
    for polygon in polygons:
        for point in polygon:
            bounds = adjust_bounds(bounds, point)

    points = generate_random_points(num_points, bounds)

    distances = poly.get_distances_edge(context, points)
    distances_naive = vdsegment(points, polygons)
    for i, point in enumerate(points):
        assert distances[i] == approx(distances_naive[i])

    distances = poly.get_distances_vertex(context, points)
    closest_indices_naive, distances_naive = get_distances_vertex_naive(points, polygons)
    for i, point in enumerate(points):
        assert distances[i] == approx(distances_naive[i])

    closest_indices = poly.get_closest_vertices(context, points)
    assert closest_indices_naive == closest_indices

    distances = poly.get_distances_vertex_custom(context, points)
    distances_naive = get_distances_vertex_custom_naive(points, polygons, polygons_coefficients, num_coefficients_per_point)
    for i, point in enumerate(points):
        assert distances[i] == approx(distances_naive[i])

    poly.free_context(context)
