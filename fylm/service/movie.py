from fylm.model.location import LocationSet
from fylm.service.location import LocationSet as LocationSetService
from fylm.service.image_reader import ImageReader
from fylm.model.image_slice import ImageSlice
from fylm.model.movie import Movie as MovieModel
from skimage import io
from fylm.service.errors import terminal_error
import logging

log = logging.getLogger("fylm")


class Movie(object):
    def __init__(self, experiment):
        self._experiment = experiment
        location_service = LocationSetService(experiment)
        self._location_set = LocationSet(experiment)
        location_service.load_existing_models(self._location_set)

    def make_channel_overview(self, field_of_view, channel_number):
        """
        Makes a movie of a single catch channel, showing every focus level
        and filter channel available (lined up along the horizontal axis).

        :type field_of_view:    int
        :type channel_number:   int

        """
        image_reader = ImageReader(self._experiment)
        image_reader.timepoint = 1
        image_reader.field_of_view = field_of_view
        channels = self._get_channels(image_reader)
        z_levels = image_reader.nd2.z_level_count
        image_slice = self._get_image_slice(field_of_view, channel_number)
        movie = MovieModel(image_slice.height * 2, image_slice.width)

        for image_set in image_reader:
            self._update_image_data(image_slice, image_set, channels, z_levels, movie)
            io.imshow(movie.frame)
            io.show()

    def _get_image_slice(self, field_of_view, channel_number):
        for model in self._location_set.existing:
            if not model.field_of_view == field_of_view:
                continue
            notch, tube = model.get_channel_data(channel_number)
            if notch.x < tube.x:
                x = notch.x
                fliplr = False
            else:
                x = tube.x
                fliplr = True
            y = tube.y
            width = int(abs(notch.x - tube.x))
            height = int(notch.y - tube.y)
            return ImageSlice(x, y, width, height, fliplr=fliplr)
        terminal_error("Channel location has not been provided.")

    @staticmethod
    def _get_channels(image_reader):
        channels = [""]
        for channel in sorted(image_reader.nd2.channels):
            if channel.name not in channels:
                channels.append(channel.name)
        return channels

    @staticmethod
    def _update_image_data(image_slice, image_set, channels, z_levels, movie):
        for channel in channels:
            for z_level in xrange(z_levels):
                image = image_set.get_image(channel, z_level)
                if image is not None:
                    image_slice.set_image(image)
                    movie.update_image(channel, z_level, image_slice.image_data)