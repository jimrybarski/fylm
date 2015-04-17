from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationService
from fylm.service.image_reader import ImageReader
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.service.base import BaseSetService
from fylm.service.utilities import timer
from fylm.model.constants import Constants
import logging
import trackpy as tp
import skimage.io

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

    def save(self):
        """
        Tracks puncta in fluorescent channels.

        """
        self._action(self._experiment.time_periods)

    @timer
    def _action(self, time_periods):
        """
        Acquires all the movie objects that need to be created, sets up some variables, and gets the movies made.

        :param time_periods: list of int

        :return:    bool

        """
        # for field_of_view in self._experiment.fields_of_view:
        #     self._analyze_puncta(time_periods, field_of_view)
        self._analyze_puncta(time_periods, 0)

    @timer
    def _analyze_puncta(self, time_periods, field_of_view):
        """
        Actually extracts the images from the ND2s, then calls the movie creation method when finished.

        :type field_of_view:    int

        :returns:   bool

        """
        punctas = []
        for channel_number in xrange(Constants.NUM_CATCH_CHANNELS):
            for location_model in self._location_set.existing:
                image_slice = location_model.get_image_slice(channel_number)
                if location_model.get_channel_location(channel_number) and image_slice and location_model.field_of_view == field_of_view:
                    puncta = PunctaModel()
                    puncta.image_slice = image_slice
                    puncta.field_of_view = location_model.field_of_view
                    puncta.catch_channel_number = channel_number
                    punctas.append(puncta)

        # Make ImageReader only show us the relevant images
        image_reader = ImageReader(self._experiment)
        image_reader.field_of_view = field_of_view

        # Iterate over the images, extract the movie frames, and save them to disk
        for puncta in punctas:
            for time_period in [1]:
                image_reader.time_period = time_period
                for name in image_reader.channel_names:
                    log.debug(name)

                image_reader.time_period = time_period
                for n, image_set in enumerate(image_reader):
                    log.debug("FOV %s: %0.2f%%" % (image_reader.field_of_view, 100.0 * float(n) / float(len(image_reader))))
                    if puncta.field_of_view == image_reader.field_of_view:
                        self._update_image_data(puncta, image_set)

            log.debug(puncta.data)
            log.debug("pd len: %s" % len(puncta.data))
            log.debug("\n\n\n")
            log.debug("******** TRACKPY TIME ***********")
            log.debug("\n\n\n")
            f = tp.batch(puncta.data, 3, minmass=100)
            t = tp.link_df(f, 10, memory=3)
            t1 = tp.filter_stubs(t, 50)
            log.debug("puncta %s-%s before: %s" % (puncta.field_of_view, puncta.catch_channel_number, t['particle'].nunique()))
            log.debug("puncta %s-%s before: %s" % (puncta.field_of_view, puncta.catch_channel_number, t1['particle'].nunique()))
            print(t.head())
            tp.mass_size(t.groupby('particle').mean())
            print(t1.head())
            tp.mass_size(t1.groupby('particle').mean())

            # TODO: Filter out puncta outside of cell bounds!
            # TODO: Write results to disk!
            exit()


    @staticmethod
    def _update_image_data(puncta, image_set):
        image = image_set.get_image("GFP", 1)
        if image is not None:
            puncta.image_slice.set_image(image)
            puncta.update_image(image_set.timestamp)