class Info:
    description = 'Some information'

    def __init__(self,
                 source,
                 value,
                 extractor=None):
        """
        :param source:    Source from where the information is discovered.
        :param value:     Value of the infomation to be represented.
        :param extractor: ``InfoExtractor`` class used to extract the
                          information.
        """
        self.source = source
        self._value = value
        self.extractor = extractor

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self.__class__.__name__
