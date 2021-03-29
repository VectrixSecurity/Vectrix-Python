"""
Vectrix Detection Pack Utilities
"""
import boto3
import os
import json
import logging

from .assets import Asset
from .events import Event
from .issues import Issue

from .graphql.routes import GraphQLRoutes
from .graphql.client import graphql_client
from .graphql.utils import vectrix_item_converter
from .checks import output_type_check
from .settings import PRODUCTION_MODE
from .sentry import activate_sentry


class VectrixUtils:
    def __init__(self):
        if not PRODUCTION_MODE:
            print("**** Vectrix Detection Pack is in local development mode ****")
            self.__init_development_mode()
            logging.basicConfig(
                filename=(os.getcwd() + '/.vectrix/vectrix-detection-pack.log'), level=logging.WARNING)  # TODO Test logging level change with .error and .warning
        else:
            activate_sentry(os.environ.get('SENTRY_DSN', None))
            self.deployment_id = os.environ.get('DEPLOYMENT_ID')
            self.deployment_key = os.environ.get('DEPLOYMENT_KEY')
            self.auth_headers = {
                "DEPLOYMENT_ID": self.deployment_id, "DEPLOYMENT_KEY": self.deployment_key}
        self.state = self.__init_state()

        # There's some legacy reliance on production_mode being held within a class var
        self.production_mode = PRODUCTION_MODE

    def __init_state(self):
        """
        Initializes state depending on if the module is in production or not.
        If the module is in local development, it'll create a directory + module_state file that holds json of state (for continous state holding)
        """

        if (PRODUCTION_MODE):
            response = graphql_client(route=GraphQLRoutes.GET_STATE)
            deployment = response.get("deployment", None)
            state = json.loads(deployment.get("state", None))
            if state is None:
                raise Exception("Failed retrieving state from Vectrix API")
            return state
        else:
            state_file = os.getcwd() + "/.vectrix/module_state.json"
            if not os.path.exists(state_file):
                f = open(state_file, "w+")
                f.write(json.dumps({}))
                f.close()
            with open(state_file) as f:
                data = json.load(f)
            return data

    def __init_development_mode(self):
        """
        Create .vectrix directory within current directory to hold module state (only in local development mode)
        """
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'.vectrix')
        if not os.path.exists(final_directory):
            os.mkdir(final_directory)

    def __dev_hold_local_state(self, state):
        """
        This is called within set_state if the vectrix module is in local development and will sync state to the filesystem.
        """
        state_file = os.getcwd() + "/.vectrix/module_state.json"
        f = open(state_file, "w+")
        f.write(json.dumps(state))
        f.close()

    def __dev_hold_last_scan_results(self, results):
        """
        This is called within output if the vectrix module is in local development and will sync scan results to the filesystem.
        """
        state_file = os.getcwd() + "/.vectrix/last_scan_results.json"
        f = open(state_file, "w+")
        f.write(json.dumps(results))
        f.close()

    def __enforce_dict_input(self, assets, issues, events):
        """Check if Asset, Issue, or Event is an instance of its associated class. If so, convert to dict for further processing"""

        if assets is not None:
            for i in range(len(assets)):
                if isinstance(assets[i], Asset):
                    assets[i] = assets[i].to_dict()

        if issues is not None:
            for i in range(len(issues)):
                if isinstance(issues[i], Issue):
                    issues[i] = issues[i].to_dict()

        if events is not None:
            for i in range(len(events)):
                if isinstance(events[i], Event):
                    events[i] = events[i].to_dict()

    def get_state(self):
        """
        Retrieve state within the vectrix module. Utilize this method to retrieve state that was previously set with set_state()

        :returns: dict containing current state.
        """
        return self.state

    def set_state(self, new_state: dict):
        """
        Set state within the vectrix module. Utilize this method to add state to the module.
        This doesn't overwrite the current state, but rather performs a merge operation against the current state.

        :params: dict with containing new state to set.
        :returns: dict containing current state.
        """
        if not isinstance(new_state, dict):
            raise ValueError("set_state requires dict type parameter")

        merged_state = self.state.copy()
        merged_state.update(new_state)
        self.state = merged_state

        if PRODUCTION_MODE is False:
            self.__dev_hold_local_state(merged_state)
        return merged_state

    def unset_state(self, key: str):
        """
        unset_state will remove a key from the current state

        :params: (String) key to be removed from state
        :returns: (No return)
        """
        if not isinstance(key, str):
            raise ValueError(
                "unset_state requires str type parameter containing log message")
        self.state.pop(key, None)
        if PRODUCTION_MODE is False:
            self.__dev_hold_local_state(self.state)

    def output(self, *ignore, assets=None, issues=None, events=None):
        """
        output will send the identified assets, issues, and events to the Vectrix platform. This should always be called after a scan.

        :params: assets (list) - Keyword argument of the assets identified during a scan.
        :params: issues (list) - Keyword argument of the issues identified during a scan.
        :params: events (list) - Keyword argument of the events identified during a scan.
        :returns: (No return)
        """
        self.__enforce_dict_input(assets, issues, events)
        output_type_check(assets, issues, events)
        if PRODUCTION_MODE is False:
            print("(DEV MODE) Vectrix Detection Pack Output:")
            print("**** ASSETS ****")
            print(json.dumps(assets))
            print("**** ISSUES ****")
            print(json.dumps(issues))
            print("**** EVENTS ****")
            print(json.dumps(events))
            self.__dev_hold_last_scan_results(
                {"assets": assets, "issues": issues, "events": events})
        else:
            formatted_input = {
                "assets": vectrix_item_converter(assets),
                "issues": vectrix_item_converter(issues),
                "events": vectrix_item_converter(events),
                "state": str(json.dumps(self.state))
            }
            response = graphql_client(
                route=GraphQLRoutes.OUTPUT_RESULTS, variables={"input": formatted_input})
            deployment_scan = response.get("deploymentScanEntryCreate", None)
            errors = deployment_scan.get("errors", None)
            if len(errors) != 0:
                raise Exception(
                    f"Failed outputting scan results to Vectrix API: {str(errors)}")

    def get_credentials(self):
        """
        This will return applicable customer credentials to be used for restricted APIs. For more information, visit https://developer.vectrix.io/module-development/module-access

        :params: (None)
        :returns: dict of credentials (keys within dict depend on the cloud vendor, For more information, visit https://developer.vectrix.io/module-development/module-access)
        """
        if PRODUCTION_MODE is False:
            raise NotImplementedError(
                "get_credentials isn't allowed within local development, please handle yourself then implement once moving vectrix module to production")
        else:
            response = graphql_client(route=GraphQLRoutes.GET_CREDENTIALS)
            deployment = response.get("deployment", None)
            credentials = json.loads(deployment.get("credentials", None))
            if credentials is None:
                raise Exception(
                    "Failed retrieving credentials from Vectrix API")
            return credentials

    def create_aws_session(self, aws_role_arn=None, aws_external_id=None):
        """
        This will return an authenticated boto3 session to access a customer AWS environment. For more information, visit https://developer.vectrix.io/module-development/module-access/aws-access

        :param: aws_role_arn (String) - Customer AWS Role ARN (can be retrieved from get_credentials)
        :param: aws_external_id (String) - Customer AWS External ID (can be retrieved from get_credentials)
        :returns: authenticated boto3 session object
        """
        if PRODUCTION_MODE is False:
            raise NotImplementedError(
                "create_aws_session isn't allowed within local development, please handle yourself then implement once moving vectrix module to production")

        aws_variables = {
            "awsRoleArn": aws_role_arn,
            "awsExternalId": aws_external_id
        }

        response = graphql_client(route=GraphQLRoutes.CREATE_AWS_SESSION, variables={
                                  "input": aws_variables})
        mutation = response.get("awsSessionCreate", None)
        aws_session = mutation.get("awsSession", None)
        errors = mutation.get("errors", None)
        if len(errors) != 0:
            raise Exception(
                f"Error retreiving AWS Session from Vectrix API: {str(errors)}")

        access_key_id = aws_session.get("accessKeyId")
        secret_access_key = aws_session.get("secretAccessKey")
        session_token = aws_session.get("sessionToken")

        aws_session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token)

        return aws_session

    def get_last_scan_results(self):
        """
        This will return the last scan results of a module within a dictionary of keys 'assets' 'issues' and 'events' - For more information, visit https://developer.vectrix.io/module-development/module-state#last-scan-results
        """
        if PRODUCTION_MODE is False:
            scan_file = os.getcwd() + "/.vectrix/last_scan_results.json"
            if not os.path.exists(scan_file):
                return {"assets": [], "issues": [], "events": []}
            else:
                with open(scan_file) as f:
                    data = json.load(f)
                return data
        else:
            response = graphql_client(
                route=GraphQLRoutes.GET_LAST_SCAN_RESULTS)
            scan_results = response.get("deploymentLastScanResults")
            return {
                "assets": json.loads(scan_results['assets']),
                "issues": json.loads(scan_results['issues']),
                "events": json.loads(scan_results['events'])
            }

    def __log_sender(self, log_type: str, visibility: str, message: str):
        """
        Internal helper function to send logs to Vectrix API
        """

        api_input = {
            "logType": log_type,
            "logVisibility": visibility,
            "logMessage": message
        }
        response = graphql_client(
            route=GraphQLRoutes.CREATE_LOG, variables={"input": api_input})
        mutation = response.get("deploymentLogCreate")
        errors = mutation.get("errors")
        if len(errors) != 0:
            raise Exception(
                f"Error creating log in Vectrix API: {str(errors)}")

    def log(self, message: str):
        """
        Vectrix logs are internal logs for developers to create that are sent to the developer via our platform. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for log message
        :returns: (No return)
        """
        if not isinstance(message, str):
            raise ValueError(
                "log requires str type parameter containing log message")
        if PRODUCTION_MODE is False:
            logging.warning("VECTRIX LOG (INTERNAL): " + message)
        else:
            self.__log_sender(
                log_type="LOG", visibility="INTERNAL", message=message)

    def external_log(self, message: str):
        """
        Vectrix external logs are customer facing logs that our developers use to show what a module is doing within a scan. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for log message
        :returns: (No return)
        """
        if not isinstance(message, str):
            raise ValueError(
                "external_log requires str type parameter containing log message")
        if PRODUCTION_MODE is False:
            logging.warning("VECTRIX LOG (EXTERNAL): " + message)
        else:
            self.__log_sender(
                log_type="LOG", visibility="EXTERNAL", message=message)

    def error(self, error: str):
        """
        Vectrix errors are internal errors for developers to create that are sent to the developer via our platform. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for error message
        :returns: (No return)
        """
        if not isinstance(error, str):
            raise ValueError(
                "error requires str type parameter containing error message")
        if PRODUCTION_MODE is False:
            logging.error("VECTRIX ERROR (INTERNAL): " + error)
        else:
            self.__log_sender(log_type="ERROR",
                              visibility="INTERNAL", message=error)

    def external_error(self, error: str):
        """
        Vectrix external errors are are customer facing errors that our developers use to alert a customer of an error that the customer could action, for instance, lack of permissions. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for error message
        :returns: (No return)
        """
        if not isinstance(error, str):
            raise ValueError(
                "external_error requires str type parameter containing error message")
        if PRODUCTION_MODE is False:
            logging.error("VECTRIX ERROR (EXTERNAL): " + error)
        else:
            self.__log_sender(log_type="ERROR",
                              visibility="EXTERNAL", message=error)
