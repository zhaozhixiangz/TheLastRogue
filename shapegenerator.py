import random
import math
import rng
import direction
import geometry as geo


def dfs_tunnler(start_position, min_length, max_length,
                size, direction_list):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    visited = set()
    while len(visited) < size:
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        visited.add(position)
        for _ in range(length):
            if(len(visited) >= size):
                break
            position = geo.add_2d(position, direction_)
            visited.add(position)
    return visited


def dfs_tunnler_with_random_stop(start_position, min_length, max_length,
                                 size, direction_list):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    visited = set()
    while len(visited) < size:
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        visited.add(position)
        for _ in range(length):
            if(len(visited) >= size):
                break
            position = geo.add_2d(position, direction_)
            visited.add(position)
        if(rng.coin_flip()):
            position = random.sample(visited, 1)[0]
    return visited


def dfs_tunnler_with_random_restart(start_position, min_length, max_length,
                                    size, direction_list):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    visited = set()
    while len(visited) < size:
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        visited.add(position)
        for _ in range(length):
            if(len(visited) >= size):
                break
            position = geo.add_2d(position, direction_)
            visited.add(position)
        if(rng.coin_flip()):
            position = start_position
    return visited


def random_exlosion(start_pos, size, move_list=None):
    if move_list is None:
        move_list = direction.DIRECTIONS
    position = start_pos
    visited = set()
    unvisited_positions = set()
    while len(visited) < size:
        visited.add(position)
        neighbors = set([geo.add_2d(position, _direction)
                         for _direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if(len(unvisited_positions) >= 1):
            position = random.sample(unvisited_positions, 1)[0]
        else:
            break
    return visited


def triangle_points(distance, width, height):
    triangle_height = math.sqrt(3.0 / 4.0) * distance
    triangle_width = float(distance)
    points = []
    for x in range(width):
        for y in range(height):
            x_shift = 0 if y % 2 == 0 else triangle_width / 2.0
            point = (int(x * triangle_width + x_shift),
                     int(y * triangle_height))
            points.append(point)
    return points


def manhattan_walker(start_point, end_point):
    return _manhattan_walker_recursive(start_point, end_point, set())


def _manhattan_walker_recursive(start_point, end_point, points):
    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]

    start_x = start_point[0]
    start_y = start_point[1]

    if(delta_x == 0):
        step = 1 if delta_y >= 0 else -1
        for y in range(start_y, int(delta_y) + start_y, step):
            points.add((start_x, y))
        return points
    elif(delta_y == 0):
        step = 1 if delta_x >= 0 else -1
        for x in range(start_x, int(delta_x) + start_x, step):
            points.add((x, start_y))
        return points

    if abs(delta_x) > abs(delta_y):
        x_step = int(float(delta_x) / abs(float(delta_y)))
        mini_step = 1 if x_step >= 0 else -1
        for x in range(start_x, start_x + x_step + mini_step, mini_step):
            points.add((x, start_y))
        y_step = 1 if delta_y >= 0 else -1
    else:
        y_step = int(float(delta_y) / abs(float(delta_x)))
        mini_step = 1 if y_step >= 0 else -1
        for y in range(start_y, start_y + y_step + mini_step, mini_step):
            points.add((start_x, y))
        x_step = 1 if delta_x >= 0 else -1
    new_start_point = (start_x + x_step, start_y + y_step)
    return _manhattan_walker_recursive(new_start_point, end_point, points)


class Shape(object):
    def __init__(self, points):
        self._points = set(points)

    @property
    def points(self):
        return self._points

    def calc_rect(self):
        sample_point = random.sample(self.points, 1)[0]
        left = sample_point[0]
        right = sample_point[0]
        up = sample_point[1]
        down = sample_point[1]

        for point in self.points:
            left = min(point[0], left)
            right = max(point[0], right)
            up = min(point[1], up)
            down = max(point[1], down)
        return geo.Rect((left, up), right - left, down - up)

    def calc_normalized_points(self, offset=0):
        rect = self.calc_rect()
        normalized = set()
        for point in self.points:
            normalized.add((point[0] - rect.left + offset,
                            point[1] - rect.top + offset))
        return normalized