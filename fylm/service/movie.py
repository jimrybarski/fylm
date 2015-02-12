from fylm.model.image_slice import ImageSlice
from fylm.model.location import LocationSet
from fylm.model.movie import Movie as MovieModel
from fylm.service.errors import terminal_error
from fylm.service.image_reader import ImageReader
from fylm.service.location import LocationSet as LocationSetService
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
import logging
from skimage import io
import subprocess
import os

log = logging.getLogger(__name__)


class Movie(object):
    def __init__(self, experiment):
        self._location_set = LocationSet(experiment)
        location_service = LocationSetService(experiment)
        location_service.load_existing_models(self._location_set)
        self._annotation_service = AnnotationSetService(experiment)
        self._annotation = KymographAnnotationSet(experiment)
        self._image_reader = ImageReader(experiment)
        self._base_dir = experiment.data_dir + "/movie/"
        kymograph_service = KymographSetService(experiment)
        kymograph_set = KymographSet(experiment)
        kymograph_service.load_existing_models(kymograph_set)
        self._annotation.kymograph_set = kymograph_set

    def _get_cell_bounds(self, time_period, field_of_view, channel_number):
        """
        Gets the x-position (in pixels) of the old and new cell poles for each frame. Each index holds a tuple
        of ints. If not available, the index holds None.

        :return:    dict

        """
        self._annotation.time_period = time_period
        self._annotation.field_of_view = field_of_view
        self._annotation.channel_number = channel_number
        try:
            self._annotation_service.load_existing_models(self._annotation)
            channel_group = self._annotation.get_model(field_of_view, channel_number)
        except ValueError:
            # That annotation doesn't exist yet or it has no data
            return {}
        else:
            return channel_group.get_cell_bounds(time_period)

    def make_channel_overview(self, time_period, field_of_view, channel_number):
        """
        Makes a movie of a single catch channel, showing every focus level
        and filter channel available (lined up along the horizontal axis).

        :type field_of_view:    int
        :type channel_number:   int

        """
        self._image_reader.time_period = time_period
        self._image_reader.field_of_view = field_of_view
        cell_bounds = self._get_cell_bounds(time_period, field_of_view, channel_number)
        channels = self._get_channels(self._image_reader)
        z_levels = self._image_reader.nd2.z_level_count
        image_slice = self._get_image_slice(field_of_view, channel_number)
        movie = MovieModel(image_slice.height * 2, image_slice.width)
        images = os.listdir(self._base_dir)
        base_filename = self._base_dir + "tp%s-fov%s-channel%s" % (time_period, field_of_view, channel_number)

        log.info("Creating movie file: %s.avi" % base_filename)

        for n, image_set in enumerate(self._image_reader):
            filename = "tp%s-fov%s-channel%s-%03d.png" % (time_period, field_of_view, channel_number, n)
            if filename not in images:
                self._update_image_data(image_slice, image_set, channels, z_levels, movie)
                log.debug("Adding movie frame %s" % n)
                poles = cell_bounds.get(n)
                if poles is not None:
                    movie.add_triangle(poles[0])
                    movie.add_triangle(poles[1])
                frame = movie.frame
                io.imsave(self._base_dir + filename, frame)

        command = ("/usr/bin/mencoder",
                   'mf://%s*.png' % self._base_dir,
                   '-mf',
                   'w=%s:h=%s:fps=24:type=png' % (movie.frame.shape[1], movie.frame.shape[0]),
                   '-ovc', 'copy', '-oac', 'copy', '-o', '%s.avi' % base_filename)
        DEVNULL = open(os.devnull, "w")
        failure = subprocess.call(" ".join(command), shell=True, stdout=DEVNULL, stderr=subprocess.STDOUT)
        if not failure:
            self._delete_temp_images()

    def _delete_temp_images(self):
        try:
            files = os.listdir(self._base_dir)
            for f in files:
                if f.endswith(".png"):
                    os.remove(self._base_dir + f)
        except Exception:
            log.exception("Error deleting temporary movie images.")

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