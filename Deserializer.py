

class Deserializer:

    def __init__(self, deserialize_dict, default_header, split=False, default_sep=","):
        self.default_header = tuple(default_header)
        self.deserialize_dict = deserialize_dict
        self.default_sep = default_sep
        self.split = split

    def __call__(self, line):
        return self.deserialize(line)

    def deserialize(self, line, header=None, sep=None,):

        if sep is None:
            sep = self.default_sep

        if header is None:
            header = self.default_header

        if self.split:
            if sep:
                line = line.split(sep)
            else:
                line = line.split(self.default_sep)
                
        return {key: self.deserialize_dict[key](val) for key, val in zip(header, line)}
