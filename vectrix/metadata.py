import re

from enum import IntEnum

"""Represents a vectrix metadata.

https://developer.vectrix.io/dev/components/output#metadata-structure
"""
class MetadataElement():
    def __init__(self, priority, value, link=None):
        self._priority = priority
        self._value = value
        self._link = link

        if link == None and isinstance(value, str):
            url = re.search(r"(?P<url>https?://[^\s]+)", value)
            if url != None:
                self._link = url.group()

    """Range between -1 and 100 that denotes the priority of the MetadataElement"""
    @property
    def priority(self):
        return self._priority

    """The value of the MetaDataElement"""
    @property
    def value(self):
        return self._value

    """Link to relevant information about the MetadataElement"""
    @property
    def link(self):
        return self._link

    """Provides a dictionary representation of the Metadata.

    This should be invoked before adding the Metadata to the Asset or Issue
    """
    def to_dict(self):
        result = {
            'priority': int(self.priority),
            'value': self.value
        }

        if self.link != None:
            result['link'] = self.link

        return result


"""Enum for the metadata priority

https://developer.vectrix.io/dev/components/output#metadata-priority-system
"""
class MetadataPriority(IntEnum):
    DO_NOT_SURFACE = -1
    LOW = 0
    MEDIUM = 50
    HIGH = 100
