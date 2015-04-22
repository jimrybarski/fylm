from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
from fylm.service.image_reader import ImageReader
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.service.base import BaseSetService
import logging
import trackpy as tp

log = logging.getLogger(__name__)


class PunctaModel(object):
    def __init__(self):
        self._frames = []
        self.image_slice = None
        self.time_period = None
        self.field_of_view = None
        self.catch_channel_number = None
        self._timestamps = []

    def update_image(self, timestamp):
        self._frames.append(self.image_slice.image_data)
        self._timestamps.append(timestamp)

    @property
    def data(self):
        return self._frames


class PunctaSet(BaseSetService):
    """
    Creates a movie for each catch channel, with every zoom level and fluorescence channel in each frame.
    This works by iterating over the ND2, extracting the image of each channel for all dimensions, and saving
    a PNG file. When every frame has been extracted, we use mencoder to combine the still images into a movie
    and then delete the PNGs.

    The videos end up losing some information so this is mostly just for debugging and for help with annotating
    kymographs when weird things show up, as well as for figures, potentially.

    Previously we had some functionality that would add orange arrows to point out the cell pole positions if the
    annotations had been done. That was removed temporarily when this module was refactored but we intend to add it
    back in soon.

    """
    def __init__(self, experiment):
        super(PunctaSet, self).__init__()
        self._name = "puncta"
        self._experiment = experiment
        self._location_set = LocationSet(experiment)
        LocationService(self._experiment).load_existing_models(self._location_set)
        self._annotation_service = AnnotationSetService(experiment)
        self._annotation = KymographAnnotationSet(experiment)
        kymograph_service = KymographSetService(experiment)
        kymograph_set = KymographSet(experiment)
        kymograph_service.load_existing_models(kymograph_set)
        self._annotation.kymograph_set = kymograph_set

    def list_channels(self):
        for location_model in self._location_set.existing:
            next(location_model.data)
            for channel_number, locations in location_model.data:
                print("fov %s channel %s" % (location_model.field_of_view, channel_number))

    def get_data_and_batch(self, field_of_view, channel_number):
        """
        Analyzes puncta.

        """
        for location_model in self._location_set.existing:
            if location_model.field_of_view == field_of_view:
                image_slice = location_model.get_image_slice(channel_number)
                if location_model.get_channel_location(channel_number) and image_slice:
                    puncta = PunctaModel()
                    puncta.image_slice = image_slice
                    puncta.field_of_view = location_model.field_of_view
                    puncta.catch_channel_number = channel_number
                    break
        else:
            log.error("No data for that fov/channel!")
            return False

        image_reader = ImageReader(self._experiment)
        image_reader.field_of_view = field_of_view

        for time_period in self._experiment.time_periods:
            image_reader.time_period = time_period
            for n, image_set in enumerate(image_reader):
                log.debug("TP:%s FOV:%s CH:%s %0.2f%%" % (time_period,
                                                          image_reader.field_of_view,
                                                          puncta.catch_channel_number,
                                                          100.0 * float(n) / float(len(image_reader))))
                self._update_image_data(puncta, image_set)
                if n > 8:
                    break

        # while True:
        #     for n, frame in enumerate(test_frames):
        #         image = puncta.data[frame]
        #         f = tp.locate(image, 15, 1.0)
        #         tp.annotate(f[(f['mass'] > minintensity) & (f['ecc'] < ecc_upper_limit) & (f['size'] > minsize)], image)
        #
        #     done = raw_input("OK? Enter=no, anything else=yes: ")
        #     log.debug("done: %s" % done)
        #     if done:
        #         break
        #     minintensity = float(raw_input("min intensity (%s): " % minintensity) or minintensity)
        #     ecc_upper_limit = float(raw_input("ecc_upper_limit (%s): " % ecc_upper_limit) or ecc_upper_limit)
        #     minsize = int(raw_input("min diameter (%s): " % minsize) or minsize)

        return puncta.data, tp.batch(puncta.data, 3, 0.01)

        # for item in batch.iteritems():
        #     annotation = self._annotation.get_model(field_of_view, channel_number)
        #     try:
        #         left, right = annotation.get_cell_bounds(time_period, item['frame'])
        #     except TypeError:
        #         # no cell bounds so we can't tell if puncta are in the cell or not
        #         # in fact there might not be a cell, or it could be dead
        #         continue
        #     else:
        #         print(item[(item['mass'] > minintensity) & (item['ecc'] < ecc_upper_limit) & (item['size'] > minsize)
        #               & (right >= item['x'] >= left)])

        # THESE MIGHT BE WRONG DEPENDING ON WHAT ITEM IS
        # percentile_position = (item['x'] - left) / (right - left)
        # distribution of puncta brightness in space (Do puncta of a certain brightness tend to be found in a certain location?)
        # distribution of puncta size in space (Do puncta of a certain size tend to be found in a certain location?)
        # total puncta count over time (Is there a relationship between puncta and aging?)
        # number of puncta at death (manual)
        # number of puncta immediately after division

    def look(self, puncta_data, frame):
        tp.annotate(puncta_data, puncta_data[frame])


    @staticmethod
    def _update_image_data(puncta, image_set):
        image = image_set.get_image("GFP", 1)
        if image is not None:
            puncta.image_slice.set_image(image)
            puncta.update_image(image_set.timestamp)