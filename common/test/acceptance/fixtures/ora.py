"""
Fixture to configure ORA stub problem locations.
"""

import requests
import json
from . import ORA_STUB_URL


class OraResponseFixtureError(Exception):
    pass


class OraLocationsFixture(object):
    """
    """

    def __init__(self, locations):
        self._locations = locations

    def install(self):
        url = ORA_STUB_URL + "/set_config"
        payload = {'problem_locations': json.dumps(self._locations)}

        response = requests.put(url, data=payload)

        if not response.ok:
            raise OraResponseFixtureError(
                "Could not configure ORA stub with locations {locations}.  Status code: {status}".format(
                    locations=self._locations, status=response.status_code))
