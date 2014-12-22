from fylm.model.constants import Constants
from fylm.service.interactor.base import HumanInteractor
import logging
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import gray2rgb
from fylm.model.annotation import AnnotationLine

log = logging.getLogger("fylm")


class KymographAnnotator(HumanInteractor):
    """
    Gets the user to define the exact location of all 28 channels, one-by-one. The user clicks on the notch, then the top right corner of the catch tube (i.e. the
    corner of the catch tube and the central trench). The location of the bottom right corner is inferred from this data.

    """
    def __init__(self, annotation_model_set):
        super(KymographAnnotator, self).__init__()
        self._annotation_model_set = annotation_model_set
        self._done = False
        self._annotation = self._annotation_model_set.get_first_unfinished_model()
        self._current_channel_number = self._annotation.channel_number
        self._current_field_of_view = self._annotation.field_of_view
        self._line_indices = None
        self._im = None

        while not self._done:
            self._start()
            if not self._done:
                self._reset()

    @property
    def _user_line_color(self):
        """
        Color for lines manually created by user

        """
        return 65536, 36045, 0  # bright orange

    @property
    def _label_line_color(self):
        """
        Color for lines derived from labels

        """
        return 19660, 39321, 65536  # light blue

    def _on_mouse_click(self, human_input):
        if human_input.left_click:
            self._add_point(human_input.coordinates.x, human_input.coordinates.y)
        if human_input.right_click:
            self._remove_last_point()

    def _on_key_press(self, human_input):
        actions = {"d": self._delete_last_line,
                   "w": self._save_line,
                   "enter": self._save_kymograph,
                   "escape": self._clear,
                   "left": self._previous_channel,
                   "right": self._next_channel,
                   "up": self._next_timepoint,
                   "down": self._previous_timepoint
                   }
        actions[human_input.key]()

    def _delete_last_line(self):
        raise NotImplemented

    def _save_line(self):
        annotation_line = AnnotationLine()
        annotation_line.set_coordinates(self._coordinates)
        self._annotation.add_line(annotation_line)
        self._done = True
        self._redraw()

    def _save_kymograph(self):
        self._handle_results()
        self._increment_channel()
        self._clear()

    def _previous_channel(self):
        self._clear()
        self._decrement_channel()

    def _next_channel(self):
        self._clear()
        self._increment_channel()

    def _previous_timepoint(self):
        self._clear()
        self._decrement_timepoint()

    def _next_timepoint(self):
        self._clear()
        self._increment_timepoint()

    def _decrement_channel(self):
        # TODO: Add support for fields of view as well
        if self._current_channel_number == 1:
            self._current_channel_number = Constants.NUM_CATCH_CHANNELS
        else:
            self._current_channel_number -= 1

    def _increment_channel(self):
        if self._current_channel_number == Constants.NUM_CATCH_CHANNELS:
            self._current_channel_number = 1
        else:
            self._current_channel_number += 1

    def _decrement_timepoint(self):
        self._annotation_model_set.decrement_timepoint()

    def _increment_timepoint(self):
        self._annotation_model_set.increment_timepoint()

    def _clear(self):
        self._erase_all_points()
        self._close()

    def _handle_results(self):
        if self._coordinates:
            # do stuff
            pass
        self._clear()

    def _redraw(self):
        result_array = np.zeros(self._annotation.current_image.shape)
        for y_list, x_list in self._annotation.points:
            result_array[y_list, x_list] = 1
        line_indices = np.where(result_array == 1)

        active_image = gray2rgb(np.copy(self._annotation.current_image))
        active_image[line_indices] = self._label_line_color
        self._im.set_data(active_image)
        plt.draw()

    def _start(self):
        self._fig.suptitle("Timepoint %s/%s FOV: %s Channel: %s" % (self._annotation.current_timepoint,
                                                                    self._annotation.max_timepoint,
                                                                    self._annotation.field_of_view,
                                                                    self._current_channel_number), fontsize=20)
        self._im = self._ax.imshow(self._annotation.current_image, cmap='gray')
        self._ax.autoscale(False)
        self._redraw()
        plt.show()