"""Represents a vectrix Event

https://developer.vectrix.io/dev/components/output#events
"""
class Event():
    def __init__(self):
        self._display_name = None
        self._event = None
        self._event_time = None
        self._metadata = None

    """The identifier of the event. Displayed to customers"""
    @property
    def display_name(self):
        return self._display_name

    """Identifies the type of the event"""
    @property
    def event(self):
        return self._event

    """The time the event was detected"""
    @property
    def event_time(self):
        return self._event_time

    """Dictionary containing relevant information about the Event"""
    @property
    def metadata(self):
        return self._metadata

    def to_dict(self):
        return {
            "display_name": self._display_name,
            "event": self._event,
            "event_time": self._event_time,
            "metadata": self._metadata
        }
