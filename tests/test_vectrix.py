import pytest
from tests import vectrix

correct_asset = [
    {
        "type": "aws_s3_bucket",
        "id": "arn:aws:s3:::sample-id",
        "display_name": "Sample ID",
        "link": "https://localhost.com",
        "metadata": {
                "aws_s3_bucket_name": {
                    "priority": 50,
                    "value": "sample-id"
                }
        }
    }
]

correct_issue = [
    {
        "issue": "Public S3 Bucket",
        "asset_id": ["arn:aws:s3:::sample-id"],
        "metadata": {
            "aws_s3_bucket_name": {
                "priority": -1,
                "value": "sample-id"
            }
        }
    }
]

correct_event = [
    {
        "event": "S3 Bucket Created",
        "event_time": 1596843510,
        "display_name": "Storage Bucket created",
        "metadata": {
            "aws_s3_bucket_name": {
                "priority": -1,
                "value": "sample-id"
            },
            "aws_s3_bucket_arn": {
                "priority": -1,
                "value": "sample-id"
            },
            "aws_account_number": {
                "priority": -1,
                "value": "sample-id"
            },
            "aws_region": {
                "priority": -1,
                "value": "sample-id"
            }
        }
    }
]


def test_vectrix_output():
    vectrix.output(assets=correct_asset,
                   issues=correct_issue, events=correct_event)


def test_vectrix_output_bad_asset_type():
    bad_asset = [
        {
            "type": "Aws_s3_bucket",  # Vendors aren't allowed to be caps
            "id": "arn:aws:s3:::sample-id",
            "display_name": "Sample ID",
            "link": "https://localhost.com",
            "metadata": {
                    "aws_s3_bucket_name": {
                        "priority": 50,
                        "value": "sample-id"
                    }
            }
        }
    ]
    with pytest.raises(ValueError) as excinfo:
        vectrix.output(assets=bad_asset, issues=correct_issue,
                       events=correct_event)
    assert 'asset type vendor instantiation is required to be all lowercase' == str(
        excinfo.value).split(".")[0]


def test_vectrix_output_bad_asset_type2():
    bad_asset = [
        {
            "type": "aws_s3_Bucket",  # Resources aren't allowed to be PascalCase
            "id": "arn:aws:s3:::sample-id",
            "display_name": "Sample ID",
            "link": "https://localhost.com",
            "metadata": {
                    "aws_s3_bucket_name": {
                        "priority": 50,
                        "value": "sample-id"
                    }
            }
        }
    ]
    with pytest.raises(ValueError) as excinfo:
        vectrix.output(assets=bad_asset, issues=correct_issue,
                       events=correct_event)
    assert 'asset type service and resource instantiations are required to follow camelCase for multiple words' == str(
        excinfo.value).split(".")[0]


def test_vectrix_output_bad_metadata():
    bad_asset_metadata = [
        {
            "type": "aws_s3_bucket",
            "id": "arn:aws:s3:::sample-id",
            "display_name": "Sample ID",
            "link": "https://localhost.com",
            "metadata": {
                    "aws_s3_bucket_name": {
                        # Priority is only allowed to be between -1 and 100 (inclusive)
                        "priority": -2,
                        "value": "sample-id"
                    }
            }
        }
    ]

    with pytest.raises(ValueError) as excinfo:
        vectrix.output(assets=bad_asset_metadata, issues=correct_issue,
                       events=correct_event)
    assert "metadata 'priority' key is only allowed to be between -1 and 100 (inclusive)" == str(
        excinfo.value).split(".")[0]


def test_vectrix_output_bad_metadata_link():
    bad_asset_metadata = [
        {
            "type": "aws_s3_bucket",
            "id": "arn:aws:s3:::sample-id",
            "display_name": "Sample ID",
            "link": "https://localhost.com",
            "metadata": {
                    "aws_s3_bucket_name": {
                        "priority": -1,
                        "value": "sample-id",
                        "link": "http://insecure-link.com"
                    }
            }
        }
    ]

    with pytest.raises(ValueError) as excinfo:
        vectrix.output(assets=bad_asset_metadata, issues=correct_issue,
                       events=correct_event)
    assert "Only secure links are allowed in metadata elements (HTTPS)" == str(
        excinfo.value).split(".")[0]


def test_vectrix_output_disallowed_event_key():
    bad_event_key = [
        {
            "type": "aws_s3_bucket",
            "event": "S3 Bucket Created",
            "event_time": 1596843510,
            "display_name": "Storage Bucket created",
            "metadata": {
                "aws_s3_bucket_name": {
                    "priority": -1,
                    "value": "sample-id"
                },
                "aws_s3_bucket_arn": {
                    "priority": -1,
                    "value": "sample-id"
                }
            }
        }
    ]

    with pytest.raises(ValueError) as excinfo:
        vectrix.output(assets=correct_asset, issues=correct_issue,
                       events=bad_event_key)
    assert "event dict does not allow key 'type'" == str(
        excinfo.value).split(".")[0]


def test_vectrix_set_state():
    assert vectrix.get_state() == {}
    vectrix.set_state({'1': '1'})
    vectrix.set_state({'2': '2'})
    assert vectrix.get_state() == {'1': '1', '2': '2'}


def test_vectrix_get_state():
    assert vectrix.get_state() == {'1': '1', '2': '2'}


def test_vectrix_unset_state():
    vectrix.unset_state('2')
    vectrix.unset_state('1')
    assert vectrix.get_state() == {}


def test_vectrix_get_last_scan_results():
    results = vectrix.get_last_scan_results()
    check_val = {"assets": correct_asset,
                 "issues": correct_issue, "events": correct_event}
    assert results == check_val
