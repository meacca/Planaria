from planaria.read_data import parse_file
from planaria.draw_data import calculate_bb
from typing import Tuple
from PIL import Image, ImageDraw


class SkeletonWay:
    def __init__(self, path_to_skeleton_way: str):
        _, _, _, self._skeleton_way = parse_file(path_to_skeleton_way, diagram_type="skeleton_way")
        self.__straight_skeleton_way()

    @staticmethod
    def __compute_line_length(point_1: Tuple[float, float], point_2: Tuple[float, float]):
        return ((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2) ** 0.5

    def __straight_skeleton_way(self):
        cur_x = 0
        self._skeleton_way_straight = [{"point": (0.0, 0.0), "radius": 0.0}]
        for i in range(1, len(self._skeleton_way)):
            cur_node, prev_node = self._skeleton_way[i], self._skeleton_way[i-1]
            edge_length = self.__compute_line_length(cur_node["point"], prev_node["point"])
            cur_x += edge_length
            self._skeleton_way_straight.append({"point": (cur_x, 0.0), "radius": cur_node["radius"]})

    def draw_straight_skeleton_way(self, image_size: Tuple[int, int] = (900, 900),
                                   draw_circles: bool = True) -> Image:
        img = Image.new("RGB", image_size, (255, 255, 255))
        d = ImageDraw.Draw(img)
        y_image = image_size[1] // 2

        for i in range(len(self._skeleton_way_straight) - 1):
            cur_node, next_node = self._skeleton_way_straight[i], self._skeleton_way_straight[i + 1]
            cur_draw_point = (cur_node["point"][0], y_image)
            next_draw_point = (next_node["point"][0], y_image)
            d.line([cur_draw_point, next_draw_point], fill=(256, 0, 0))
            if draw_circles:
                bb = calculate_bb(cur_draw_point, cur_node["radius"])
                d.ellipse(bb, outline=0)
        return img

    def calculate_length(self) -> float:
        return self._skeleton_way_straight[-1]["point"][0]

    def calculate_square(self) -> float:
        square = 0
        for i in range(1, len(self._skeleton_way_straight)):
            prev_node, cur_node = self._skeleton_way_straight[i-1], self._skeleton_way_straight[i]
            prev_x, prev_radius = prev_node["point"][0], prev_node["radius"]
            cur_x, cur_radius = cur_node["point"][0], cur_node["radius"]

            edge_length = cur_x - prev_x
            trapezoid_line = prev_radius + cur_radius

            square += edge_length * trapezoid_line
        return square

    def calculate_mean_radius(self) -> float:
        return self.calculate_square() / 2 / self.calculate_length()