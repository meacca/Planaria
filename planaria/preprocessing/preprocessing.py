import os
from .skeleton_way import SkeletonWay
from collections import defaultdict
import pandas as pd
import math


class Preprocesser:
    def __init__(self, skeleton_dir: str, skeleton_way_ending: str = "_skeleton_extra.txt"):
        self._skeleton_dir = skeleton_dir
        self._skeleton_way_ending = skeleton_way_ending

    @staticmethod
    def read_skeletons_dir(dir_name, skeleton_way_ending="_skeleton_extra.txt"):
        class_label = int(dir_name.split(' ')[-1])
        skeletons_dir = []
        sample_names = []
        skeleton_files = os.listdir(dir_name)
        skeleton_files = [os.path.join(dir_name, x) for x in skeleton_files
                          if x.endswith(skeleton_way_ending)]
        for skeleton_file in skeleton_files:
            sample_name = os.path.basename(skeleton_file).rstrip(skeleton_way_ending)
            sample_names.append(sample_name)
            skeleton_way = SkeletonWay(skeleton_file)
            skeletons_dir.append(skeleton_way)
        class_labels_dir = [class_label] * len(skeletons_dir)
        return skeletons_dir, class_labels_dir, sample_names

    def read_skeletons_all(self):
        skeletons_all = []
        class_labels_all = []
        sample_names_all = []
        for directory in os.listdir(self._skeleton_dir):
            planaria_directory = os.path.join(self._skeleton_dir, directory)
            if not os.path.isdir(planaria_directory):
                continue
            skeletons_dir, class_labels_dir, sample_names = self.read_skeletons_dir(planaria_directory,
                                                                                    self._skeleton_way_ending)
            skeletons_all.extend(skeletons_dir)
            class_labels_all.extend(class_labels_dir)
            sample_names_all.extend(sample_names)
        return skeletons_all, class_labels_all, sample_names_all


class FeaturePreprocesser(Preprocesser):
    def __init__(self, skeleton_dir: str, skeleton_way_ending: str = "_skeleton_extra.txt"):
        super().__init__(skeleton_dir, skeleton_way_ending)

    def preprocess_all(self) -> pd.DataFrame:
        skeletons_all, class_labels_all, sample_names_all = self.read_skeletons_all()
        res_dict = defaultdict(list)
        res_dict["sample"] = sample_names_all
        res_dict["class_label"] = class_labels_all
        for skeleton_way in skeletons_all:
            skeleton_features = skeleton_way.get_features()
            for key, feature in skeleton_features.items():
                res_dict[key].append(feature)
        return pd.DataFrame(res_dict)


class ShapePreprocesser(Preprocesser):
    def __init__(self, skeleton_dir: str, skeleton_way_ending: str = "_skeleton_extra.txt"):
        super().__init__(skeleton_dir, skeleton_way_ending)

    def preprocess_all(self, len_threshold: int = 900):
        skeletons_all, class_labels_all, sample_names_all = self.read_skeletons_all()
        skeletons_res, class_labels_res, sample_names_res = [], [], []
        for skeleton, class_label, name in zip(skeletons_all, class_labels_all, sample_names_all):
            skeleton_len = skeleton.calculate_length()
            if (not math.isnan(skeleton_len)) and (skeleton_len < len_threshold):
                skeletons_res.append(skeleton)
                class_labels_res.append(class_label)
                sample_names_res.append(name)
        return skeletons_res, class_labels_res, sample_names_res
