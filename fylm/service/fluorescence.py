from fylm.service.base import BaseSetService
from fylm.service.location import LocationSet as LocationService
from fylm.model.location import LocationSet
from fylm.service.annotation import AnnotationSet as AnnotationService
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.kymograph import KymographSet as KymographService
from fylm.model.kymograph import KymographSet
from fylm.service.utilities import timer
import logging
from fylm.service.image_reader import ImageReader
import numpy as np
from skimage import measure, draw
import skimage.io

log = logging.getLogger(__name__)


class FluorescenceSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(FluorescenceSet, self).__init__()
        self._experiment = experiment
        self._annotation_set = KymographAnnotationSet(experiment)
        kymograph_set = KymographSet(experiment)
        KymographService(experiment).load_existing_models(kymograph_set)
        self._annotation_set.kymograph_set = kymograph_set
        AnnotationService(experiment).load_existing_models(self._annotation_set)
        self._location_set = LocationSet(experiment)
        LocationService(experiment).load_existing_models(self._location_set)
        self._name = "fluorescence analyses"

    @timer
    def save_action(self, fl_model):
        """
        Calculates the fluorescence intensity for a catch channel.

        :type fl_model:   fylm.model.fluorescence.Fluorescence()

        """
        log.debug("Creating fluorescence file %s" % fl_model.filename)

        try:
            # figure out where the channel is and get the pole coordinates for each frame
            location_model = self._location_set.get_model(fl_model.field_of_view)
            image_slice = location_model.get_image_slice(fl_model.channel_number)
            if not image_slice:
                return True
            channel_annotation = self._annotation_set.get_model(fl_model.field_of_view, fl_model.channel_number)
            image_reader = ImageReader(self._experiment)
            image_reader.field_of_view = fl_model.field_of_view
            image_reader.time_period = fl_model.time_period
        except IndexError:
            pass
        else:
            # image_set gives us access to every image for every filter channel for a single time index
            for image_set in image_reader:
                # channel_names are alphabetized
                for channel_name in image_reader.channel_names:
                    if channel_name == "":
                        # we skip the brightfield image since it never shows fluorescence
                        continue
                    # we grab the fluorescent image with the in-focus image. There are no out-of-focus fluorescent images
                    # in our experiments, but we still need to designate this
                    image = image_set.get_image(channel_name, z_level=1)
                    if image is None:
                        # We don't have fluorescent data for this time index. This happens because we don't take fluorescent
                        # images at the same frequency as bright field, to lower the amount of blue light that the cells
                        # are exposed to.
                        continue
                    log.debug("Time index %s" % image_set.time_index)
                    # extract the pixels just covering our catch channel
                    image_slice.set_image(image)
                    # quantify the fluorescence data
                    try:
                        mean, stddev, median, area, centroid = self._measure_fluorescence(fl_model.time_period, image_set.time_index, image_slice, channel_annotation)
                    # store the data in the model so it can be saved to disk later
                    except (IndexError, ValueError, TypeError):
                        # We won't be able to get data unless the cell poles are defined, so here we silently ignore that.
                        pass
                    else:
                        fl_model.add(image_set.time_index, channel_name, mean, stddev, median, area, centroid)

    def _measure_fluorescence(self, time_period, time_index, image_slice, channel_annotation):
        log.debug("mf")
        mask = np.zeros((image_slice.height, image_slice.width))
        log.debug("mask")
        old_pole, new_pole = channel_annotation.get_cell_bounds(time_period, time_index)
        log.debug("%s,%s" % (old_pole, new_pole))
        ellipse_minor_radius = int(0.80 * image_slice.height * 0.5)
        ellipse_major_radius = int((new_pole - old_pole) / 2.0) * 0.8
        centroid_y = int(image_slice.height / 2.0)
        centroid_x = int((new_pole + old_pole) / 2.0)
        rr, cc = draw.ellipse(centroid_y, centroid_x, ellipse_minor_radius, ellipse_major_radius)
        mask[rr, cc] = 1
        mean, stddev, median, area, centroid = self._calculate_cell_intensity_statistics(mask.astype("int"), image_slice.image_data)
        log.debug(" ".join([mean, stddev, median, area, centroid]))
        return mean, stddev, median, area, centroid

    @staticmethod
    def _calculate_cell_intensity_statistics(mask, fluorescent_image_data):
        # assert fluorescent_image_data.dtype == "float64"
        assert np.max(mask) == 1  # If no cell was identified, raise an exception
        masked_cell = np.ma.array(fluorescent_image_data, mask=mask == 0)
        skimage.io.imshow(masked_cell)
        skimage.io.show()
        region_properties = list(measure.regionprops(mask))
        assert len(region_properties) == 1
        properties = region_properties[0]
        centroid = int(properties.centroid[1])
        return np.ma.mean(masked_cell), np.ma.std(masked_cell), np.ma.median(masked_cell), np.ma.sum(mask), centroid