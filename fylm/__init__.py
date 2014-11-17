import logging

log = logging.getLogger("fylm")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)