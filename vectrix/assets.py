"""Represents a vectrix asset.

https://developer.vectrix.io/dev/components/output#assets
"""
class Asset():
    def __init__(self):
        self._display_name = None
        self._id = None
        self._link = None
        self._metadata = None
        self._type = None

    """Displayed name of the Asset"""
    @property
    def display_name(self):
        return self._display_name

    """Static and unique identifier of the Asset"""
    @property
    def id(self):
        return self._id

    """Link to where end user can find more information about the Asset"""
    @property
    def link(self):
        return self._link

    """Dictionary containing relevant information about the Asset"""
    @property
    def metadata(self):
        return self._metadata

    """The type of the Asset"""
    @property
    def type(self):
        return self._type

    """Provides a dictionary representation of the Asset.

    This should be invoked before adding the Asset to the asset output list
    """
    def to_dict(self):
        result = {
            "display_name": self.display_name,
            "id": self.id,
            "metadata": self.metadata,
            "type": self.type
        }

        if self.link != None:
            result['link'] = self.link

        return result
