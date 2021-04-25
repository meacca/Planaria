import os
from . import SkeletonWay
from collections import defaultdict
import pandas as pd


class Preprocesser:
    def __init__(self, skeleton_dir: str, skeleton_way_ending: str = "_skeleton_extra.txt"):
        self._skeleton_dir = skeleton_dir
        self._skeleton_way_ending = skeleton_way_ending

    def __preprocess_file(self, skeleton_file: str, class_label: int):
        sample_name = os.path.basename(skeleton_file).rstrip(self._skeleton_way_ending)
        skeleton_way = SkeletonWay(skeleton_file)
        skeleton_features = skeleton_way.get_features()
        return sample_name, class_label, skeleton_features

    @staticmethod
    def __preprocess_features(skeleton_features):
        res = defaultdict(list)
        for feature_dict in skeleton_features:
            for key in feature_dict:
                res[key].append(feature_dict[key])
        return res

    def __preprocess_directory(self, directory_path: str) -> pd.DataFrame:
        class_label = int(directory_path.split(' ')[-1])
        skeleton_files = os.listdir(directory_path)
        skeleton_files = [os.path.join(directory_path, x) for x in skeleton_files
                          if x.endswith(self._skeleton_way_ending)]
        sample_names, class_labels = [], []
        skeleton_features_all = []
        for skeleton_file in skeleton_files:
            sample_name, class_label, skeleton_features = self.__preprocess_file(skeleton_file, class_label)
            sample_names.append(sample_name)
            class_labels.append(class_label)
            skeleton_features_all.append(skeleton_features)
        res_dict = {"sample": sample_names, "class_label": class_labels}
        res_dict.update(self.__preprocess_features(skeleton_features_all))
        return pd.DataFrame(res_dict)

    def preprocess_all(self) -> pd.DataFrame:
        preprocessed_dirs = []
        for directory in os.listdir(self._skeleton_dir):
            planaria_directory = os.path.join(self._skeleton_dir, directory)
            if not os.path.isdir(planaria_directory):
                continue
            preprocessed_dirs.append(self.__preprocess_directory(directory_path=planaria_directory))
        res = pd.concat(preprocessed_dirs)
        res.reset_index(drop=True, inplace=True)
        return res
