import logging

# Show us all log messages in the terminal as the program runs
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# If any errors occur, write those log messages to a file in addition to showing them on the screen
# We're doing this since Jim keeps accidentally closing the terminal and losing important debug information
error_handler = logging.FileHandler("/var/log/fylm_error.log")
error_handler.setLevel(logging.ERROR)

debug_handler = logging.FileHandler("/var/log/fylm.log")
debug_handler.setLevel(logging.DEBUG)

# Actually instantiate the logger
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(stream_handler)
log.addHandler(error_handler)
log.addHandler(debug_handler)