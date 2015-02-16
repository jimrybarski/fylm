from fylm.service.interactor.base import HumanInteractor
from fylm.service.utilities import FileInteractor
import logging
import numpy as np
from matplotlib import pyplot as plt
from skimage.color import gray2rgb
from fylm.model.annotation import AnnotationLine
from fylm.service.reader import Reader

log = logging.getLogger(__name__)


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
                   "c": self._change_state,
                   "escape": self._clear,
                   "left": self._previous_channel,
                   "right": self._next_channel,
                   "up": self._next_time_period,
                   "down": self._previous_time_period,
                   "q": self._shutdown
                   }
        if human_input.key in actions.keys():
            actions[human_input.key]()

    def _change_state(self):
        self.current_annotation.change_state(self._annotation_model_set.current_time_period)
        self._refresh_data()
        self._clear()

    def _shutdown(self):
        self._done = True
        self._close()

    def _delete_last_line(self):
        self.current_annotation.delete_last_line(self._annotation_model_set.current_time_period)
        self._refresh_data()
        self._redraw()

    def _save_line(self):
        annotation_line = AnnotationLine()
        annotation_line.time_period = self._annotation_model_set.current_time_period
        annotation_line.set_coordinates(self._coordinates)
        self.current_annotation.add_line(annotation_line)
        self._refresh_data()

    def _refresh_data(self):
        file_interactor = FileInteractor(self.current_annotation)
        file_interactor.write_text()
        Reader().read(self.current_annotation, expect_missing_file=True)
        self._erase_all_points()
        self._redraw()

    def _previous_channel(self):
        self._annotation_model_set.decrement_channel()
        self._clear()

    def _next_channel(self):
        self._annotation_model_set.increment_channel()
        self._clear()

    def _previous_time_period(self):
        self._annotation_model_set.decrement_time_period()
        self._clear()

    def _next_time_period(self):
        self._annotation_model_set.increment_time_period()
        self._clear()

    def _clear(self):
        self._erase_all_points()
        self._close()

    def _redraw(self):
        result_array = np.zeros(self._image.shape)
        for y_list, x_list in self.current_annotation.points(self._annotation_model_set.current_time_period):
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
        time_period = self._annotation_model_set.current_time_period
        self._fig.suptitle("Time Period %s/%s FOV: %s Channel: %s State: %s" % (time_period,
                           self._annotation_model_set.max_time_period,
                           self.current_annotation.field_of_view + 1,
                           self.current_annotation.channel_number + 1,
                           self.current_annotation.state), fontsize=20)
        self._image = self.current_annotation.get_image(time_period)
        self._im = self._ax.imshow(self._image, cmap='gray')
        self._ax.autoscale(False)
        self._redraw()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()