from fylm.service.base import BaseSetService
from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationSetService
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
        # Get the channel locations so we can create ImageSlice objects to help extract lines for kymographs.
        location_set = LocationSet(self._experiment)
        location_service = LocationSetService(self._experiment)
        location_service.load_existing_models(location_set)
        # Not all of the locations will necessarily be done at this point. So we take the set of kymographs that still need
        # to be generated, then see if there is any location data available for them. If not, we just skip them for now.
        available_kymographs = []
        for kymograph_model in kymograph_model_set.remaining:
            # Find the location model that corresponds to the field of view we're interested in
            for location_model in location_set.existing:
                if location_model.field_of_view == kymograph_model.field_of_view:
                    location = location_model
                    break
            else:
                log.warn("No location exists for field of view %s" % kymograph_model.field_of_view)
                continue
            kymograph_model.set_location(location)

            # create kymograph numpy arrays
            # save images to disk

        did_work = False
        for kymograph in available_kymographs:
            did_work = True

        if not did_work:
            log.debug("All %s have been created." % self._name)