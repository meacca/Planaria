import os
from . import SkeletonWay


def parse_polygons(polygons_raw: str, point_sep: str = "\n", polygon_sep: str = "\n\n"):
    polygons = polygons_raw.split(polygon_sep)
    assert polygons[0] == "POLYGONS"
    polygons = polygons[1:]
    parsed_polygons = []
    for polygon in polygons:
        polygon_points = [tuple(map(float, point.split(' '))) for point in polygon.split(point_sep)]
        parsed_polygons.append(polygon_points)
    return parsed_polygons


def parse_edges(edges_raw: str, edges_sep: str = '\n', radius_sep: str = '\t'):
    edges = edges_raw.split(edges_sep)
    assert edges[0] == "EDGES"
    edges = edges[1:]
    parsed_edges = []
    for edge_rad in edges:
        if edge_rad == "":
            continue
        parsed_edge = {}
        edge, radii = edge_rad.split(radius_sep)
        edge_split = edge.split(' ')
        assert len(edge_split) in [4, 6]
        parsed_edge["first_point"] = tuple(map(float, edge_split[:2]))
        parsed_edge["second_point"] = tuple(map(float, edge_split[2:4]))
        if len(edge_split) == 6:
            parsed_edge["virtual_point"] = tuple(map(float, edge_split[4:]))
        parsed_edge["radii"] = tuple(map(float, radii.split(' ')))
        parsed_edges.append(parsed_edge)
    return parsed_edges


def parse_nodes(nodes_raw: str, nodes_sep: str = '\n', radius_sep: str = '\t'):
    nodes = nodes_raw.split(nodes_sep)
    # assert nodes[0] == "NODES"
    nodes = nodes[1:]
    parsed_nodes = []
    for node_rad in nodes:
        if node_rad == "":
            continue
        parsed_node = {}
        point, radius = node_rad.split(radius_sep)
        parsed_node["point"] = tuple(map(float, point.split(' ')))
        parsed_node["radius"] = float(radius)
        parsed_nodes.append(parsed_node)
    return parsed_nodes


def parse_file_voronoi(diagram_raw: str, total_sep: str = "\n\n\n\n"):
    polygons_raw, edges_raw = diagram_raw.split(total_sep)
    parsed_polygons = parse_polygons(polygons_raw)
    parsed_edges = parse_edges(edges_raw)
    return parsed_polygons, parsed_edges


def parse_file_skeleton(skeleton_raw: str, total_sep: str = "\n\n\n\n"):
    polygons_raw, edges_raw, nodes_raw = skeleton_raw.split(total_sep)
    parsed_polygons = parse_polygons(polygons_raw)
    parsed_edges = parse_edges(edges_raw)
    parsed_nodes = parse_nodes(nodes_raw)
    return parsed_polygons, parsed_edges, parsed_nodes


def parse_file_extra_skeleton(skeleton_raw: str, total_sep: str = "\n\n\n\n"):
    parsed = skeleton_raw.split(total_sep)
    if len(parsed) == 1:
        return int(parsed[0].split('\n')[1]), [], [], []
    count_terminals_raw, nodes_raw, edges_raw, skeleton_way_raw = parsed
    count_terminals = int(count_terminals_raw.split('\n')[-1])
    parsed_nodes = parse_nodes(nodes_raw)
    parsed_edges = parse_edges(edges_raw)
    skeleton_way = parse_nodes(skeleton_way_raw)
    return count_terminals, parsed_nodes, parsed_edges, skeleton_way


def parse_file(path_to_file: str, diagram_type: str, total_sep: str = "\n\n\n\n"):
    assert diagram_type in ["voronoi", "skeleton", "skeleton_way"]
    with open(path_to_file, "r") as f:
        file_raw = f.read()
    if diagram_type == "voronoi":
        return parse_file_voronoi(file_raw, total_sep)
    elif diagram_type == "skeleton":
        return parse_file_skeleton(file_raw, total_sep)
    else:
        return parse_file_extra_skeleton(file_raw, total_sep)


def read_skeletons_dir(dir_name, skeleton_way_ending="_skeleton_extra.txt"):
    class_label = int(dir_name.split(' ')[-1])
    skeletons_dir = []
    skeleton_files = os.listdir(dir_name)
    skeleton_files = [os.path.join(dir_name, x) for x in skeleton_files
                      if x.endswith(skeleton_way_ending)]
    for skeleton_file in skeleton_files:
        skeleton_way = SkeletonWay(skeleton_file)
        skeletons_dir.append(skeleton_way)
    class_labels_dir = [class_label] * len(skeletons_dir)
    return skeletons_dir, class_labels_dir


def read_skeletons_all(total_dir_name, skeleton_way_ending="_skeleton_extra.txt"):
    skeletons_all = []
    class_labels_all = []
    for directory in os.listdir(total_dir_name):
        planaria_directory = os.path.join(total_dir_name, directory)
        if not os.path.isdir(planaria_directory):
            continue
        skeletons_dir, class_labels_dir = read_skeletons_dir(planaria_directory,
                                                             skeleton_way_ending=skeleton_way_ending)
        skeletons_all.extend(skeletons_dir)
        class_labels_all.extend(class_labels_dir)
    return skeletons_all, class_labels_all
