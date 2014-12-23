from fylm.service.interactor.base import HumanInteractor
import logging
from matplotlib import pyplot as plt

log = logging.getLogger("fylm")


class ApproximateChannelFinder(HumanInteractor):
    """
    Gets the user to click on the notches in the top-left and bottom-right channels, then uses those coordinates to guess the approximate location of all 28 channels.
    Returns an ImageSliceSet with 28 ImageSlices, each with the image data of what is hopefully a catch channel.

    """
    def __init__(self, image_data):
        super(ApproximateChannelFinder, self).__init__()
        self._image_data = image_data
        self._start()

    def _on_mouse_click(self, human_input):
        if human_input.left_click and len(self._coordinates) < 2:
            self._add_point(human_input.coordinates.x, human_input.coordinates.y)
        if human_input.right_click:
            self._remove_last_point()

    def _on_key_press(self, human_input):
        if human_input.key == 'enter' and len(self._coordinates) == 2:
            self._close()
            self._handle_results()
        elif human_input.key == 'escape':
            self._erase_all_points()

    def _start(self):
        self._ax.imshow(self._image_data, cmap='gray')
        self._ax.autoscale(False)
        plt.show()

    def _handle_results(self):
        self._results = (self._coordinates[0], self._coordinates[1])

    @property
    def results(self):
        return self._results[0].x, self._results[0].y, self._results[1].x, self._results[1].y