from PIL import Image, ImageDraw
from .read_data import parse_file
import matplotlib.pyplot as plt


def draw_voronoi(voronoi_path: str, image_size: tuple = (900, 900)):
    polygons, edges = parse_file(voronoi_path, diagram_type="voronoi")
    img = Image.new("RGB", image_size, (255, 255, 255))
    d = ImageDraw.Draw(img)
    for polygon in polygons:
        d.polygon(polygon, outline=(0, 0, 0))
    for edge in edges:
        d.line([edge["first_point"], edge["second_point"]], fill=(256, 0, 0))
    return img


def calculate_bb(point: tuple, radius: float):
    left_upper_point = (point[0] - radius, point[1] - radius)
    right_upper_point = (point[0] + radius, point[1] + radius)
    return [left_upper_point, right_upper_point]


def draw_skeleton(skeleton_path: str, image_size: tuple = (900, 900), draw_circles: bool = False):
    polygons, edges, nodes = parse_file(skeleton_path, diagram_type="skeleton")
    img = Image.new("RGB", image_size, (255, 255, 255))
    d = ImageDraw.Draw(img)
    for polygon in polygons:
        d.polygon(polygon, outline=(0, 0, 0))
    for edge in edges:
        d.line([edge["first_point"], edge["second_point"]], fill=(256, 0, 0))
    if draw_circles:
        for node in nodes:
            bb = calculate_bb(node["point"], node["radius"])
            d.ellipse(bb, outline=0)
    return img


def add_extra_edges(cut_skeleton_path: str, extra_skeleton_path: str):
    img = draw_diagram(cut_skeleton_path, diagram_type="skeleton")
    count_terminals, parsed_nodes, parsed_edges = parse_file(extra_skeleton_path, diagram_type="skeleton_way")
    if len(parsed_edges) == 0:
        return img
    d = ImageDraw.Draw(img)
    for edge in parsed_edges:
        d.line([edge["first_point"], edge["second_point"]], fill=(256, 0, 0))
    return img


def draw_diagram(diagram_path: str, image_size: tuple = (900, 900), diagram_type: str = "voronoi",
                 draw_circles: bool = False):
    assert diagram_type in ["voronoi", "skeleton"]
    if diagram_type == "voronoi":
        img = draw_voronoi(voronoi_path=diagram_path, image_size=image_size)
    else:
        img = draw_skeleton(skeleton_path=diagram_path, image_size=image_size, draw_circles=draw_circles)
    return img


def plot_3_images(voronoi: Image.Image, skeleton: Image.Image, skeleton_cut: Image.Image,
                  figure_size: tuple = (18, 6)):
    plt.subplots(1, 3, figsize=figure_size)
    plt.subplot(1, 3, 1)
    plt.imshow(voronoi)
    plt.axis("off")
    plt.subplot(1, 3, 2)
    plt.imshow(skeleton)
    plt.axis("off")
    plt.subplot(1, 3, 3)
    plt.imshow(skeleton_cut)
    plt.axis("off")
    return plt


def plot_3_diagrams(voronoi_path: str, skeleton_path: str, skeleton_cut_path: str,
                    image_size: tuple = (900, 900), figure_size: tuple = (18, 6),
                    draw_circles: tuple = (False, False)):
    voronoi = draw_diagram(diagram_path=voronoi_path, image_size=image_size,
                           diagram_type="voronoi")
    skeleton = draw_diagram(diagram_path=skeleton_path, image_size=image_size,
                            diagram_type="skeleton", draw_circles=draw_circles[0])
    skeleton_cut = draw_diagram(diagram_path=skeleton_cut_path, image_size=image_size,
                                diagram_type="skeleton", draw_circles=draw_circles[1])
    plot = plot_3_images(voronoi=voronoi, skeleton=skeleton, skeleton_cut=skeleton_cut,
                         figure_size=figure_size)
    return plot
