import pytest
import json
from pytest_mock import mocker

from vectrix.graphql.client import graphql_client
from vectrix.graphql.routes import GraphQLRoutes
from vectrix.graphql.utils import snake_case_to_camel_case
from vectrix.graphql.utils import vectrix_item_converter


class TestraphQLUtils:

    def test_snake_case_to_camel_case(self):
        test_string_1 = "snake_case"
        test_string_2 = "alreadyInProperCase"
        test_recursion = {
            "test_test": {
                "another_one": {
                    "one_more": 1
                }
            }
        }
        correct_recursion_answer = {
            "testTest": {
                "anotherOne": {
                    "oneMore": 1
                }
            }
        }
        assert snake_case_to_camel_case(test_string_1) == "snakeCase"
        assert snake_case_to_camel_case(test_string_2) == "alreadyInProperCase"
        assert correct_recursion_answer == snake_case_to_camel_case(test_recursion)

    def test_snake_case_to_camel_case_exception(self):
        with pytest.raises(Exception) as excinfo:
            snake_case_to_camel_case([])
        assert "Invalid input object type provided" in str(excinfo.value)

    def test_vectrix_item_converter(self):

        test_assets = [
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id-model",
                "display_name": "Bucket: Sample ID",
                "link": "https://localhost.com",
                "metadata": {
                        "aws_s3_bucket_name": {
                            "priority": 50,
                            "value": "sample-id"
                        }
                }
            },
            {
                "type": "aws_s3_bucket",
                "id": "arn:aws:s3:::sample-id-1",
                "display_name": "Bucket: Sample ID1",
                "link": "https://localhost.com",
                "metadata": {
                        "aws_s3_bucket_name": {
                            "priority": 50,
                            "value": "sample-id"
                        }
                }
            }
        ]

        returned_vals = vectrix_item_converter(test_assets)

        for index, val in enumerate(returned_vals):
            assert isinstance(val['metadata'], str) is True
            assert json.loads(val['metadata']) == json.loads(returned_vals[index]['metadata'])
            assert 'display_name' not in val
            assert 'displayName' in val


class TestGraphqlClient:

    def test_graphql_client_pass(self, mocker):
        mocked_requests = mocker.patch("vectrix.graphql.client.requests")
        fake_post = mocker.Mock()
        fake_post.status_code = 200
        fake_post.json.return_value = {
            "data": {
                "dummy": 1
            }
        }
        mocked_requests.post.return_value = fake_post

        assert graphql_client(route=GraphQLRoutes.GET_STATE) == {"dummy": 1}

    def test_graphql_client_error(self, mocker):

        mocked_requests = mocker.patch("vectrix.graphql.client.requests")
        fake_post = mocker.Mock()
        fake_post.status_code = 400
        mocked_requests.post.return_value = fake_post

        assert graphql_client(route=GraphQLRoutes.GET_STATE) is None
