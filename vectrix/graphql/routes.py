from enum import Enum


class GraphQLRoutes(Enum):
    """
    Includes all routes for GraphQL API
    """

    GET_STATE = """
    query {
        deployment {
            state
        }
    }
    """

    GET_CREDENTIALS = """
    query {
        deployment {
            credentials
        }
    }
    """

    GET_LAST_SCAN_RESULTS = """
    query {
        deploymentLastScanResults {
            assets
            issues
            events
        }
    }
    """

    CREATE_AWS_SESSION = """
    mutation ($input: AwsSessionCreateInput!) {
        awsSessionCreate(input: $input){
            errors
            awsSession {
                accessKeyId
                secretAccessKey
                sessionToken
            }
        }
    }
    """

    CREATE_LOG = """
    mutation ($input: DeploymentLogInput!) {
        deploymentLogCreate(input: $input){
            errors
            deploymentLog {
                id
                message
                logType {
                    visibility
                    type
                }
            }
        }
    }
    """

    OUTPUT_RESULTS = """
    mutation($input: DeploymentScanEntryInput!) {
        deploymentScanEntryCreate(input: $input) {
            errors
        }
    }
    """
