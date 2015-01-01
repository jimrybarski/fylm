from fylm.service.location import LocationSet
from fylm.service.image_reader import ImageReader


class Movie(object):
    def __init__(self, experiment):
        self._experiment = experiment
        self._location_set = LocationSet(experiment)

    def make_channel_overview(self, field_of_view, channel_number):
        """
        Makes a movie of a single catch channel, showing every focus level
        and filter channel available (lined up along the horizontal axis).

        :type field_of_view:    int
        :type channel_number:   int

        """
        for model in self._location_set.existing:
            if not model.field_of_view == field_of_view:
                continue
            notch, tube = model.get_channel_data(channel_number)
            # Create the image slice, reverse image if needed
            # Create a movie model
            # Create an ImageReader and start iterating over the image sets
            # For each image set, set the image on the image slice,
            #   extract the slice, and update the image data on the movie model
            #   Then get the frame image, and...uh...add it to a pile?
            #   Look at that 3rd party library now to learn how to make movies

            # TODO: Get kymograph annotation data, add orange triangles