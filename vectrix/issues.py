"""Represents a vectrix issue.

https://developer.vectrix.io/dev/components/output#issues
"""
class Issue():
    def __init__(self):
        self._asset_id = None
        self._issue = None
        self._metadata = None

    """The ids of the Assets affected by the issue"""
    @property
    def asset_id(self):
        return self._asset_id

    """Identifies the type of issue"""
    @property
    def issue(self):
        return self._issue

    """Dictionary containing relevant information about the Issue"""
    @property
    def metadata(self):
        return self._metadata

    """Provides a dictionary representation of the Issue.

    This should be invoked before adding the Issue to the issue output list
    """
    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'issue': self.issue,
            'metadata': self.metadata
        }
