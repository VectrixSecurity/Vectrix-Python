from tests import Event

correct_event = {
    "event": "S3 Bucket Created",
    "event_time": 1596843510,
    "display_name": "Bucket: storage-bucket",
    "metadata": {
        "aws_s3_bucket_name": {
            "priority": 90,
            "value": "storage-bucket"
        }
    }
}

class TestEvent(Event):
    def __init__(self):
        super().__init__()
        self._display_name = "Bucket: storage-bucket"
        self._event = "S3 Bucket Created"
        self._event_time = 1596843510
        self._metadata = {
            "aws_s3_bucket_name": {
                "priority": 90,
                "value": "storage-bucket"
            }
        }

    __test__ = False

def test_event_to_dict():
    assert TestEvent().to_dict() == correct_event