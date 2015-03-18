"""
Coordinates all quantification.

Creates an ND2Reader and an ImageReader as needed.
Determines dependencies and doesn't create ImageReader until necessary.
Passes objects to each other as needed (so Fluorescence can get the Location and Annotation models it needs)

"""