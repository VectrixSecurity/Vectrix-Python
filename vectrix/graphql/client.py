import logging

import requests

from .routes import GraphQLRoutes
from .utils import snake_case_to_camel_case
from ..settings import API_URL

logger = logging.getLogger()


def graphql_client(route: GraphQLRoutes, variables: dict = {}):
    """
    Small wrapper around Vectrix GraphQL API to nicely transmit and convert data
    """
    try:
        formatted_variables = snake_case_to_camel_case(variables)

        response = requests.post(
            API_URL, json={"query": route.value, "variables": formatted_variables})

        if response.status_code == 400:
            raise Exception(
                f"Error communicating with Vectrix API on Query: {route}")

        return response.json()['data']

    except Exception as e:
        logger.exception(e)
        return None
