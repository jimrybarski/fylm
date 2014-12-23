from abc import abstractmethod
from fylm.model.coordinates import Coordinates
from fylm.model.interactor import HumanInput
from matplotlib import pyplot as plt


class HumanInteractor(object):
    """
    Methods and tools to help create services that get information from a user.

    """
    def __init__(self):
        self._points = []
        self._coordinates = []
        self._results = None
        self._mouse_click_listener_id = None
        self._key_press_listener_id = None
        self._fig, self._ax = plt.subplots()
        self._listen()

    def _listen(self):
        self._mouse_click_listener_id = self._fig.canvas.mpl_connect('button_press_event', self._parse_event)
        self._key_press_listener_id = self._fig.canvas.mpl_connect('key_press_event', self._parse_event)

    def _close(self):
        self._fig.canvas.mpl_disconnect(self._mouse_click_listener_id)
        self._fig.canvas.mpl_disconnect(self._key_press_listener_id)
        plt.close()

    def _reset(self):
        self._fig, self._ax = plt.subplots()
        self._listen()

    def _add_point(self, x, y, marker='ro'):
        self._points.append(plt.plot(x, y, marker))
        self._coordinates.append(Coordinates(x=x, y=y))
        plt.draw()

    def _remove_last_point(self):
        try:
            self._points[-1][0].remove()
            del(self._points[-1])
            del(self._coordinates[-1])
            plt.draw()
        except IndexError:
            pass

    def _erase_all_points(self):
        for _ in range(len(self._points)):
                self._remove_last_point()

    def _parse_event(self, event):
        human_input = HumanInput(event)
        if human_input.mouse_event:
            self._on_mouse_click(human_input)
        elif human_input.key_event:
            self._on_key_press(human_input)

    @abstractmethod
    def _on_mouse_click(self, human_input):
        raise NotImplemented

    @abstractmethod
    def _on_key_press(self, human_input):
        raise NotImplemented

    @abstractmethod
    def _handle_results(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def _start(self, *args):
        """
        Should include something that shows the image, like plt.show(image_data)

        """
        raise NotImplemented