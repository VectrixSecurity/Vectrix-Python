"""
All type checking for functions for Vectrix SDK
"""


def link_check(link):
    if "http://" == link[:7]:
        raise ValueError(
            "Only secure links are allowed (HTTPS). Violated on link '{link}'. Information:  https://developer.vectrix.io/dev/components/output".format(link=link))
    if "https://" != link[:8]:
        raise ValueError(
            "Only https links are allowed to be included. Violated on link '{link}'. Information:  https://developer.vectrix.io/dev/components/output".format(link=link))


def asset_type_check(asset):
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
            "asset types aren't allowed to have spaces. Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
    if "-" in asset_type:
        raise ValueError(
            "asset types aren't allowed to have hyphens. Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
    if "_" not in asset_type:
        raise ValueError(
            "asset types require at least a vendor and a resource specification following snake case (ex. github_repo). Violated on asset type '{type}'. Standard asset type structure is (vendor_service_resource). Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
    split_asset_type = asset_type.split("_")
    if len(split_asset_type) > 3:
        raise ValueError(
            "asset types are only allowed to follow the structure: (vendor_service_resource) (ex. aws_s3_bucket) (service only applies where available). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
    for index, word in enumerate(split_asset_type):
        if len(word) < 2:
            raise ValueError(
                "asset types need to have at least two characters per vendor, service, resource instantiantion (ex. aws_s3_bucket). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
        if index == 0:
            for char in word:
                if char.isupper():
                    raise ValueError(
                        "asset type vendor instantiation is required to be all lowercase. (ex. aws_iam_role). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))
        if word[0].isupper():
            raise ValueError(
                "asset type service and resource instantiations are required to follow camelCase for multiple words. (ex. aws_iam_accessKey). Violated on asset type '{type}'. Information:  https://developer.vectrix.io/dev/components/output".format(type=asset_type))


def metadata_deep_check(metadata):
    """
    This will check each metadata element to confirm it correctly abides by:
    1 - Metadata Naming Convention guidelines
    2 - Metadata 'priority' key guidelines
    3 - Metadata 'link' key guidelines


    Naming Convention:
    - No Spaces
    - No Uppercase
    - No Hyphens
    - Only lowercase
    - Underscores for new words
    """
    keys = metadata.keys()
    for key in keys:
        if " " in key:
            raise ValueError(
                "metadata keys aren't allowed to have spaces. Violated on key '{key}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key))
        if "-" in key:
            raise ValueError(
                "metadata keys aren't allowed to have hyphens. Violated on key '{key}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key))
        for char in key:
            if char.isupper():
                raise ValueError(
                    "metadata keys can't have uppercase characters. Violated on key '{key}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key))
        p_val = metadata[key]['priority']
        if p_val > 100 or p_val < -1:
            raise ValueError(
                "metadata 'priority' key is only allowed to be between -1 and 100 (inclusive). Violated on key '{key}' with priority value '{val}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key, val=p_val))
        if 'link' in metadata[key]:
            if metadata[key]['link'][:7] == "http://":
                raise ValueError(
                    "Only secure links are allowed in metadata elements (HTTPS). Violated on key '{key}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key))
            if metadata[key]['link'][:8] != "https://":
                raise ValueError(
                    "Only https links are allowed to be included in metadata elements. Violated on key '{key}'. Information:  https://developer.vectrix.io/dev/components/output".format(key=key))


def output_type_check(assets, issues, events):
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
                    raise ValueError("{key} dict does not allow key '{bad_key}'. Only allowed keys: {allowed_keys}. Information: https://developer.vectrix.io/dev/components/output".format(
                        key=key, bad_key=item_key, allowed_keys=str(test_keys[key])))
            for elem in test_elems[key]:
                if elem['key'] in item:
                    if not isinstance(item[elem['key']], type(elem['val'])):
                        raise ValueError(
                            "{msg} dict key '{key}' value needs to be {val}".format(msg=key, key=elem['key'], val=type(elem['val']).__name__))
                    if elem['key'] == 'link':
                        link_check(item[elem['key']])
                    if elem['key'] == 'display_name':
                        check_display_name = item[elem['key']]
                        if len(check_display_name) > 0 and ":" not in check_display_name:
                            raise ValueError(
                                "{msg} dict key 'display_name' requires a colon that separates a key and value. Information: https://developer.vectrix.io/dev/components/output#display-name-convention".format(msg=key))
                    if elem['key'] == "metadata":
                        metadata = item['metadata']
                        metadata_keys_to_check = [
                            {"key": "priority", "val": 1},
                            # These are allowed to be str and lists (account for below)
                            {"key": "value", "val": "str"},
                            {"key": "link", "val": "str"}
                        ]
                        metadata_keys = ["priority", "value", "link"]
                        for metadata_key in metadata:
                            if not isinstance(metadata[metadata_key], type({})):
                                raise ValueError("metadata element '{key}' value needs to be {val}. Information: https://developer.vectrix.io/dev/components/output".format(
                                    key=metadata_key, val=type({}).__name__))
                            for check_key in metadata_keys_to_check:
                                if check_key['key'] not in metadata[metadata_key] and check_key['key'] != "link":
                                    raise ValueError(
                                        "all metadata elements are required to have '{key}' key. Information: https://developer.vectrix.io/dev/components/output".format(key=check_key['key']))
                                if check_key['key'] != "value" and check_key['key'] != "link" and not isinstance(metadata[metadata_key][check_key['key']], type(check_key['val'])):
                                    raise ValueError(
                                        "metadata element {elem} key '{key}' value needs to be {val}".format(elem=metadata_key, key=check_key['key'], val=type(check_key['val']).__name__))
                                if check_key['key'] == "value":
                                    if not isinstance(metadata[metadata_key][check_key['key']], type("")) and not isinstance(metadata[metadata_key][check_key['key']], type([])):
                                        raise ValueError("metadata element {elem} key 'value' needs to be either (1) str or (2) list of str's".format(
                                            elem=metadata_key))
                                    if isinstance(metadata[metadata_key][check_key['key']], type([])):
                                        for metadata_check_key_list_elem in metadata[metadata_key][check_key['key']]:
                                            if not isinstance(metadata_check_key_list_elem, type("")):
                                                raise ValueError("metadata element {elem} key 'value' can be list, but each element in the list has to be 'str'. Violated with list element value of: {violation}".format(
                                                    violation=str(metadata_check_key_list_elem), elem=metadata_key))

                            for inputted_key in metadata[metadata_key]:
                                if inputted_key not in metadata_keys:
                                    raise ValueError(
                                        "metadata element isn't allowed to have '{key}' key. Only keys permitted: {allowed_keys}. Information: https://developer.vectrix.io/dev/components/output".format(key=inputted_key, allowed_keys=str(metadata_keys)))
                        metadata_deep_check(metadata)
                elif 'optional' not in elem or elem['optional'] is not True:
                    raise ValueError(
                        "{msg} dict requires '{key}' key. Information: https://developer.vectrix.io/dev/components/output".format(msg=key, key=elem['key']))
                else:
                    pass  # The key is optional, pass.

    inputted_asset_ids = {}
    for asset in assets:
        asset_type_check(asset)
        if asset['id'] in inputted_asset_ids:
            raise ValueError(
                "Duplicate asset id entry '{asset_id}'. All asset id's are required to be unique. Information: https://developer.vectrix.io/dev/components/output".format(asset_id=asset['id']))
        else:
            inputted_asset_ids[asset['id']] = asset
    for issue in issues:
        for asset in issue['asset_id']:
            if asset not in inputted_asset_ids:
                raise ValueError(
                    "Vectrix issue ({issue}) references non-existent asset: {asset}".format(issue=issue['issue'], asset=asset))
