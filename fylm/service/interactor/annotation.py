from fylm.service.interactor.base import HumanInteractor
from fylm.service.utilities import FileInteractor
import logging
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import gray2rgb
from fylm.model.annotation import AnnotationLine
from fylm.service.reader import Reader

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
                   "escape": self._clear,
                   "left": self._previous_channel,
                   "right": self._next_channel,
                   "up": self._next_timepoint,
                   "down": self._previous_timepoint
                   }
        if human_input.key in actions.keys():
            actions[human_input.key]()

    def _delete_last_line(self):
        raise NotImplemented

    def _save_line(self):
        annotation_line = AnnotationLine()
        annotation_line.timepoint = self._annotation_model_set.current_timepoint
        annotation_line.set_coordinates(self._coordinates)
        self.current_annotation.add_line(annotation_line)
        file_interactor = FileInteractor(self.current_annotation)
        file_interactor.write_text()
        Reader().read(self.current_annotation, expect_missing_file=True)
        self._erase_all_points()
        self._redraw()

    def _previous_channel(self):
        self._annotation_model_set.decrement_channel()

    def _next_channel(self):
        self._annotation_model_set.increment_channel()

    def _previous_timepoint(self):
        self._annotation_model_set.decrement_timepoint()
        self._clear()

    def _next_timepoint(self):
        self._annotation_model_set.increment_timepoint()
        self._clear()

    def _clear(self):
        self._erase_all_points()
        self._close()

    def _redraw(self):
        result_array = np.zeros(self._image.shape)
        for y_list, x_list in self.current_annotation.points(self._annotation_model_set.current_timepoint):
            result_array[y_list, x_list] = 1
        line_indices = np.where(result_array == 1)
        active_image = gray2rgb(np.copy(self._image))
        active_image[line_indices] = self._label_line_color
        self._im.set_data(active_image)
        plt.draw()

    @property
    def current_annotation(self):
        return self._annotation_model_set.current_model

    def _start(self):
        # Refresh the lines from disk in case we saved some during this session
        Reader().read(self.current_annotation, expect_missing_file=True)
        timepoint = self._annotation_model_set.current_timepoint
        self._fig.suptitle("Timepoint %s/%s FOV: %s Channel: %s" % (timepoint,
                                                                    self._annotation_model_set.max_timepoint,
                                                                    self.current_annotation.field_of_view,
                                                                    self.current_annotation.channel_number), fontsize=20)
        self._image = self.current_annotation.get_image(timepoint)
        self._im = self._ax.imshow(self._image, cmap='gray')
        self._ax.autoscale(False)
        self._redraw()
        plt.show()