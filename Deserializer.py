

class Deserializer:
    """
    Deserializer class
    Defines a process to transform a string (or a list of stings) into a dictionary.

    The string contains elements separated by a separator character, each of these elements
    are casted to the right type and stored in a dictionary.
    """

    def __init__(self, deserialize_dict, default_header, split=False, default_sep=","):
        """
        Parameters
        ----------
            deserialize_dict : dict
                dictionary object that maps a label to a fonction that deserialize objects of this label.
            default_header : tuple 
                list of the labels that corespond to the labels of the elements of the string.
            split : bool 
                True if the input is a list of string (the input string is already splitted).
            default_sep : str
                If split is False, default_sep is the default separator to use to split the input string.
        """

        self.default_header = tuple(default_header)
        self.deserialize_dict = deserialize_dict
        self.default_sep = default_sep
        self.split = split

    def __call__(self, line):
        """
        Shortcut to make the object callable and directly call the deserialize function.
        """

        return self.deserialize(line)

    def deserialize(self, line, header=None, sep=None):
        """
        Function to deserialize a string (or a list of strings) into a dictionary.

        Parameters
        ----------
        line : string or list of strings
            Input string or list of strings to deserialize.
        header : tuple 
            Labels of each element of the input string in the right order.
        sep : int 
            Separator character to use if the input is not already separated
            into the different labels

        Returns
        -------
        output : dict
            dictionary object that has for keys the elements of the header and
            for value the deserialized value of the input string.
        """

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
