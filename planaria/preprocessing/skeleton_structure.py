from PIL import Image, ImageDraw
from .read_data import parse_file
from .draw_data import calculate_bb
from typing import Tuple


class SkeletonNode:
    def __init__(self, node_id: int, point: Tuple[int, int], radius: float):
        self.node_id = node_id
        self.point = point
        self.radius = radius
        self.connected_edges = []

    def is_terminal(self) -> bool:
        return len(self.connected_edges) == 1

    def add_edge(self, edge):
        self.connected_edges.append(edge)

    def remove_edge(self, del_edge):
        for i, edge in enumerate(self.connected_edges):
            if edge == del_edge:
                self.connected_edges.pop(i)


class SkeletonEdge:
    def __init__(self, first_node_id: int, second_node_id: int):
        self.first_node_id = first_node_id
        self.second_node_id = second_node_id


class Skeleton:
    def __init__(self, skeleton_file: str):
        self.skeleton_file = skeleton_file
        polygons, edges, nodes = parse_file(skeleton_file, diagram_type="skeleton_structure")
        self.polygons = polygons
        self.edges = []
        self.nodes = dict()
        self.__add_nodes(nodes)
        self.__add_edges(edges)

    def __add_nodes(self, nodes):
        for node in nodes:
            new_node = SkeletonNode(node["id"], node["point"], node["radius"])
            self.nodes[node["id"]] = new_node

    def __add_edges(self, edges):
        for edge in edges:
            first_node_id, second_node_id = edge["first_node"], edge["second_node"]
            new_edge = SkeletonEdge(first_node_id, second_node_id)
            self.edges.append(new_edge)
            self.nodes[first_node_id].add_edge(new_edge)
            self.nodes[second_node_id].add_edge(new_edge)

    def draw_skeleton(self, image_size: tuple = (900, 900), draw_circles: bool = False):
        img = Image.new("RGB", image_size, (255, 255, 255))
        d = ImageDraw.Draw(img)
        for polygon in self.polygons:
            d.polygon(polygon, outline=(0, 0, 0))
        for edge in self.edges:
            first_point = self.nodes[edge.first_node_id].point
            second_point = self.nodes[edge.second_node_id].point
            d.line([first_point, second_point], fill=(256, 0, 0))
        if draw_circles:
            for _, node in self.nodes.items():
                bb = calculate_bb(node.point, node.radius)
                d.ellipse(bb, outline=0)
        return img
