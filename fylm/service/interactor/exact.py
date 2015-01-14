from fylm.model.constants import Constants
from fylm.model.image_slice import ImageSlice
from fylm.service.interactor.base import HumanInteractor
import logging
from matplotlib import pyplot as plt
import time

log = logging.getLogger("fylm")


class ExactChannelFinder(HumanInteractor):
    """
    Gets the user to define the exact location of all 28 channels, one-by-one. The user clicks on the notch, then the top right corner of the catch tube (i.e. the
    corner of the catch tube and the central trench). The location of the bottom right corner is inferred from this data.

    """
    def __init__(self, location_model, image):
        super(ExactChannelFinder, self).__init__()
        # some constants
        self._top_left = location_model.top_left
        self._bottom_right = location_model.bottom_right
        self._current_image_slice = None
        self._total_height = self._bottom_right.y - self._top_left.y  # numpy arrays have y increasing as you go downwards
        self._likely_distance = self._total_height / ((Constants.NUM_CATCH_CHANNELS / 2) - 1)  # exclude the first channel because math
        self._expected_channel_width = 230
        self._expected_channel_height = 30
        self._width_margin = 60
        self._height_margin = 30
        self._image = image
        # dynamic variables
        self._location_model = location_model
        self._current_channel_number = 0
        self._done = False
        while not self._done:
            self._start()
            if not self._done:
                self._reset()

    def _get_image_slice(self):
        # we need a row number from 0 to 13 to calculate the offset from the first row
        row = (self._current_channel_number - self._current_channel_number % 2) / 2
        if self._current_channel_number % 2 == 0:
            # left catch channel
            x = max(0, self._top_left.x - self._width_margin)
            y = max(0, self._top_left.y + self._likely_distance * row - self._height_margin * 2)
            width = self._expected_channel_width + self._width_margin * 2
            height = self._expected_channel_height + self._height_margin
            image_slice = ImageSlice(x, y, width, height)
        else:
            # right catch channel
            x = max(0, self._bottom_right.x - self._expected_channel_width - self._width_margin)
            y = max(0, self._top_left.y + self._likely_distance * row - self._height_margin * 2)
            width = self._expected_channel_width + self._width_margin * 2
            height = self._expected_channel_height + self._height_margin
            image_slice = ImageSlice(x, y, width, height)
        image_slice.set_image(self._image)
        return image_slice

    def _on_mouse_click(self, human_input):
        if human_input.left_click and len(self._coordinates) < 2:
            self._add_point(human_input.coordinates.x, human_input.coordinates.y)
        if human_input.right_click:
            self._remove_last_point()

    def _on_key_press(self, human_input):
        if human_input.key == 'w':
            self._location_model.skip_remaining()
            self._done = True
            self._clear()
        elif human_input.key == 'enter' and len(self._coordinates) == 2:
            self._handle_results()
            self._increment_channel()
            self._clear()
        elif human_input.key == 'escape':
            self._handle_results()
            self._clear()
            self._increment_channel()
        elif human_input.key == 'left':
            if not self._coordinates:
                self._handle_results()
            self._clear()
            self._decrement_channel()
        elif human_input.key == 'right':
            if not self._coordinates:
                self._handle_results()
            self._clear()
            self._increment_channel()

    def _decrement_channel(self):
        self._current_channel_number -= 1
        if self._current_channel_number == -1:
            self._current_channel_number = Constants.NUM_CATCH_CHANNELS - 1

    def _increment_channel(self):
        self._current_channel_number += 1
        if self._current_channel_number == Constants.NUM_CATCH_CHANNELS:
            self._current_channel_number = 0

    def _clear(self):
        self._erase_all_points()
        self._close()
        time.sleep(0.2)

    def _handle_results(self):
        if self._coordinates:
            notch = self._current_image_slice.get_parent_coordinates(self._coordinates[0])
            tube = self._current_image_slice.get_parent_coordinates(self._coordinates[1])
            self._location_model.set_channel_location(self._current_channel_number, notch.x, notch.y, tube.x, tube.y)
        else:
            self._location_model.skip_channel(self._current_channel_number)
        self._clear()

    def _start(self):
        self._current_image_slice = self._get_image_slice()
        self._fig.suptitle("Channel: " + str(self._current_channel_number + 1), fontsize=20)
        self._ax.imshow(self._current_image_slice.image_data, cmap='gray')
        self._ax.autoscale(False)
        self._draw_existing_data()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()

    def _draw_existing_data(self):
        coordinates = self._location_model.get_channel_location(self._current_channel_number)
        if coordinates == "skipped":
            # draw an X
            pass
        elif coordinates:
            notch = self._current_image_slice.get_child_coordinates(coordinates[0])
            tube = self._current_image_slice.get_child_coordinates(coordinates[1])
            self._add_point(notch.x, notch.y)
            self._add_point(tube.x, tube.y)