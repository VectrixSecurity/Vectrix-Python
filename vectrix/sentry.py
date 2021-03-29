from sentry_sdk import init


def activate_sentry(sentry_webhook: str):
    if not sentry_webhook:
        raise Exception("No webhook provided to activate sentry.")
    init(sentry_webhook)
