from __future__ import annotations

import pytest

from together._models import construct_type
from together.types.endpoint_deployment import Placement as ResponsePlacement
from together.lib.cli.api.endpoints._utils._placement import (
    shared_placement,
    combine_placement,
    placement_from_response,
)
from together.types.endpoints.deployment_create_params import PlacementInline


def _parsed(value: dict[str, object]) -> ResponsePlacement:
    return construct_type(value=value, type_=ResponsePlacement)  # type: ignore[return-value]


class TestPlacementFromResponse:
    def test_inline_hipaa_regions_and_constraint(self) -> None:
        parsed = _parsed(
            {
                "inline": {
                    "regions": ["us-east-1", "us-west-2"],
                    "constraint": "ENFORCEMENT_REQUIRED",
                    "compliancePolicy": {"hipaa": True},
                }
            }
        )

        assert placement_from_response(parsed) == {
            "inline": {
                "regions": ["us-east-1", "us-west-2"],
                "constraint": "ENFORCEMENT_REQUIRED",
                "compliance_policy": {"hipaa": True},
            }
        }

    def test_profile(self) -> None:
        parsed = _parsed({"profile": "pp_hipaa"})

        assert placement_from_response(parsed) == {"profile": "pp_hipaa"}

    def test_missing_placement(self) -> None:
        assert placement_from_response(None) is None

    def test_hipaa_false_is_preserved(self) -> None:
        parsed = _parsed({"inline": {"compliancePolicy": {"hipaa": False}}})

        assert placement_from_response(parsed) == {"inline": {"compliance_policy": {"hipaa": False}}}


class TestCombinePlacement:
    def test_omitted_flags_copy_inherited_placement(self) -> None:
        inherited = PlacementInline(inline={"compliance_policy": {"hipaa": True}, "regions": ["us-east-1"]})

        assert combine_placement(None, inherited, hipaa_specified=False) == inherited

    def test_region_override_keeps_inherited_hipaa(self) -> None:
        explicit = PlacementInline(inline={"regions": ["us-west-2"]})
        inherited = PlacementInline(
            inline={
                "regions": ["us-east-1"],
                "constraint": "ENFORCEMENT_REQUIRED",
                "compliance_policy": {"hipaa": True},
            }
        )

        assert combine_placement(explicit, inherited, hipaa_specified=False) == {
            "inline": {"regions": ["us-west-2"], "compliance_policy": {"hipaa": True}}
        }

    def test_explicit_hipaa_replaces_inherited_placement(self) -> None:
        explicit = PlacementInline(inline={"compliance_policy": {"hipaa": True}})
        inherited = PlacementInline(inline={"regions": ["us-east-1"], "compliance_policy": {"hipaa": True}})

        assert combine_placement(explicit, inherited, hipaa_specified=True) == explicit

    def test_profile_replaces_inherited_hipaa(self) -> None:
        inherited = PlacementInline(inline={"compliance_policy": {"hipaa": True}})

        assert combine_placement({"profile": "pp_other"}, inherited, hipaa_specified=False) == {"profile": "pp_other"}


class TestSharedPlacement:
    def test_equal_placements(self) -> None:
        placement = PlacementInline(inline={"compliance_policy": {"hipaa": True}})

        assert shared_placement([("dep_a", placement), ("dep_b", placement)]) == placement

    def test_disagreement_names_deployments(self) -> None:
        with pytest.raises(ValueError, match=r"dep_a vs dep_b"):
            shared_placement(
                [
                    ("dep_a", PlacementInline(inline={"compliance_policy": {"hipaa": True}})),
                    ("dep_b", None),
                ]
            )

    def test_empty(self) -> None:
        assert shared_placement([]) is None
