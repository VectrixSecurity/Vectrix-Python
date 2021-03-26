import json

from .checks import output_type_check
from .settings import PRODUCTION_MODE


def test_output(*ignore, assets=None, issues=None, events=None):
    """
    __test_output takes in the same parameters as output and acts very similiarly, however it will print out top level information instead of all assets, issues, and events identified.
    """
    final = {"assets": {}, "issues": {}, "events": {}}
    for asset in assets:
        if asset['type'] in final['assets']:
            final['assets'][asset['type']] += 1
        else:
            final['assets'][asset['type']] = 1
    for issue in issues:
        if issue['issue'] in final['issues']:
            final['issues'][issue['issue']] += 1
        else:
            final['issues'][issue['issue']] = 1
    for event in events:
        if event['event'] in final['events']:
            final['events'][event['event']] += 1
        else:
            final['events'][event['event']] = 1
    output_type_check(assets, issues, events)
    if PRODUCTION_MODE is False:
        print("(DEV MODE) Vectrix Module Output:")
        print("**** ASSETS ****")
        print(json.dumps(final['assets']))
        print("**** ISSUES ****")
        print(json.dumps(final['issues']))
        print("**** EVENTS ****")
        print(json.dumps(final['events']))
    else:
        raise NotImplementedError(
            "__test_ouput may only be utilized in development mode.")
