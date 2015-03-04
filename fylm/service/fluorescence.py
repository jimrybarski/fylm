from fylm.service.base import BaseSetService
from fylm.service.location import LocationSet as LocationService
from fylm.model.location import LocationSet
from fylm.service.annotation import AnnotationSet as AnnotationService
from fylm.model.annotation import KymographAnnotationSet
from fylm.service.kymograph import KymographSet as KymographService
from fylm.model.kymograph import KymographSet
from fylm.service.utilities import timer
import logging
import nd2reader
import numpy as np
from skimage import measure, draw

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
        Calculates the rotation offset for a single field of view and time_period.

        :type fl_model:   fylm.model.fluorescence.Fluorescence()

        """
        log.debug("Creating fluorescence file %s" % fl_model.filename)
        nd2_filename = self._experiment.get_nd2_from_time_period(fl_model.time_period)
        nd2 = nd2reader.Nd2(nd2_filename)
        try:
            # figure out where the channel is and get the pole coordinates for each frame
            location_model = self._location_set.get_model(fl_model.field_of_view)
            image_slice = location_model.get_image_slice(fl_model.channel_number)
            channel_annotation = self._annotation_set.get_model(fl_model.field_of_view, fl_model.channel_number)
        except IndexError:
            pass
        else:
            # image_set gives us access to every image for every filter channel for a single time index
            for image_set in nd2.image_sets(fl_model.field_of_view, z_levels=[1]):
                # nd2 channel names are alphabetized
                for channel_name in nd2.channel_names:
                    if channel_name == "":
                        # we skip the brightfield image since it never shows fluorescence
                        continue
                    # we grab the fluorescent image with the in-focus image. There are no out-of-focus fluorescent images
                    # in our experiments, but we still need to designate this
                    image = image_set.get_image(channel_name, z_level=1)
                    # extract the pixels just covering our catch channel
                    image_slice.set_image(image)
                    # quantify the fluorescence data
                    mean, stddev, median, area, centroid = self._measure_fluorescence(image_set.time_index, image_slice, channel_annotation)
                    # store the data in the model so it can be saved to disk later
                    fl_model.add(image_set.time_index, channel_name, mean, stddev, median, area, centroid)

    def _measure_fluorescence(self, time_index, image_slice, channel_annotation):
        try:
            mask = np.zeros((image_slice.height, image_slice.width))
            old_pole, new_pole = channel_annotation.get_cell_bounds(time_index)
            ellipse_minor_radius = int(0.80 * image_slice.height * 0.5)
            ellipse_major_radius = int((new_pole - old_pole) / 2.0) * 0.8
            centroid_y = int(image_slice.height / 2.0)
            centroid_x = int((new_pole + old_pole) / 2.0)
            rr, cc = draw.ellipse(centroid_y, centroid_x, ellipse_minor_radius, ellipse_major_radius)
            mask[rr, cc] = 1
            mean, stddev, median, area, centroid = self._calculate_cell_intensity_statistics(mask.astype("int"), image_slice.image_data)
        except IndexError:
            # We'll throw an exception anytime the cell pole locations aren't defined, in which case we want to throw out
            # any fluorescence data since we can't tell if it's the elder sibling cell or not
            return None, None, None, None, None
        else:
            return mean, stddev, median, area, centroid

    @staticmethod
    def _calculate_cell_intensity_statistics(mask, fluorescent_image_data):
        assert fluorescent_image_data.dtype == "float64"
        assert np.max(mask) == 1  # If no cell was identified, raise an exception
        masked_cell = np.ma.array(fluorescent_image_data, mask=mask == 0)
        region_properties = list(measure.regionprops(mask))
        assert len(region_properties) == 1
        properties = region_properties[0]
        centroid = int(properties.centroid[1])
        return np.ma.mean(masked_cell), np.ma.std(masked_cell), np.ma.median(masked_cell), np.ma.sum(mask), centroid