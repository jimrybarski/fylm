from fylm.model.location import LocationSet
from fylm.service.image_reader import ImageReader
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.service.base import BaseSetService
import logging
import subprocess
import os
import matplotlib.pyplot as plt
from matplotlib import cm

log = logging.getLogger(__name__)


class MovieSet(BaseSetService):
    def __init__(self, experiment):
        super(MovieSet, self).__init__()
        self._name = "movie"
        self._experiment = experiment
        self._location_set = LocationSet(experiment)
        self._annotation_service = AnnotationSetService(experiment)
        self._annotation = KymographAnnotationSet(experiment)
        kymograph_service = KymographSetService(experiment)
        kymograph_set = KymographSet(experiment)
        kymograph_service.load_existing_models(kymograph_set)
        self._annotation.kymograph_set = kymograph_set

    def save(self, movie_model_set):
        self.load_existing_models(movie_model_set)
        # Find the location model that corresponds to the field of view we're interested in
        did_work = self.action(movie_model_set)
        if not did_work:
            log.info("All %s have been created." % self._name)

    def action(self, movie_model_set):
        did_work = False

        movies = [movie for movie in movie_model_set.remaining]

        for time_period in self._experiment.time_periods:
            for field_of_view in self._experiment.fields_of_view:
                image_reader = ImageReader(self._experiment)
                image_reader.field_of_view = field_of_view
                image_reader.time_period = time_period
                channels = self._get_channels(image_reader)
                z_levels = image_reader.nd2.z_level_count

                # Iterate over the images of the channel
                for n, image_set in enumerate(image_reader):
                    for movie in movies:
                        movie.time_period = time_period
                        self._update_image_data(movie, image_set, channels, z_levels)
                        image_filename = "tp%s-fov%s-channel%s-%03d.png" % (time_period,
                                                                            field_of_view,
                                                                            movie.catch_channel_number,
                                                                            n)
                        frame = movie.get_next_frame()
                        # We have to set up a Matplotlib plot so we can add text.
                        # scikit-image unfortunately has no text annotation methods.
                        fig, ax = plt.subplots()
                        ax.imshow(frame, cmap=cm.gray)

                        # Remove whitespace and ticks from the image
                        plt.gca().set_axis_off()
                        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
                        plt.margins(0, 0)
                        plt.gca().xaxis.set_major_locator(plt.NullLocator())
                        plt.gca().yaxis.set_major_locator(plt.NullLocator())

                        # Add the frame number to the bottom right of the image in red text
                        ax.annotate(str(n + 1), xy=(1, 1), xytext=(frame.shape[1] - 9, frame.shape[0] - 5), color='r')
                        log.debug("Creating %s" % movie.base_path + "/" + image_filename)
                        fig.savefig(movie.base_path + "/" + image_filename, bbox_inches='tight', pad_inches=0)
                        plt.close()

            for movie in movies:
                # We've finished making the frames of the movie. Now we use mencoder to combine them into a single .avi file
                command = ("/usr/bin/mencoder",
                           'mf://%s/tp%s-fov%s-channel%s-*.png' % (movie.base_path,
                                                                   time_period,
                                                                   movie.field_of_view,
                                                                   movie.catch_channel_number),
                           '-mf',
                           'w=%s:h=%s:fps=24:type=png' % movie.shape,
                           '-ovc', 'copy', '-oac', 'copy', '-o', '%s.avi' % movie.filename)
                DEVNULL = open(os.devnull, "w")
                failure = subprocess.call(" ".join(command), shell=True, stdout=DEVNULL, stderr=subprocess.STDOUT)
                if not failure:
                    # only delete images if everything went okay. Otherwise leave them around so we can debug the mencoder command
                    self._delete_temp_images(movie_model_set)

    # def _get_cell_bounds(self, time_period, field_of_view, channel_number):
    #     """
    #     Gets the x-position (in pixels) of the old and new cell poles for each frame. Each index holds a tuple
    #     of ints. If not available, the index holds None.
    #
    #     :return:    dict
    #
    #     """
    #     self._annotation.time_period = time_period
    #     self._annotation.field_of_view = field_of_view
    #     self._annotation.channel_number = channel_number
    #     try:
    #         self._annotation_service.load_existing_models(self._annotation)
    #         channel_group = self._annotation.get_model(field_of_view, channel_number)
    #         bounds = channel_group.get_cell_bounds(time_period)
    #     except (ValueError, IndexError, AttributeError):
    #         # That annotation doesn't exist yet or it has no data
    #         return {}
    #     else:
    #         return bounds

    @staticmethod
    def _get_channels(image_reader):
        channels = [""]
        for channel in sorted(image_reader.nd2.channels):
            if channel.name not in channels:
                channels.append(channel.name)
        return channels

    def _delete_temp_images(self, movie_model_set):
        try:
            files = os.listdir(movie_model_set.base_path)
            for f in files:
                if f.endswith(".png"):
                    os.remove(movie_model_set.base_path + "/" + f)
        except OSError:
            log.exception("Error deleting temporary movie images.")

    # def _get_image_slice(self, field_of_view, channel_number):
    #     for model in self._location_set.existing:
    #         if not model.field_of_view == field_of_view:
    #             continue
    #         notch, tube = model.get_channel_data(channel_number)
    #         if notch.x < tube.x:
    #             x = notch.x
    #             fliplr = False
    #         else:
    #             x = tube.x
    #             fliplr = True
    #         y = tube.y
    #         width = int(abs(notch.x - tube.x))
    #         height = int(notch.y - tube.y)
    #         return ImageSlice(x, y, width, height, fliplr=fliplr)
    #     terminal_error("Channel location has not been provided.")

    @staticmethod
    def _update_image_data(movie, image_set, channels, z_levels):
        for channel in channels:
            for z_level in xrange(z_levels):
                image = image_set.get_image(channel, z_level)
                if image is not None:
                    movie.image_slice.set_image(image)
                    movie.update_image(channel, z_level)