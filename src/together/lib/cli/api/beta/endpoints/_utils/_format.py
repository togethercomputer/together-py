from __future__ import annotations


def format_endpoint_type(endpoint_type: str | None) -> str:
    if endpoint_type is None:
        return "Unknown"

    return {
        "ENDPOINT_TYPE_DEDICATED": "Dedicated",
        "ENDPOINT_TYPE_SERVERLESS": "Serverless",
        "ENDPOINT_TYPE_RESERVED": "Reserved",
    }.get(endpoint_type, endpoint_type.replace("ENDPOINT_TYPE_", "").replace("_", " ").title())
