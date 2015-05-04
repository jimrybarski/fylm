from fylm.model.location import LocationSet
from fylm.service.base import BaseSetService
from fylm.service.experiment import Experiment as ExperimentService
from fylm.service.image_reader import ImageReader
from fylm.service.location import LocationSet as LocationSetService
from fylm.service.utilities import timer
from fylm.service.reader import Reader
import logging
import numpy as np
from skimage import exposure
import skimage.io


log = logging.getLogger(__name__)


class KymographSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(KymographSet, self).__init__()
        self._experiment = experiment
        self._name = "kymographs"

    def save(self, kymograph_model_set):
        # Get the channel locations so we can create ImageSlice objects to help extract lines for kymographs.
        location_set = LocationSet(self._experiment)
        location_service = LocationSetService(self._experiment)
        location_service.load_existing_models(location_set)
        self.load_existing_models(kymograph_model_set)
        # Not all of the locations will necessarily be done at this point.
        # So we take the set of kymographs that still need
        # to be generated, then see if there is any location data available for them. If not, we just skip them for now.

        # Find the location model that corresponds to the field of view we're interested in
        did_work = False
        for location_model in location_set.existing:
            log.debug("Making kymographs for field of view %s" % location_model.field_of_view)

            # Each location model contains data for 28 channels in one field of view
            available_kymographs = [kymo for kymo in self.set_kymograph_locations(location_model, kymograph_model_set)]
            did_work = self.action(location_model, available_kymographs)

        if not did_work:
            log.info("All %s have been created." % self._name)

    @timer
    def action(self, location_model, available_kymographs):
        did_work = False
        log.info("Making kymographs for field of view %s:" % location_model.field_of_view)
        for time_period in self._experiment.time_periods:
            image_reader = ImageReader(self._experiment)
            image_reader.field_of_view = location_model.field_of_view
            image_reader.time_period = time_period
            # Now that we know the width and height of the kymographs, we can allocate memory for the images
            try:
                did_work = self.allocate_kymographs(available_kymographs, image_reader)
            except IOError:
                # kymographs for this time period have already been created and this image has been put in storage
                log.warn("Not making kymographs for time period %s as the ND2 is not available anymore." % time_period)
                continue

            # only iterate over this time_period's images if there is at least one channel it
            for kymograph_model in available_kymographs:
                if kymograph_model.time_period == time_period:
                    # at least one catch channel has data
                    break
            else:
                # skip this time_period
                continue

            if not self._experiment.review_annotations:
                for time_index, image_set in enumerate(image_reader):
                    log.debug("Adding lines for kymographs from time index %s" % time_index)
                    image = image_set.get_image(channel="", z_level=0)

                    for kymograph_model in available_kymographs:
                        if kymograph_model.time_period == time_period:
                            kymograph_model.set_image(image)
                            kymograph_model.add_line(time_index)
                for kymograph_model in available_kymographs:
                    if kymograph_model.time_period == time_period:
                        log.debug("Saving kymograph %s" % kymograph_model.channel_number)
                        # we stretch the image contrast to give it a better spread over the available space
                        # this prevents some information loss and makes the image more distinct
                        lower_percentile, upper_percentile = np.percentile(kymograph_model.data, (5, 95))
                        rescaled_image = exposure.rescale_intensity(kymograph_model.data, in_range=(lower_percentile,
                                                                                                    upper_percentile))
                        skimage.io.imsave(kymograph_model.path, rescaled_image)
                        kymograph_model.free_memory()

            if did_work:
                # log the completion of this time period's extraction
                ExperimentService().add_time_period_to_log(self._experiment, time_period)
        return did_work

    @staticmethod
    def set_kymograph_locations(location_model, kymograph_model_set):
        for kymograph_model in kymograph_model_set.remaining:
                # Each kymograph contains data for one channel in one field of view
                if kymograph_model.field_of_view != location_model.field_of_view:
                    continue
                try:
                    notch, tube = location_model.get_channel_data(kymograph_model.channel_number)
                except (KeyError, ValueError):
                    # There's no data for this channel
                    pass
                else:
                    kymograph_model.set_location(notch, tube)
                    yield kymograph_model

    @staticmethod
    def allocate_kymographs(available_kymographs, image_reader):
        did_work = False
        for kymograph_model in available_kymographs:
            did_work = True
            # create a numpy array with as many rows as images (and as wide as the individual channel)
            kymograph_model.allocate_memory(len(image_reader))
        return did_work