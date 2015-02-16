from fylm.service.errors import terminal_error
import skimage.io


class Reader(object):

    def read(self, model, expect_missing_file=False):
        """
        Opens the file associated with the model

        """
        actions = {"text": self.read_text,
                   "image": self.read_image,
                   "movie": lambda *x: None     # These are output only, we never need to load them
                   }
        return actions[model.kind](model, expect_missing_file)

    @staticmethod
    def read_text(model, expect_missing_file):
        try:
            with open(model.path) as f:
                # strip raw data to remove trailing newlines, so splitting on newline can't produce an empty value
                data = f.read(-1).strip().split("\n")
                model.load(data)
        except Exception as e:
            if expect_missing_file:
                return None
            else:
                terminal_error("Could not load text file: %s because: %s" % (model.path, str(e)))
        else:
            return True

    @staticmethod
    def read_image(model, expect_missing_file):
        try:
            image = skimage.io.imread(model.path)
            model.load(image)
        except Exception as e:
            terminal_error("Could not load image file: %s because: %s" % (model.path, str(e)))
        else:
            return True