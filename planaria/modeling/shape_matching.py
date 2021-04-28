from planaria.preprocessing import SkeletonWay


def node_constructor(x, y, radius):
    return {"point": (x, y), "radius": radius}


def skeleton_constructor(x_list, y_list, radius_list):
    skeleton = []
    for x, y, radius in zip(x_list, y_list, radius_list):
        skeleton.append(node_constructor(x, y, radius))
    return skeleton


def unite_shapes(shape_1, shape_2):
    shape_1_unite, shape_2_unite = [], []
    pointer_1, pointer_2 = 0, 0
    while (pointer_1 < len(shape_1)) and (pointer_2 < len(shape_2)):
        x_1, x_2 = shape_1[pointer_1]["point"][0], shape_2[pointer_2]["point"][0]
        rad_1, rad_2 = shape_1[pointer_1]["radius"], shape_2[pointer_2]["radius"]
        if x_1 == x_2:
            shape_1_unite.append(node_constructor(x_1, 0, rad_1))
            shape_2_unite.append(node_constructor(x_2, 0, rad_2))
            pointer_1 += 1
            pointer_2 += 1
        if x_1 < x_2:
            shape_1_unite.append(node_constructor(x_1, 0, rad_1))
            rad_2_left = shape_2[pointer_2 - 1]["radius"]
            x_2_left = shape_2[pointer_2 - 1]["point"][0]
            koef = (x_1 - x_2_left) / (x_2 - x_2_left)
            rad_2_new = koef * (rad_2 - rad_2_left) + rad_2_left
            shape_2_unite.append(node_constructor(x_1, 0, rad_2_new))
            pointer_1 += 1
        if x_2 < x_1:
            shape_2_unite.append(node_constructor(x_2, 0, rad_2))
            rad_1_left = shape_1[pointer_1 - 1]["radius"]
            x_1_left = shape_1[pointer_1 - 1]["point"][0]
            koef = (x_2 - x_1_left) / (x_1 - x_1_left)
            rad_1_new = koef * (rad_1 - rad_1_left) + rad_1_left
            shape_1_unite.append(node_constructor(x_2, 0, rad_1_new))
            pointer_2 += 1
    while pointer_1 < len(shape_1):
        x_1, rad_1 = shape_1[pointer_1]["point"][0], shape_1[pointer_1]["radius"]
        shape_1_unite.append(node_constructor(x_1, 0, rad_1))
        shape_2_unite.append(node_constructor(x_1, 0, 0))
        pointer_1 += 1
    while pointer_2 < len(shape_2):
        x_2, rad_2 = shape_2[pointer_2]["point"][0], shape_2[pointer_2]["radius"]
        shape_1_unite.append(node_constructor(x_2, 0, rad_2))
        shape_2_unite.append(node_constructor(x_2, 0, 0))
        pointer_2 += 1
    return shape_1_unite, shape_2_unite


def calculate_diff_integral(k_1, k_2, a_1, a_2, a, b):
    k = k_1 - k_2
    a_lin = a_1 - a_2

    def linear(x):
        return k * x + a_lin
    if k == 0:
        if a_lin > 0:
            return (b - a) * a_lin
        return 0
    x_inter = -a_lin / k
    if (x_inter <= a) or (x_inter >= b):
        t = linear((a + b) / 2)
        if t > 0:
            return (b - a) * t
        return 0
    if linear((x_inter + a) / 2) > 0:
        left_edge, right_edge = a, x_inter
    else:
        left_edge, right_edge = x_inter, b
    return (right_edge - left_edge) * linear((left_edge + right_edge) / 2)


def calculate_symmetric_integral(k_1, k_2, a_1, a_2, a, b):
    return (calculate_diff_integral(k_1, k_2, a_1, a_2, a, b) + calculate_diff_integral(k_2, k_1, a_2, a_1, a, b)) * 2


def calculate_symmetric_diff_part(node_left_1, node_left_2, node_right_1, node_right_2):
    x_1_left, x_1_right = node_left_1["point"][0], node_right_1["point"][0]
    y_1_left, y_1_right = node_left_1["radius"], node_right_1["radius"]
    x_2_left, x_2_right = node_left_2["point"][0], node_right_2["point"][0]
    y_2_left, y_2_right = node_left_2["radius"], node_right_2["radius"]

    k_1 = (y_1_right - y_1_left) / (x_1_right - x_1_left)
    a_1 = ((x_1_right * y_1_left) - (x_1_left * y_1_right)) / (x_1_right - x_1_left)
    k_2 = (y_2_right - y_2_left) / (x_2_right - x_2_left)
    a_2 = ((x_2_right * y_2_left) - (x_2_left * y_2_right)) / (x_2_right - x_2_left)

    return calculate_symmetric_integral(k_1, k_2, a_1, a_2, a=x_1_left, b=x_1_right)


class ShapeMatcher:
    def __init__(self):
        pass

    @staticmethod
    def calculate_symmetric_diff_square(skeleton_1: SkeletonWay, skeleton_2: SkeletonWay):
        shape_1, shape_2 = skeleton_1.get_straight_skeleton(), skeleton_2.get_straight_skeleton()
        shape_1_unite, shape_2_unite = unite_shapes(shape_1, shape_2)
        res = 0
        for i in range(len(shape_1_unite) - 1):
            diff_part = calculate_symmetric_diff_part(shape_1_unite[i], shape_2_unite[i],
                                                      shape_1_unite[i + 1], shape_2_unite[i + 1])
            res += diff_part
        return res

    def get_shapes_diff_features(self, skeleton_1: SkeletonWay, skeleton_2: SkeletonWay):
        res = dict()
        symmetric_diff = self.calculate_symmetric_diff_square(skeleton_1, skeleton_2)
        res["absolute_diff"] = symmetric_diff
        skeleton_1_square, skeleton_2_square = skeleton_1.calculate_square(), skeleton_2.calculate_square()
        union_square = (skeleton_1_square + skeleton_2_square - symmetric_diff) / 2
        relative_symmetric_diff = symmetric_diff / (union_square + symmetric_diff)
        res["relative_diff"] = relative_symmetric_diff
        return res

