import logging
from skimage.filter import rank, threshold_otsu, vsobel
from skimage.morphology import disk, remove_small_objects
from scipy import ndimage
import os.path
import time

log = logging.getLogger(__name__)


def timer(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        log.info('Process took: %.2f sec' % (time.time() - ts))
        return result
    return timed


class FileInteractor(object):
    def __init__(self, model):
        """
        A utility to help store models on disk.

        :param model:   fylm.model.base.BaseFile()

        """
        self._model = model

    @property
    def file_already_exists(self):
        """
        Determines whether the file that represents the model on disk exists already. If it does,
        we generally don't want to overwrite that file, though that decision is left up to the service
        implementation. This does not determine if the file is valid or even contains data.

        """
        return os.path.isfile(self._model.path)

    def write_text(self):
        """
        Saves a model to disk.

        """
        with open(self._model.path, "w+") as f:
            for line in self._model.lines:
                f.write(line + "\n")

    def read_text(self):
        """
        Loads a model from disk.

        """
        with open(self._model.path) as f:
            data = f.read(-1)
            self._model.load(data)


class ImageUtilities(object):
    @staticmethod
    def create_vertical_segments(image_data):
        """
        Creates a binary image with blobs surrounding areas that have a lot of vertical edges

        :param image_data:  a 2D numpy array

        """
        # Find edges that have a strong vertical direction
        vertical_edges = vsobel(image_data)
        # Separate out the areas where there is a large amount of vertically-oriented stuff
        return ImageUtilities._segment_edge_areas(vertical_edges)

    @staticmethod
    def _segment_edge_areas(edges, disk_size=9, mean_threshold=200, min_object_size=500):
        """
        Takes a greyscale image (with brighter colors corresponding to edges) and returns a binary image where white
        indicates an area with high edge density and black indicates low density.

        """
        # Convert the greyscale edge information into black and white (ie binary) image
        threshold = threshold_otsu(edges)
        # Filter out the edge data below the threshold, effectively removing some noise
        raw_channel_areas = edges <= threshold
        # Smooth out the data
        channel_areas = rank.mean(raw_channel_areas, disk(disk_size)) < mean_threshold
        # Remove specks and blobs that are the result of artifacts
        clean_channel_areas = remove_small_objects(channel_areas, min_size=min_object_size)
        # Fill in any areas that are completely surrounded by the areas (hopefully) covering the channels
        return ndimage.binary_fill_holes(clean_channel_areas)