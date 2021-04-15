import json


def convert(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def snake_case_to_camel_case(input):
    """
    Converts str or dict or list of dicts input to camelCase.
    """
    if isinstance(input, str):
        return convert(input)
    elif isinstance(input, dict):
        formatted_dict = {}
        for item in input:
            if isinstance(input[item], dict):
                formatted_dict[convert(item)] = snake_case_to_camel_case(
                    input[item])
            else:
                formatted_dict[convert(item)] = input[item]
        return formatted_dict
    else:
        raise Exception("Invalid input object type provided")


def vectrix_item_converter(item_list: list):
    """
    Converts a list of assets, issues, or events into proper metadata formatting for the API request
    """

    formatted_item_list = []
    for item in item_list:
        new_item_dict = {}
        for elem in item:
            if elem == 'metadata':
                new_item_dict['metadata'] = str(json.dumps(item['metadata']))
            else:
                new_item_dict[snake_case_to_camel_case(elem)] = item[elem]
        formatted_item_list.append(new_item_dict)

    return formatted_item_list
