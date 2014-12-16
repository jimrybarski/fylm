from fylm.model.constants import Constants
from fylm.service.interactor.base import HumanInteractor
import logging
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import gray2rgb
from skimage.draw import line

log = logging.getLogger("fylm")


class KymographAnnotator(HumanInteractor):
    """
    Gets the user to define the exact location of all 28 channels, one-by-one. The user clicks on the notch, then the top right corner of the catch tube (i.e. the
    corner of the catch tube and the central trench). The location of the bottom right corner is inferred from this data.

    """
    def __init__(self, location_model, image):
        super(KymographAnnotator, self).__init__()
        self._done = False
        while not self._done:
            self._start()
            if not self._done:
                self._reset()

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
                self._clear()
                self._decrement_channel()
        elif human_input.key == 'right':
            if not self._coordinates:
                self._clear()
                self._increment_channel()

    def _decrement_channel(self):
        if self._current_channel_number == 1:
            self._current_channel_number = Constants.NUM_CATCH_CHANNELS
        else:
            self._current_channel_number -= 1

    def _increment_channel(self):
        if self._current_channel_number == Constants.NUM_CATCH_CHANNELS:
            self._current_channel_number = 1
        else:
            self._current_channel_number += 1

    def _clear(self):
        self._erase_all_points()
        self._close()

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
        self._fig.suptitle("Channel: " + str(self._current_channel_number), fontsize=20)
        self._ax.imshow(self._current_image_slice.image_data, cmap='gray')
        self._ax.autoscale(False)
        self._draw_existing_data()
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