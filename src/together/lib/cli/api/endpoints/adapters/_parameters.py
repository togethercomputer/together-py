from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

EndpointIDParameter = Annotated[str, Parameter(help="The ID of the endpoint")]
ModelIDParameter = Annotated[
    str,
    Parameter(help='Combined identifier in format "endpoint_name:adapter_model_name"'),
]
