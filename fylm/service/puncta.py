from fylm.model.location import LocationSet
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
        for field_of_view in self._experiment.fields_of_view:
            log.info("Making movies for fov: %s" % field_of_view)
            self._analyze_puncta(time_periods, field_of_view)

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
                if location_model.get_channel_location(channel_number) and image_slice:
                    puncta = PunctaModel()
                    puncta.image_slice = image_slice
                    puncta.field_of_view = location_model.field_of_view
                    puncta.catch_channel_number = channel_number
                    log.debug("New puncta obj: fov %s channel %s" % (field_of_view, channel_number))
                    punctas.append(puncta)

        # Make ImageReader only show us the relevant images
        image_reader = ImageReader(self._experiment)
        image_reader.field_of_view = field_of_view

        # Iterate over the images, extract the movie frames, and save them to disk
        for time_period in xrange(time_periods):
            log.debug("Puncta Time period %s" % time_period)
            image_reader.time_period = time_period
            for n, image_set in enumerate(image_reader):
                log.debug("image #%s" % n)
                for puncta in punctas:
                    self._update_image_data(puncta, image_set)

        for puncta in punctas:
            f = tp.batch(puncta.data, 3, minmass=500)
            t = tp.link_df(f, 5, memory=3)
            t1 = tp.filter_stubs(t, 50)
            log.debug("puncta %s-%s before: %s" % (puncta.field_of_view, puncta.channel_number, t['particle'].nunique()))
            log.debug("puncta %s-%s before: %s" % (puncta.field_of_view, puncta.channel_number, t1['particle'].nunique()))

    @staticmethod
    def _update_image_data(puncta, image_set):
        image = image_set.get_image("GFP", 1)
        if image is not None:
            puncta.image_slice.set_image(image)
            puncta.update_image(image_set.timestamp)
            log.debug("added image for puncta fov %s chan %s at %s" % (puncta.field_of_view,
                                                                       puncta.channel_number,
                                                                       image_set.timestamp))