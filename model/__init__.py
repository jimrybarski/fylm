import os


class Experiment(object):
    """
    Models the files and directory structure of experimental data and results. Determines
    what has been done in terms of processing and what remains to be done.

    """
    pass


class Metadata(object):
    """
    A much cleaner version of the metadata file that is provided by Elements.

    """
    pass


class ImageCorrections(object):
    """
    Translational and rotational offsets for each frame.

    """
    pass


class ChannelLocations(object):
    """
    Locations of the channels.

    """
    pass


class KymographAnnotation(object):
    """
    Holds coordinates of cell pole lines provided by a user.

    """
    pass


class FluorescenceData(object):
    """
    Holds fluorescence intensity for channels.

    """
    pass


