from tests import Issue

correct_issue = {
    "issue": "Public S3 Bucket",
    "asset_id": ["arn:aws:s3:::sample-id"],
    "metadata": {
        "aws_s3_bucket_name": {
            "priority": -1,
            "value": "sample-id"
        }
    }
}


class TestIssue(Issue):
    def __init__(self):
        super().__init__()
        self._issue = "Public S3 Bucket"
        self._asset_id = ["arn:aws:s3:::sample-id"]
        self._metadata = {
            "aws_s3_bucket_name": {
                "priority": -1,
                "value": "sample-id"
            }
        }

    __test__ = False


def test_issue_to_dict():
    assert TestIssue().to_dict() == correct_issue
