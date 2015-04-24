from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
from fylm.service.image_reader import ImageReader
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.service.base import BaseSetService
from fylm.service.timestamp import TimestampSet as TimestampService
from fylm.model.timestamp import TimestampSet
import logging
import trackpy as tp
import skimage.io
from pandas import DataFrame
from itertools import izip

log = logging.getLogger(__name__)



class PunctaDataModel(object):
    def __init__(self):
        self._frames = []
        self.image_slice = None
        self.time_period = None
        self.field_of_view = None
        self.catch_channel_number = None
        self._timestamps = []
        self.annotation = None
        self.diameter = 3
        self.intensity = 30
        self.ecc = 0.2

    def update_image(self, image, timestamp):
        self.image_slice.set_image(image)
        self._frames.append(self.image_slice.image_data)
        self._timestamps.append(timestamp)

    def analyze(self, frame, look=True):
        bounds = self.get_cell_bounds(frame * 2)
        if not bounds:
            log.info("No cell bounds for that frame, cell is missing or dead at that point.")
            return False
        left, right = bounds
        # We hardcode minmass here instead of using self.intensity so that we can see how many puncta total could
        # possibly be found. This helps us figure out if our criteria are too strict.
        f = tp.locate(self._frames[frame], self.diameter, minmass=3)
        f = f[(f['x'] < right)]
        f = f[(f['x'] > left)]
        f = f[(f['mass'] > self.intensity)]
        if look:
            log.debug(f)
            tp.annotate(f, self._frames[frame])
        return f

    def get_cell_bounds(self, frame):
        try:
            left, right = self.annotation.get_cell_bounds(self.time_period, frame)
        except TypeError:
            return None
        else:
            return left, right

    @property
    def batch(self):
        b = DataFrame()
        for n, frame in enumerate(self._frames):
            bounds = self.get_cell_bounds(n * 2)
            if not bounds:
                continue
            left, right = bounds
            # We hardcode minmass here instead of using self.intensity so that we can see how many puncta total could
            # possibly be found. This helps us figure out if our criteria are too strict.
            f = tp.locate(frame, self.diameter, minmass=self.intensity)
            f = f[(f['x'] < right)]
            f = f[(f['x'] > left)]
            f['timestamp'] = self._timestamps[n]
            print(f)
            b = b.append(f)
        # tdf = DataFrame(self._timestamps, columns=['timestamp'])
        # b = b.merge(tdf, left_index=True, right_index=True)
        return b

    @property
    def counts(self):
        batch = self.batch
        return batch.groupby('timestamp').size()


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
        self._annotation_service.load_existing_models(self._annotation)
        self._timestamps = TimestampSet(experiment)
        TimestampService(experiment).load_existing_models(self._timestamps)

    def list_channels(self):
        for location_model in self._location_set.existing:
            next(location_model.data)
            for channel_number, locations in location_model.data:
                print("fov %s channel %s" % (location_model.field_of_view, channel_number))

    def get_puncta_data(self, field_of_view, channel_number, tp=None):
        """
        Analyzes puncta.

        """
        for location_model in self._location_set.existing:
            if location_model.field_of_view == field_of_view:
                image_slice = location_model.get_image_slice(channel_number)
                if location_model.get_channel_location(channel_number) and image_slice:
                    puncta = PunctaDataModel()
                    puncta.image_slice = image_slice
                    puncta.field_of_view = location_model.field_of_view
                    puncta.catch_channel_number = channel_number
                    break
        else:
            log.error("No data for that fov/channel!")
            return False

        puncta.annotation = self._annotation.get_model(field_of_view, channel_number)

        if puncta.annotation is None:
            log.error("PD IS NONE")
            return None

        image_reader = ImageReader(self._experiment)
        image_reader.field_of_view = field_of_view

        time_periods = self._experiment.time_periods if tp is None else tp

        for time_period in time_periods:
            puncta.time_period = time_period
            image_reader.time_period = time_period
            for n, image_set in enumerate(image_reader):
                log.debug("TP:%s FOV:%s CH:%s TIME: %s --- %0.2f%%" % (time_period,
                                                                       image_reader.field_of_view,
                                                                       puncta.catch_channel_number,
                                                                       image_set.timestamp,
                                                                       100.0 * float(n) / float(len(image_reader))))
                self._update_image_data(puncta, image_set)
        return puncta

    @staticmethod
    def _update_image_data(puncta, image_set):
        image = image_set.get_image("GFP", 1)
        if image is not None:
            puncta.update_image(image, image_set.timestamp)