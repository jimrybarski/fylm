class Coordinates(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return float(self._x)

    @property
    def y(self):
        return float(self._y)

    def __eq__(self, other):
        """
        Determines if this object is the same point as another. Used for unit testing only for now.

        """
        return other.x == self.x and other.y == self.y