from fylm.model.location import LocationSet
from fylm.service.image_reader import ImageReader
from fylm.service.annotation import AnnotationSet as AnnotationSetService
from fylm.model.annotation import KymographAnnotationSet
from fylm.model.kymograph import KymographSet
from fylm.service.kymograph import KymographSet as KymographSetService
from fylm.service.base import BaseSetService
from fylm.service.utilities import timer
import logging
import subprocess
import os
import matplotlib.pyplot as plt
from matplotlib import cm

log = logging.getLogger(__name__)


class MovieSet(BaseSetService):
    """
    Creates a movie for each catch channel, with every zoom level and fluorescence channel in each frame.
    This works by iterating over the ND2, extracting the image of each channel for all dimensions, and saving
    a PNG file. When every frame has been extracted, we used mencoder to combine the still images into a movie
    and then delete the PNGs.

    The videos end up losing some information so this is mostly just for debugging and for help with annotating
    kymographs when weird things show up.

    """
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

    @timer
    def action(self, movie_model_set):
        did_work = False
        movies = [movie for movie in movie_model_set.remaining]
        for time_period in self._experiment.time_periods:
            for field_of_view in self._experiment.fields_of_view:
                log.info("Making movies for fov: %s" % field_of_view)
                if self._make_field_of_view_movie(movies, time_period, field_of_view):
                    did_work = True
        return did_work

    @timer
    def _make_field_of_view_movie(self, movies, time_period, field_of_view):
        # movies contains movie objects from every field of view. We separate out the ones for the current field
        # of view and act only on them. We also update the time period as that's used in the output file name
        fov_movies = [movie for movie in movies if movie.field_of_view == field_of_view]
        for movie in fov_movies:
            movie.time_period = time_period

        # If this field of view has any movies, we're necessarily going to be creating files that don't yet exist,
        # so we can be certain work will be done.
        did_work = bool(fov_movies)

        # Make ImageReader only show us the relevant images
        image_reader = ImageReader(self._experiment)
        image_reader.field_of_view = field_of_view
        image_reader.time_period = time_period
        channels = self._get_channels(image_reader)
        z_levels = image_reader.nd2.z_level_count

        # Iterate over the images, extract the movie frames, and save them to disk
        for n, image_set in enumerate(image_reader):
            for movie in fov_movies:
                self._update_image_data(movie, image_set, channels, z_levels)
                image_filename = "tp%s-fov%s-channel%s-%03d.png" % (time_period,
                                                                    field_of_view,
                                                                    movie.catch_channel_number,
                                                                    n)
                self._write_movie_frame(n, movie.get_next_frame(), movie.base_path, image_filename)

        # We've finished making the frames of the movie.
        # Now we use mencoder to combine them into a single .avi file
        for movie in fov_movies:
            self._create_movie_from_frames(movie, time_period)
        return did_work

    @timer
    def _create_movie_from_frames(self, movie, time_period):
        """
        Makes a movie in chronological order using images with a given filename pattern.

        """
        command = ("/usr/bin/mencoder",
                   'mf://%s/tp%s-fov%s-channel%s-*.png' % (movie.base_path,
                                                           time_period,
                                                           movie.field_of_view,
                                                           movie.catch_channel_number),
                   '-mf',
                   'w=%s:h=%s:fps=24:type=png' % movie.shape,
                   '-ovc', 'copy', '-oac', 'copy', '-o', '%s' % movie.base_path + "/" + movie.filename)
        log.info("Making movie with: %s" % " ".join(command))
        DEVNULL = open(os.devnull, "w")
        failure = subprocess.call(" ".join(command), shell=True, stdout=DEVNULL, stderr=subprocess.STDOUT)
        if not failure:
            # only delete images if everything went okay.
            # Otherwise leave them around so we can debug the mencoder command
            self._delete_temp_images(movie, time_period)

    @staticmethod
    def _write_movie_frame(frame_number, frame, base_path, image_filename):
        """
        Takes a movie frame, adds the frame number to the bottom right of the image, and saves it to disk.

        """
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
        ax.annotate(str(frame_number + 1), xy=(1, 1), xytext=(frame.shape[1] - 9, frame.shape[0] - 5), color='r')
        log.debug("Creating %s" % base_path + "/" + image_filename)
        fig.savefig(base_path + "/" + image_filename, bbox_inches='tight', pad_inches=0)
        plt.close()



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
        """
        Creates an alphabetized list of filter channel names, starting with bright field (which in ND2s is called "")

        :return:    list of str

        """
        channels = [""]
        for channel in sorted(image_reader.nd2.channels):
            if channel.name not in channels:
                channels.append(channel.name)
        return channels

    @timer
    def _delete_temp_images(self, movie, time_period):
        """
        Cleans up the temporary still image files that were used to make a movie.

        :param movie:
        :param time_period:

        """
        try:
            for filename in os.listdir(movie.base_path):
                if filename.startswith("tp%s-fov%s-channel%s" % (time_period,
                                                                 movie.field_of_view,
                                                                 movie.catch_channel_number)) and filename.endswith(".png"):
                    log.debug("Deleting %s" % filename)
                    os.remove(movie.base_path + "/" + filename)
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
        """
        Gives the Movie object more image data for any channels with new images.
        Some fluorescence channels only get captured every other frame (or less). In that case, we just don't update
        the image data for that channel, and instead use the same data from before. This will result in a movie that
        looks stuttered.

        :param movie:
        :param image_set:
        :param channels:
        :param z_levels:

        """
        for channel in channels:
            for z_level in xrange(z_levels):
                image = image_set.get_image(channel, z_level)
                if image is not None:
                    movie.image_slice.set_image(image)
                    movie.update_image(channel, z_level)