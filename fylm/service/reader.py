from fylm.service.errors import terminal_error


class ReaderService(object):

    @staticmethod
    def read(model):
        """
        Opens the file associated with the model,
        """
        try:
            with open(model.path) as f:
                # strip raw data to remove trailing newlines, so splitting on newline can't produce an empty value
                data = f.read(-1).strip().split("\n")
                model.load(data)
        except Exception as e:
            terminal_error("Could not read file: %s because: %s" % (model.path, str(e)))
        else:
            return True
