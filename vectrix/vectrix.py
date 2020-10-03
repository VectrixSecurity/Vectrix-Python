"""
Vectrix Module Utilities
"""
import requests
import boto3
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
                filename=(os.getcwd() + '/.vectrix/vectrix-module.log'), level=logging.WARNING)  # TODO Test logging level change with .error and .warning
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
                self.vectrix_platform + endpoint, headers=self.auth_headers, timeout=360)
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
                self.vectrix_platform + endpoint, json=data, headers=self.auth_headers, timeout=3600)
            return response.json()
        except Exception as e:
            logging.error("Failed POST'ing data at {endpoint} on Vectrix Platform...".format(
                endpoint=endpoint))
            logging.error(str(traceback.format_exc()))
            return None

    def __output_type_check(self, assets, issues, events):
        """
        Verify a vectrix.output() call to ensure all submitted data correctly falls within the guidelines and if not,
        will return an exception.
        """
        if not isinstance(assets, list) or not isinstance(issues, list) or not isinstance(events, list):
            raise ValueError(
                "output requires 3 keyword argument list type parameters: assets, issues, events")

        test_elems = {
            "asset": [
                {"key": "type", "val": "str"},
                {"key": "id", "val": "str"},
                {"key": "display_name", "val": "str"},
                {"key": "link", "val": "str", "optional": True},
                {"key": "metadata", "val": {}}
            ],
            "issue": [
                {"key": "issue", "val": "str"},
                {"key": "asset_id", "val": []},
                {"key": "metadata", "val": {}}
            ],
            "event": [
                {"key": "event", "val": "str"},
                {"key": "event_time", "val": 1},
                {"key": "display_name", "val": "str"},
                {"key": "metadata", "val": {}}
            ]
        }

        test_keys = {
            "asset": ["type", "id", "display_name", "link", "metadata"],
            "issue": ["issue", "asset_id", "metadata"],
            "event": ["event", "event_time", "display_name", "metadata"]
        }

        test_items = {
            "asset": assets,
            "issue": issues,
            "event": events
        }

        # Verify all inputted types are correct
        for key in test_items:
            for item in test_items[key]:
                for item_key in item:
                    if item_key not in test_keys[key]:
                        raise ValueError("{key} dict does not allow key '{bad_key}'. Only allowed keys: {allowed_keys}. Information: https://developer.vectrix.io/module-development/module-output".format(
                            key=key, bad_key=item_key, allowed_keys=str(test_keys[key])))
                for elem in test_elems[key]:
                    if elem['key'] in item:
                        if not isinstance(item[elem['key']], type(elem['val'])):
                            raise ValueError(
                                "{msg} dict key '{key}' value needs to be {val}".format(msg=key, key=elem['key'], val=type(elem['val']).__name__))
                        if elem['key'] == 'link':
                            self.__link_check(item[elem['key']])
                        if elem['key'] == "metadata":
                            metadata = item['metadata']
                            metadata_keys_to_check = [
                                {"key": "priority", "val": 1},
                                {"key": "value", "val": "str"},
                                {"key": "link", "val": "str"}
                            ]
                            metadata_keys = ["priority", "value", "link"]
                            for metadata_key in metadata:
                                if not isinstance(metadata[metadata_key], type({})):
                                    raise ValueError("metadata element '{key}' value needs to be {val}. Information: https://developer.vectrix.io/module-development/module-output".format(
                                        key=metadata_key, val=type({}).__name__))
                                for check_key in metadata_keys_to_check:
                                    if check_key['key'] not in metadata[metadata_key] and check_key['key'] != "link":
                                        raise ValueError(
                                            "all metadata elements are required to have '{key}' key. Information: https://developer.vectrix.io/module-development/module-output".format(key=check_key['key']))
                                    if check_key['key'] != "link" and not isinstance(metadata[metadata_key][check_key['key']], type(check_key['val'])):
                                        raise ValueError(
                                            "metadata element {elem} key '{key}' value needs to be {val}".format(elem=metadata_key, key=check_key['key'], val=type(check_key['val']).__name__))

                                for inputted_key in metadata[metadata_key]:
                                    if inputted_key not in metadata_keys:
                                        raise ValueError(
                                            "metadata element isn't allowed to have '{key}' key. Only keys permitted: {allowed_keys}. Information: https://developer.vectrix.io/module-development/module-output".format(key=inputted_key, allowed_keys=str(metadata_keys)))
                            self.__metadata_deep_check(metadata)
                    elif 'optional' not in elem or elem['optional'] is not True:
                        raise ValueError(
                            "{msg} dict requires '{key}' key. Information: https://developer.vectrix.io/module-development/module-output".format(msg=key, key=elem['key']))
                    else:
                        pass  # The key is optional, pass.

        inputted_asset_ids = {}
        for asset in assets:
            self.__asset_type_check(asset)
            if asset['id'] in inputted_asset_ids:
                raise ValueError(
                    "Duplicate asset id entry '{asset_id}'. All asset id's are required to be unique. Information: https://developer.vectrix.io/module-development/module-output".format(asset_id=asset['id']))
            else:
                inputted_asset_ids[asset['id']] = asset
        for issue in issues:
            for asset in issue['asset_id']:
                if asset not in inputted_asset_ids:
                    raise ValueError(
                        "Vectrix issue ({issue}) references non-existent asset: {asset}".format(issue=issue['issue'], asset=asset))

    def __metadata_deep_check(self, metadata):
        """
        This will check each metadata element to confirm it correctly abides by:
        1 - Metadata Naming Convention guidelines
        2 - Metadata 'priority' key guidelines
        3 - Metadata 'link' key guidelines
        """
        keys = metadata.keys()
        for key in keys:
            """
            Naming Convention:
            - No Spaces
            - No Uppercase
            - No Hyphens
            - Only lowercase
            - Underscores for new words
            """
            if " " in key:
                raise ValueError(
                    "metadata keys aren't allowed to have spaces. Violated on key '{key}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key))
            if "-" in key:
                raise ValueError(
                    "metadata keys aren't allowed to have hyphens. Violated on key '{key}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key))
            for char in key:
                if char.isupper():
                    raise ValueError(
                        "metadata keys can't have uppercase characters. Violated on key '{key}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key))
            p_val = metadata[key]['priority']
            if p_val > 100 or p_val < -1:
                raise ValueError(
                    "metadata 'priority' key is only allowed to be between -1 and 100 (inclusive). Violated on key '{key}' with priority value '{val}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key, val=p_val))
            if 'link' in metadata[key]:
                if "http://" == metadata[key]['link'][:7]:
                    raise ValueError(
                        "Only secure links are allowed in metadata elements (HTTPS). Violated on key '{key}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key))
                if "https://" != metadata[key]['link'][:8]:
                    raise ValueError(
                        "Only https links are allowed to be included in metadata elements. Violated on key '{key}'. Information:  https://developer.vectrix.io/module-development/module-output".format(key=key))

    def __asset_type_check(self, asset):
        """
        Verify asset 'type' key abides by naming convention standards.

        Naming Convention Rules:
        - Asset Types are broken into three categories: <vendor>_<service>_<resource>
            - Example: aws_s3_bucket, gcp_iam_user, github_repository (service ommitted as there isn't any)
            - Always use common abbreviations for a service if there are an any.
            - For multiple words, only use camelCase. This is only allowed for services and resources.
            - For vendors, always use lowercase. Even if the vendor might capitalize their own name in parts. use 'github' instead of GitHub.
        Assets Types aren't allowed to have:
            - Spaces.
            - Hyphens.
            - Uppercase first words.
            - No less than vendor + resource.
            - No more than vendor + service + resource.
        """
        asset_type = asset['type']
        if " " in asset_type:
            raise ValueError(
                "asset types aren't allowed to have spaces. Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
        if "-" in asset_type:
            raise ValueError(
                "asset types aren't allowed to have hyphens. Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
        if "_" not in asset_type:
            raise ValueError(
                "asset types require at least a vendor and a resource specification following snake case (ex. github_repo). Violated on asset type '{type}'. Standard asset type structure is (vendor_service_resource). Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
        split_asset_type = asset_type.split("_")
        if len(split_asset_type) > 3:
            raise ValueError(
                "asset types are only allowed to follow the structure: (vendor_service_resource) (ex. aws_s3_bucket) (service only applies where available). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
        for index, word in enumerate(split_asset_type):
            if len(word) < 2:
                raise ValueError(
                    "asset types need to have at least two characters per vendor, service, resource instantiantion (ex. aws_s3_bucket). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
            if index == 0:
                for char in word:
                    if char.isupper():
                        raise ValueError(
                            "asset type vendor instantiation is required to be all lowercase. (ex. aws_iam_role). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))
            if word[0].isupper():
                raise ValueError(
                    "asset type service and resource instantiations are required to follow camelCase for multiple words. (ex. aws_iam_accessKey). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/module-development/module-output".format(type=asset_type))

    def __link_check(self, link):
        if "http://" == link[:7]:
            raise ValueError(
                "Only secure links are allowed (HTTPS). Violated on link '{link}'. Information:  https://developer.vectrix.io/module-development/module-output".format(link=link))
        if "https://" != link[:8]:
            raise ValueError(
                "Only https links are allowed to be included. Violated on link '{link}'. Information:  https://developer.vectrix.io/module-development/module-output".format(link=link))

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

        if self.production_mode is False:
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
        self.__output_type_check(assets, issues, events)
        if self.production_mode is False:
            print("(DEV MODE) Vectrix Module Output:")
            print("**** ASSETS ****")
            print(json.dumps(assets))
            print("**** ISSUES ****")
            print(json.dumps(issues))
            print("**** EVENTS ****")
            print(json.dumps(events))
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
        if not isinstance(message, str):
            raise ValueError(
                "log requires str type parameter containing log message")
        if self.production_mode is False:
            logging.warning("VECTRIX LOG (INTERNAL): " + message)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/log/internal", data={"message": message})

    def external_log(self, message: str):
        """
        Vectrix external logs are customer facing logs that our developers use to show what a module is doing within a scan. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for log message
        :returns: (No return)
        """
        if not isinstance(message, str):
            raise ValueError(
                "external_log requires str type parameter containing log message")
        if self.production_mode is False:
            logging.warning("VECTRIX LOG (EXTERNAL): " + message)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/log/external", data={"message": message})

    def error(self, error: str):
        """
        Vectrix errors are internal errors for developers to create that are sent to the developer via our platform. For more information, visit: https://developer.vectrix.io/module-development/logging-and-exception-handling

        :param: String for error message
        :returns: (No return)
        """
        if not isinstance(error, str):
            raise ValueError(
                "error requires str type parameter containing error message")
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
        if not isinstance(error, str):
            raise ValueError(
                "external_error requires str type parameter containing error message")
        if self.production_mode is False:
            logging.error("VECTRIX ERROR (EXTERNAL): " + error)
        else:
            self.__post_vectrix_platform(
                endpoint="/v1/error/external", data={"message": error})
