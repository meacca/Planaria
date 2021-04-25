import os
from shutil import rmtree
import numpy as np
from skimage import io, img_as_ubyte
from skimage import util, color, feature, filters
from scipy import ndimage as ndi
from planaria.config import PLANARIA_PHOTO_DIR_PATH, PLANARIA_SEGMENTATION_DIR_PATH


def find_planaria(image: np.ndarray) -> np.ndarray:
    plan = util.img_as_float(image)
    # to black-white
    plan = color.rgb2gray(plan)
    # find edges with filter
    plan = feature.canny(plan, sigma=3)

    # binarization of edges
    thresh = filters.threshold_otsu(plan)
    binary_plan = (plan > thresh).astype(float)
    binary_plan = ndi.binary_dilation(binary_plan, structure=np.ones((5, 5)))

    # fill contours
    binary_plan = ndi.binary_fill_holes(binary_plan).astype(float)
    label_objects, num_labels = ndi.label(binary_plan)
    # only for planaria
    sizes = np.bincount(label_objects.ravel())
    plan_index = np.argsort(sizes)[-2]
    mask_sizes = np.zeros(num_labels + 1)
    mask_sizes[plan_index] = 1
    binary_cleaned = mask_sizes[label_objects]

    binary_cleaned[binary_cleaned > 0] = 1
    return binary_cleaned


def planaria_from_file(photo_path: str) -> np.ndarray:
    image = io.imread(photo_path)
    binary = find_planaria(image)
    return binary


def segment_planaria_photo(photo_path: str, segmentation_path: str) -> None:
    planaria = planaria_from_file(photo_path)
    io.imsave(segmentation_path, img_as_ubyte(1 - planaria))


def segment_planaria_directory(photo_dir: str, segmentation_dir: str) -> None:
    if os.path.exists(segmentation_dir):
        rmtree(segmentation_dir)
    os.mkdir(segmentation_dir)
    photo_files = [os.path.join(photo_dir, x) for x in os.listdir(photo_dir) if x.endswith('bmp')]
    for photo_path in photo_files:
        segmentation_path = os.path.join(segmentation_dir, os.path.split(photo_path)[-1])
        segment_planaria_photo(photo_path=photo_path, segmentation_path=segmentation_path)


def segment_all_photos(all_photos_dir: str = PLANARIA_PHOTO_DIR_PATH,
                       segmentation_dir: str = PLANARIA_SEGMENTATION_DIR_PATH) -> None:
    for directory in os.listdir(all_photos_dir):
        photo_directory = os.path.join(all_photos_dir, directory)
        if not os.path.isdir(photo_directory):
            continue
        segmentation_directory = os.path.join(segmentation_dir, directory)
        segment_planaria_directory(photo_dir=photo_directory, segmentation_dir=segmentation_directory)
