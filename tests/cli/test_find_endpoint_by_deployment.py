from __future__ import annotations

from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import _deployment_matches

EP1_CANDIDATE = "my-project/my-endpoint/candidate"
EP2_CANDIDATE = "my-project/other-endpoint/candidate"


class TestDeploymentMatches:
    def test_id_match(self) -> None:
        assert _deployment_matches("dep_a", "dep_a", EP1_CANDIDATE)

    def test_dep_prefix_never_name_matches(self) -> None:
        assert not _deployment_matches("dep_a", "dep_b", "dep_a")

    def test_exact_qualified_name(self) -> None:
        assert _deployment_matches(EP1_CANDIDATE, "dep_a", EP1_CANDIDATE)
        assert not _deployment_matches(EP1_CANDIDATE, "dep_b", EP2_CANDIDATE)

    def test_two_segment_suffix_does_not_collapse_to_last_segment(self) -> None:
        assert _deployment_matches("other-endpoint/candidate", "dep_b", EP2_CANDIDATE)
        assert not _deployment_matches("other-endpoint/candidate", "dep_a", EP1_CANDIDATE)

    def test_bare_name_still_matches_last_segment(self) -> None:
        assert _deployment_matches("candidate", "dep_a", EP1_CANDIDATE)
        assert _deployment_matches("candidate", "dep_b", EP2_CANDIDATE)

    def test_mistyped_qualified_name_does_not_last_segment_match(self) -> None:
        assert not _deployment_matches("my-project/wrong-endpoint/candidate", "dep_a", EP1_CANDIDATE)
        assert not _deployment_matches("my-project/wrong-endpoint/candidate", "dep_b", EP2_CANDIDATE)

    def test_none_name(self) -> None:
        assert not _deployment_matches("candidate", "dep_a", None)
