from fylm.model.coordinates import Coordinates


class HumanInput(object):
    """
    A wrapper around the matplotlib event object

    """
    def __init__(self, event):
        self._key = None
        self._button_clicked = None
        self._x = None
        self._y = None
        self._parse_event(event)

    def _parse_event(self, event):
        if event.name == 'button_press_event':
            self._parse_mouse_event(event)
        elif event.name == 'key_press_event':
            self._parse_keyboard_event(event)

    def _parse_mouse_event(self, event):
        # ignore mouse clicks that don't happen on the canvas
        if event.inaxes is not None:
            self._button_clicked = event.button
            # since we're dealing with exact pixels we always want integers
            self._x = int(event.xdata)
            self._y = int(event.ydata)

    def _parse_keyboard_event(self, event):
        self._key = event.key

    @property
    def left_click(self):
        return self._button_clicked == 1

    @property
    def middle_click(self):
        return self._button_clicked == 2

    @property
    def right_click(self):
        return self._button_clicked == 3

    @property
    def coordinates(self):
        return Coordinates(x=self._x, y=self._y)

    @property
    def key(self):
        return self._key

    @property
    def mouse_event(self):
        return self._button_clicked is not None

    @property
    def key_event(self):
        return self._key is not None