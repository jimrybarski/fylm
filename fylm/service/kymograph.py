from fylm.service.base import BaseSetService
from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationSetService
from fylm.service.image_reader import ImageReader
import skimage.io
import nd2reader
import logging


log = logging.getLogger("fylm")


class KymographSet(BaseSetService):
    """
    Determines the rotational skew of an image.

    """
    def __init__(self, experiment):
        super(KymographSet, self).__init__()
        self._experiment = experiment
        self._name = "kymographs"

    def save(self, kymograph_model_set):
        image_reader = ImageReader(self._experiment)
        # Get the channel locations so we can create ImageSlice objects to help extract lines for kymographs.
        location_set = LocationSet(self._experiment)
        location_service = LocationSetService(self._experiment)
        location_service.load_existing_models(location_set)
        # Not all of the locations will necessarily be done at this point. So we take the set of kymographs that still need
        # to be generated, then see if there is any location data available for them. If not, we just skip them for now.
        available_kymographs = []
        # Find the location model that corresponds to the field of view we're interested in
        did_work = False
        for location_model in location_set.existing:
            log.debug("Making kymographs for field of view %s" % location_model.field_of_view)
            image_reader.field_of_view = location_model.field_of_view
            # Each location model contains data for 28 channels in one field of view
            for kymograph_model in kymograph_model_set.existing:
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
                    available_kymographs.append(kymograph_model)

            for timepoint in self._experiment.timepoints:
                log.debug("Making kymographs for timepoint %s" % timepoint)
                image_reader.timepoint = timepoint
                # Now that we known the width and height of the kymographs, we can allocate memory for the images
                for kymograph_model in available_kymographs:
                    did_work = True
                    # create a numpy array with as many rows as images (and as wide as the individual channel)
                    kymograph_model.allocate_memory(len(image_reader))
                for time_index, image_set in enumerate(image_reader):
                    log.debug("Adding lines for kymographs from time index %s" % time_index)
                    image = image_set.get_image(channel="", z_level=0)
                    for kymograph_model in available_kymographs:
                        kymograph_model.set_image(image)
                        kymograph_model.add_line(time_index)

                for kymograph_model in available_kymographs:
                    log.debug("Saving kymograph %s" % kymograph_model.channel_number)
                    skimage.io.imsave(kymograph_model.path, kymograph_model.data)

        if not did_work:
            log.debug("All %s have been created." % self._name)