"""Vectrix Module Utilities"""
import requests  # TODO ADD requests library as a requirement
import boto3  # TODO ADD boto3 library as a requirement
import os
import json
import logging
import traceback


class VectrixUtils:
    def __init__(self):
        self.production_mode = os.environ.get('PRODUCTION_MODE') == "TRUE"
        self.vectrix_platform = os.environ.get('PLATFORM_URL')
        if not self.production_mode:
            print("**** Vectrix Module is in local development mode ****")
            self.__init_development_mode()
            logging.basicConfig(
                filename=(os.getcwd() + '/.vectrix/vectrix-module.log'), level=logging.DEBUG)
        else:
            self.deployment_id = os.environ.get('DEPLOYMENT_ID')
            self.deployment_key = os.environ.get('DEPLOYMENT_KEY')
            self.auth_headers = {
                "DEPLOYMENT_ID": self.deployment_id, "DEPLOYMENT_KEY": self.deployment_key}
        self.state = self.__init_state()

    def __init_state(self):
        """
        Initializes state depending on if the module is in production or not.
        If the module is in local development, it'll create a directory + module_state file that holds json of state (for continous state holding)
        """
        if (self.production_mode):
            state = self.__get_vectrix_platform(endpoint="/v1/state/get")
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

    def __get_vectrix_platform(self, endpoint=None):
        """
        Make HTTP GET request to Vectrix platform
        """
        try:
            response = requests.get(
                self.vectrix_platform + endpoint, headers=self.auth_headers, timeout=10)
            return response.json()
        except Exception as e:
            logging.error("Failed GET'ing data at {endpoint} on Vectrix Platform...".format(
                endpoint=endpoint))
            logging.error(str(traceback.format_exc()))
            return None

    def __post_vectrix_platform(self, endpoint=None, data=None):
        """
        Make HTTP POST request to Vectrix platform
        """
        try:
            response = requests.post(
                self.vectrix_platform + endpoint, json=data, headers=self.auth_headers, timeout=10)
            return response.json()
        except Exception as e:
            logging.error("Failed POST'ing data at {endpoint} on Vectrix Platform...".format(
                endpoint=endpoint))
            logging.error(str(traceback.format_exc()))
            return None

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
            raise TypeError("set_state requires dict type parameter")

        merged_state = self.state.copy()
        merged_state.update(new_state)
        self.state = merged_state

        if self.production_mode is False:
            self.__dev_hold_local_state(merged_state)
        return merged_state

    def unset_state(self, key):
        """
        unset_state will remove a key from the current state

        :params: (String) key to be removed from state
        :returns: (No return)
        """
        self.state.pop(key, None)
        if self.production_mode is False:
            self.__dev_hold_local_state(self.state)

    def output(self, *ignore, assets=None, issues=None, events=None):
        """
        output will send the identified assets, issues, and events to the Vectrix platform. This should always be called after a scan.

        :params: assets (list) - Keyword argument of the assets identified during a scan.
        :params: issues (list) - Keyword argument of the issues identified during a scan.
        :params: events (list) - Keyword argument of the events identified during a scan.
        :returns: (No return)
        """
        if not isinstance(assets, list) or not isinstance(issues, list) or not isinstance(events, list):
            raise TypeError(
                "output requires 3 keyword argument list type parameters: assets, issues, events")
        if self.production_mode is False:
            print("(DEV MODE) Vectrix Module Output:")
            print("**** ASSETS ****")
            print(assets)
            print("**** ISSUES ****")
            print(issues)
            print("**** EVENTS ****")
            print(events)
            self.__dev_hold_last_scan_results(
                {"assets": assets, "issues": issues, "events": events})
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/scan/create", data={"assets": assets, "issues": issues, "events": events})
            self.__post_vectrix_platform(
                endpoint="/v1/state/set", data=self.state)

    def get_credentials(self):
        """
        This will return applicable customer credentials to be used for restricted APIs. For more information, visit https://developer.vectrix.io/module-development/module-access

        :params: (None)
        :returns: dict of credentials (keys within dict depend on the cloud vendor, For more information, visit https://developer.vectrix.io/module-development/module-access)
        """
        if self.production_mode is False:
            raise NotImplementedError(
                "get_credentials isn't allowed within local development, please handle yourself then implement once moving vectrix module to production")
        else:
            return self.__get_vectrix_platform(endpoint="/v1/credentials/get")

    def create_aws_session(self, aws_role_arn=None, aws_external_id=None):
        """
        This will return an authenticated boto3 session to access a customer AWS environment. For more information, visit https://developer.vectrix.io/module-development/module-access/aws-access

        :param: aws_role_arn (String) - Customer AWS Role ARN (can be retrieved from get_credentials)
        :param: aws_external_id (String) - Customer AWS External ID (can be retrieved from get_credentials)
        :returns: authenticated boto3 session object
        """
        if self.production_mode is False:
            raise NotImplementedError(
                "create_aws_session isn't allowed within local development, please handle yourself then implement once moving vectrix module to production")

        response = self.__post_vectrix_platform(endpoint="/v1/credentials/aws", data={
                                                "aws_role_arn": aws_role_arn, "aws_external_id": aws_external_id})
        aws_session = boto3.Session(
            aws_access_key_id=response["credentials"]["AccessKeyId"],
            aws_secret_access_key=response["credentials"]["SecretAccessKey"],
            aws_session_token=response["credentials"]["SessionToken"])
        return aws_session

    def get_last_scan_results(self):
        """
        This will return the last scan results of a module within a dictionary of keys 'assets' 'issues' and 'events' - For more information, visit https://developer.vectrix.io/module-development/module-state#last-scan-results
        """
        if self.production_mode is False:
            scan_file = os.getcwd() + "/.vectrix/last_scan_results.json"
            if not os.path.exists(scan_file):
                return {"assets": [], "issues": [], "events": []}
            else:
                with open(scan_file) as f:
                    data = json.load(f)
                return data
        else:
            return self.__get_vectrix_platform("/v1/scan/get")

    def get_inputs(self):
        """
        Some Vectrix modules will require custom inputs from customers, this method is how to retrieve customer inputted values. For more information, visit https://developer.vectrix.io/module-development/module-inputs
        :returns: (dict) of customer inputs
        """
        if self.production_mode is False:
            raise NotImplementedError(
                "get_inputs isn't allowed within local development, please handle yourself then implement once moving vectrix module to production")

        else:
            return self.__get_vectrix_platform(endpoint="/v1/inputs/get")
        return None

    def log(self, message: str):
        """
        Vectrix logs are internal logs for developers to create that are sent to the developer via our platform. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for log message
        :returns: (No return)
        """
        if self.production_mode is False:
            logging.debug("VECTRIX LOG (INTERNAL): " + message)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/log/internal", data={"message": message})

    def external_log(self, message: str):
        """
        Vectrix external logs are customer facing logs that our developers use to show what a module is doing within a scan. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for log message
        :returns: (No return)
        """
        if self.production_mode is False:
            logging.debug("VECTRIX LOG (EXTERNAL): " + message)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/log/external", data={"message": message})

    def error(self, error: str):
        """
        Vectrix errors are internal errors for developers to create that are sent to the developer via our platform. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for error message
        :returns: (No return)
        """
        if self.production_mode is False:
            logging.error("VECTRIX ERROR (INTERNAL): " + error)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/error/internal", data={"message": error})

    def external_error(self, error: str):
        """
        Vectrix external errors are are customer facing errors that our developers use to alert a customer of an error that the customer could action, for instance, lack of permissions. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for error message
        :returns: (No return)
        """
        if self.production_mode is False:
            logging.error("VECTRIX ERROR (EXTERNAL): " + error)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/error/external", data={"message": error})
