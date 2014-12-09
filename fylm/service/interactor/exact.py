from fylm.model.constants import Constants
from fylm.model.image_slice import ImageSlice
from fylm.service.interactor.base import HumanInteractor
import logging
from matplotlib import pyplot as plt

log = logging.getLogger("fylm")


class ExactChannelFinder(HumanInteractor):
    """
    Gets the user to define the exact location of all 28 channels, one-by-one. The user clicks on the notch, then the top right corner of the catch tube (i.e. the
    corner of the catch tube and the central trench). The location of the bottom right corner is inferred from this data.

    """
    def __init__(self, location_model):
        super(ExactChannelFinder, self).__init__()
        self._location_set_model = location_model
        # self._channels = []
        # self._current_image_slice = None
        self._channel_number = 1
        self._start()
        self._reset()

    @property
    def _image_slices(self):
        top_left = self._location_set_model.top_left
        bottom_right = self._location_set_model.bottom_right
        total_height = bottom_right.y - top_left.y  # numpy arrays have y increasing as you go downwards
        likely_distance = total_height / ((Constants.NUM_CATCH_CHANNELS / 2) - 1)  # exclude the first channel because math
        expected_channel_width = 230
        expected_channel_height = 30
        width_margin = 60
        height_margin = 30

        for i in range(Constants.NUM_CATCH_CHANNELS / 2):
            yield ImageSlice(max(0, top_left.x - width_margin),
                             max(0, top_left.y + likely_distance * i - height_margin * 2),
                             expected_channel_width + width_margin * 2,
                             expected_channel_height + height_margin * 3)

            yield ImageSlice(max(0, bottom_right.x - expected_channel_width - width_margin),
                             max(0, top_left.y + likely_distance * i - height_margin * 2),
                             expected_channel_width + width_margin * 2,
                             expected_channel_height + height_margin * 3)

    def _on_mouse_click(self, human_input):
        if human_input.left_click and len(self._coordinates) < 2:
            self._add_point(*human_input.coordinates)
        if human_input.right_click:
            self._remove_last_point()

    def _on_key_press(self, human_input):
        if human_input.key == 'enter' and len(self._coordinates) == 2:
            self._handle_results()
        elif human_input.key == 'escape':
            self._erase_all_points()
            self._close()

    def _handle_results(self):
        # TODO: You want sweet left and right arrows to be able to go back and forth. Load previous data?
        # TODO: That may require adding some things to the Location model. That's OK. Whatever it takes.
        # notch = self._current_image_slice.get_parent_coordinates(self._coordinates[0])
        # tube = self._current_image_slice.get_parent_coordinates(self._coordinates[1])
        # channel = Channel()
        # channel.set_coords(notch.x, notch.y, tube.x, tube.y)
        # channel.set_name(self._channel_number, self._field_of_view)
        # self._channels.append(channel)
        self._erase_all_points()
        self._close()

    def _start(self):
        # self._current_image_slice = image_slice
        # self._fig.suptitle("Channel: " + str(self._channel_number), fontsize=20)
        # self._ax.imshow(image_slice.image_data, cmap='gray')
        self._ax.autoscale(False)
        plt.show()