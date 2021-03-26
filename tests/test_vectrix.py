import pytest
import json
from pytest_mock import mocker
from tests import vectrix

from .test_assets import TestAsset
from .test_issues import TestIssue
from .test_events import TestEvent
from vectrix.graphql.routes import GraphQLRoutes

correct_asset = [
    {
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
        "display_name": "Bucket: Storage Bucket created",
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


class TestVectrixUtils():

    def test_vectrix_output(self):
        vectrix.output(assets=correct_asset,
                       issues=correct_issue, events=correct_event)

    def test_vectrix_output_bad_asset_type(self):
        bad_asset = [
            {
                "type": "Aws_s3_bucket",  # Vendors aren't allowed to be caps
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
        ]
        with pytest.raises(ValueError) as excinfo:
            vectrix.output(assets=bad_asset, issues=correct_issue,
                           events=correct_event)
        assert 'asset type vendor instantiation is required to be all lowercase' == str(
            excinfo.value).split(".")[0]

    def test_vectrix_output_bad_asset_type2(self):
        bad_asset = [
            {
                "type": "aws_s3_Bucket",  # Resources aren't allowed to be PascalCase
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
        ]
        with pytest.raises(ValueError) as excinfo:
            vectrix.output(assets=bad_asset, issues=correct_issue,
                           events=correct_event)
        assert 'asset type service and resource instantiations are required to follow camelCase for multiple words' == str(
            excinfo.value).split(".")[0]

    def test_vectrix_output_bad_asset_display_name(self):
        bad_asset = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id",
                "display_name": "Sample ID",  # Display names need to be key/values denoted by colons
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
        assert "asset dict key 'display_name' requires a colon that separates a key and value" == str(
            excinfo.value).split(".")[0]

    def test_vectrix_output_bad_metadata(self):
        bad_asset_metadata = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id",
                "display_name": "Bucket: Sample ID",
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

    def test_vectrix_output_bad_metadata_value(self):
        bad_asset_metadata = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id",
                "display_name": "Bucket: Sample ID",
                "link": "https://localhost.com",
                "metadata": {
                        "aws_s3_bucket_name": {
                            # Priority is only allowed to be between -1 and 100 (inclusive)
                            "priority": -2,
                            "value": {"sample-id"}
                        }
                }
            }
        ]

        with pytest.raises(ValueError) as excinfo:
            vectrix.output(assets=bad_asset_metadata, issues=correct_issue,
                           events=correct_event)
        assert "metadata element aws_s3_bucket_name key 'value' needs to be either (1) str or (2) list of str's" == str(
            excinfo.value).split(".")[0]

    def test_vectrix_output_bad_metadata_value_2(self):
        bad_asset_metadata = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id",
                "display_name": "Bucket: Sample ID",
                "link": "https://localhost.com",
                "metadata": {
                        "aws_s3_bucket_name": {
                            # Priority is only allowed to be between -1 and 100 (inclusive)
                            "priority": -2,
                            "value": [{"sample-id"}]
                        }
                }
            }
        ]

        with pytest.raises(ValueError) as excinfo:
            vectrix.output(assets=bad_asset_metadata, issues=correct_issue,
                           events=correct_event)
        assert "metadata element aws_s3_bucket_name key 'value' can be list, but each element in the list has to be 'str'" == str(
            excinfo.value).split(".")[0]

    def test_vectrix_output_bad_metadata_link(self):
        bad_asset_metadata = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id",
                "display_name": "Bucket: Sample ID",
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

    def test_vectrix_output_disallowed_event_key(self):
        bad_event_key = [
            {
                "type": "aws_s3_bucket",
                "event": "S3 Bucket Created",
                "event_time": 1596843510,
                "display_name": "Bucket: Storage Bucket created",
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

    def test_vectrix_set_state(self):
        assert vectrix.get_state() == {}
        vectrix.set_state({'1': '1'})
        vectrix.set_state({'2': '2'})
        assert vectrix.get_state() == {'1': '1', '2': '2'}

    def test_vectrix_get_state(self):
        assert vectrix.get_state() == {'1': '1', '2': '2'}

    def test_vectrix_unset_state(self):
        vectrix.unset_state('2')
        vectrix.unset_state('1')
        assert vectrix.get_state() == {}

    def test_vectrix_get_last_scan_results(self):
        results = vectrix.get_last_scan_results()
        check_val = {"assets": correct_asset,
                     "issues": correct_issue, "events": correct_event}
        assert results == check_val

    def test_vectrix_output_allow_typed_input(self):
        vectrix.output(assets=[TestAsset()] + correct_asset,
                       issues=[TestIssue()] + correct_issue,
                       events=[TestEvent()] + correct_event)

    def test_vectrix_output_formatting(self, mocker):
        # Test to verify the variables are properly formatted
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentScanEntryCreate": {
                "errors": []
            }
        }

        vectrix.output(assets=correct_asset, issues=correct_issue, events=correct_event)

        correct_call = [mocker.call(variables={'input': {'assets': [{'type': 'aws_s3_bucket', 'id': 'arn:aws:s3:::sample-id', 'displayName': 'Bucket: Sample ID', 'link': 'https://localhost.com', 'metadata': '{"aws_s3_bucket_name": {"priority": 50, "value": "sample-id"}}'}], 'issues': [{'issue': 'Public S3 Bucket', 'assetId': ['arn:aws:s3:::sample-id'], 'metadata': '{"aws_s3_bucket_name": {"priority": -1, "value": "sample-id"}}'}], 'events': [
                                    {'event': 'S3 Bucket Created', 'eventTime': 1596843510, 'displayName': 'Bucket: Storage Bucket created', 'metadata': '{"aws_s3_bucket_name": {"priority": -1, "value": "sample-id"}, "aws_s3_bucket_arn": {"priority": -1, "value": "sample-id"}, "aws_account_number": {"priority": -1, "value": "sample-id"}, "aws_region": {"priority": -1, "value": "sample-id"}}'}], 'state': '{}'}})]

        assert len(fake_graphql_client.mock_calls) == 1
        assert fake_graphql_client.has_calls(correct_call)

    def test_production_mode_get_credentials(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deployment": {
                "credentials": '{"AWS_ROLE_ARN":"dummy"}'
            }
        }

        returned_val = vectrix.get_credentials()
        assert returned_val == {"AWS_ROLE_ARN": "dummy"}

    def test_production_mode_create_aws_session(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        dummy_credentials = {
            "accessKeyId": "xxx",
            "secretAccessKey": "yyy",
            "sessionToken": "zzz"
        }
        fake_graphql_client.return_value = {
            "awsSessionCreate": {
                "awsSession": dummy_credentials,
                "errors": []
            }
        }
        fake_boto3 = mocker.patch("vectrix.main.boto3")
        fake_boto3.Session.return_value = dummy_credentials

        assert vectrix.create_aws_session(aws_role_arn="dummy", aws_external_id="dummy") == dummy_credentials

    def test_production_mode_get_last_scan_results(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentLastScanResults": {
                "assets": str(json.dumps(correct_asset)),
                "issues": str(json.dumps(correct_issue)),
                "events": str(json.dumps(correct_event))
            }
        }

        returned_val = vectrix.get_last_scan_results()
        assert returned_val == {"assets": correct_asset, "issues": correct_issue, "events": correct_event}

    def test_production_mode_log(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentLogCreate": {
                "errors": []
            }
        }
        correct_variables = {'input': {'logType': 'LOG', 'logVisibility': 'INTERNAL', 'logMessage': 'dummy'}}

        vectrix.log(message="dummy")
        assert len(fake_graphql_client.mock_calls) == 1
        assert fake_graphql_client.call_args[1]['variables'] == correct_variables

    def test_production_mode_external_log(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentLogCreate": {
                "errors": []
            }
        }
        correct_variables = {'input': {'logType': 'LOG', 'logVisibility': 'EXTERNAL', 'logMessage': 'dummy'}}

        vectrix.external_log(message="dummy")
        assert len(fake_graphql_client.mock_calls) == 1
        assert fake_graphql_client.call_args[1]['variables'] == correct_variables

    def test_production_mode_error(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentLogCreate": {
                "errors": []
            }
        }
        correct_variables = {'input': {'logType': 'ERROR', 'logVisibility': 'INTERNAL', 'logMessage': 'dummy'}}

        vectrix.error(error="dummy")
        assert len(fake_graphql_client.mock_calls) == 1
        assert fake_graphql_client.call_args[1]['variables'] == correct_variables

    def test_production_mode_external_error(self, mocker):
        fake_pm = mocker.patch("vectrix.main.PRODUCTION_MODE")
        fake_pm = True
        fake_graphql_client = mocker.patch("vectrix.main.graphql_client")
        fake_graphql_client.return_value = {
            "deploymentLogCreate": {
                "errors": []
            }
        }
        correct_variables = {'input': {'logType': 'ERROR', 'logVisibility': 'EXTERNAL', 'logMessage': 'dummy'}}

        vectrix.external_error(error="dummy")
        assert len(fake_graphql_client.mock_calls) == 1
        assert fake_graphql_client.call_args[1]['variables'] == correct_variables
