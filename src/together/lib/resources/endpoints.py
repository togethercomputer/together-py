from typing import List

import httpx

from together import Together


def list_avzones(client: Together) -> List[str]:
    """
    List all available availability zones.

    Returns:
        List[str]: List of unique availability zones
    """

    response = client.get("clusters/availability-zones", cast_to=httpx.Response)

    return response.json()["avzones"]
