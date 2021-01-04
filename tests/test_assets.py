from tests import Asset

correct_asset = {
    "type": "aws_s3_bucket",
    "id": "arn:aws:s3:::sample-id",
    "display_name": "Bucket: Sample ID",
    "link": "https://localhost.com",
    "metadata": {
            "aws_s3_bucket_name": {
                "priority": 50,
                "value": "sample-id"
            }
    }
}


class TestAsset(Asset):
    def __init__(self):
        super().__init__()
        self._display_name = "Bucket: Sample ID"
        self._id = "arn:aws:s3:::sample-id"
        self._link = "https://localhost.com"
        self._metadata = {
            "aws_s3_bucket_name": {
                "priority": 50,
                "value": "sample-id"
            }
        }
        self._type = "aws_s3_bucket"

    __test__ = False


def test_asset_to_dict():
    assert TestAsset().to_dict() == correct_asset
