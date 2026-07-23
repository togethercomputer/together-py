# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .configs import (
    ConfigsResource,
    AsyncConfigsResource,
    ConfigsResourceWithRawResponse,
    AsyncConfigsResourceWithRawResponse,
    ConfigsResourceWithStreamingResponse,
    AsyncConfigsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncCursorPagination, AsyncCursorPagination
from ....types.beta import (
    model_list_params,
    model_create_params,
    model_update_params,
    model_list_files_params,
    model_list_supported_params,
    model_list_org_scoped_params,
)
from .remote_uploads import (
    RemoteUploadsResource,
    AsyncRemoteUploadsResource,
    RemoteUploadsResourceWithRawResponse,
    AsyncRemoteUploadsResourceWithRawResponse,
    RemoteUploadsResourceWithStreamingResponse,
    AsyncRemoteUploadsResourceWithStreamingResponse,
)
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.model import Model
from ....types.beta.supported_model import SupportedModel
from ....types.beta.model_delete_response import ModelDeleteResponse
from ....types.beta.model_list_files_response import ModelListFilesResponse
from ....types.beta.model_list_revisions_response import ModelListRevisionsResponse

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def remote_uploads(self) -> RemoteUploadsResource:
        return RemoteUploadsResource(self._client)

    @cached_property
    def configs(self) -> ConfigsResource:
        return ConfigsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        project_id: str | None = None,
        base_model_id: str,
        name: str,
        type: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Registers a custom model resource in the project.

        Registration creates the
        model's metadata; upload or import model files separately before deploying it.

        Args:
          project_id: Project identifier.

          base_model_id: ID of the supported base model from which this model was derived.

          name: Name for the custom model. May be bare or qualified as
              `<project_slug>/<model_name>`; a supplied project slug must match the project in
              the request path.

          type: Volume type to create. Use `model` or `adapter`; plural `models` and `adapters`
              are also accepted.

          description: Human-readable description of the model and its intended use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models", project_id=project_id),
            body=maybe_transform(
                {
                    "base_model_id": base_model_id,
                    "name": name,
                    "type": type,
                    "description": description,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Retrieves a custom model's metadata, visibility, weight information, and
        base-model relationship.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        update_mask: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Updates mutable model metadata such as its inference name, description, base
        model, or visibility.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          update_mask: Fields to update. If omitted, all mutable fields are overwritten.

          description: Updated user-facing model description.

          name: Updated inference-addressable model name.

          visibility: Who can discover the model. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "visibility": visibility,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, model_update_params.ModelUpdateParams),
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        organization_id: str | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[Model]:
        """Lists custom model resources owned by the specified project.

        Use the
        organization endpoint to list models shared across projects or the
        supported-model catalog to discover Together-hosted base models.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous model list response.

          limit: Maximum number of models to return.

          organization_id: Organization whose shared models should be included. Defaults to the
              authenticated project's organization.

          visibility: Model visibility. Private means it is scoped to the project. Internal means it
              is scoped to the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models", project_id=project_id),
            page=SyncCursorPagination[Model],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "organization_id": organization_id,
                        "visibility": visibility,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            model=Model,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeleteResponse:
        """Permanently deletes a custom model resource.

        The model must not be in use by an
        active deployment.

        Args:
          project_id: ID of the project that owns the model.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeleteResponse,
        )

    def list_files(
        self,
        id: str,
        *,
        project_id: str | None = None,
        revision_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListFilesResponse:
        """
        Lists files in the latest or specified revision of a model, including paths,
        sizes, and content hashes.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          revision_id: Revision identifier to read from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}/files", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"revision_id": revision_id}, model_list_files_params.ModelListFilesParams),
            ),
            cast_to=ModelListFilesResponse,
        )

    def list_org_scoped(
        self,
        organization_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[Model]:
        """
        Lists custom models shared with every project in the specified organization.
        Project-private and public models are not included.

        Args:
          organization_id: Organization identifier.

          after: Cursor from a previous list response.

          limit: Maximum number of results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/organizations/{organization_id}/models", organization_id=organization_id),
            page=SyncCursorPagination[Model],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    model_list_org_scoped_params.ModelListOrgScopedParams,
                ),
            ),
            model=Model,
        )

    def list_revisions(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListRevisionsResponse:
        """
        Lists the immutable file revisions available for a custom model, newest first.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}/revisions", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelListRevisionsResponse,
        )

    def list_supported(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        modality: Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"] | Omit = omit,
        product: Literal["PRODUCT_SERVERLESS", "PRODUCT_DEDICATED", "PRODUCT_FINE_TUNING"] | Omit = omit,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[SupportedModel]:
        """
        Lists Together-hosted base models that can be deployed for dedicated inference,
        together with their capabilities and certified deployment profiles.

        Args:
          after: Cursor from a previous supported-model list response.

          limit: Maximum number of models to return.

          modality: Filter models by input modality.

          product: Filter models by product surface.

          search: Case-insensitive search across model IDs, names, and descriptions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/supported-models" if self._client._base_url_overridden else "https://api.together.ai/v2/supported-models",
            page=SyncCursorPagination[SupportedModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "modality": modality,
                        "product": product,
                        "search": search,
                    },
                    model_list_supported_params.ModelListSupportedParams,
                ),
            ),
            model=SupportedModel,
        )

    def retrieve_supported(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupportedModel:
        """
        Retrieves a Together-hosted base model and the certified model, configuration,
        hardware, and performance profiles available for deployment.

        Args:
          id: Supported model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/supported-models/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupportedModel,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def remote_uploads(self) -> AsyncRemoteUploadsResource:
        return AsyncRemoteUploadsResource(self._client)

    @cached_property
    def configs(self) -> AsyncConfigsResource:
        return AsyncConfigsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        project_id: str | None = None,
        base_model_id: str,
        name: str,
        type: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """Registers a custom model resource in the project.

        Registration creates the
        model's metadata; upload or import model files separately before deploying it.

        Args:
          project_id: Project identifier.

          base_model_id: ID of the supported base model from which this model was derived.

          name: Name for the custom model. May be bare or qualified as
              `<project_slug>/<model_name>`; a supplied project slug must match the project in
              the request path.

          type: Volume type to create. Use `model` or `adapter`; plural `models` and `adapters`
              are also accepted.

          description: Human-readable description of the model and its intended use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "base_model_id": base_model_id,
                    "name": name,
                    "type": type,
                    "description": description,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Retrieves a custom model's metadata, visibility, weight information, and
        base-model relationship.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        update_mask: str | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Updates mutable model metadata such as its inference name, description, base
        model, or visibility.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          update_mask: Fields to update. If omitted, all mutable fields are overwritten.

          description: Updated user-facing model description.

          name: Updated inference-addressable model name.

          visibility: Who can discover the model. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                    "visibility": visibility,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"update_mask": update_mask}, model_update_params.ModelUpdateParams),
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        organization_id: str | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Model, AsyncCursorPagination[Model]]:
        """Lists custom model resources owned by the specified project.

        Use the
        organization endpoint to list models shared across projects or the
        supported-model catalog to discover Together-hosted base models.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous model list response.

          limit: Maximum number of models to return.

          organization_id: Organization whose shared models should be included. Defaults to the
              authenticated project's organization.

          visibility: Model visibility. Private means it is scoped to the project. Internal means it
              is scoped to the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models", project_id=project_id),
            page=AsyncCursorPagination[Model],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "organization_id": organization_id,
                        "visibility": visibility,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            model=Model,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeleteResponse:
        """Permanently deletes a custom model resource.

        The model must not be in use by an
        active deployment.

        Args:
          project_id: ID of the project that owns the model.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeleteResponse,
        )

    async def list_files(
        self,
        id: str,
        *,
        project_id: str | None = None,
        revision_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListFilesResponse:
        """
        Lists files in the latest or specified revision of a model, including paths,
        sizes, and content hashes.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          revision_id: Revision identifier to read from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}/files", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"revision_id": revision_id}, model_list_files_params.ModelListFilesParams
                ),
            ),
            cast_to=ModelListFilesResponse,
        )

    def list_org_scoped(
        self,
        organization_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Model, AsyncCursorPagination[Model]]:
        """
        Lists custom models shared with every project in the specified organization.
        Project-private and public models are not included.

        Args:
          organization_id: Organization identifier.

          after: Cursor from a previous list response.

          limit: Maximum number of results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/organizations/{organization_id}/models", organization_id=organization_id),
            page=AsyncCursorPagination[Model],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    model_list_org_scoped_params.ModelListOrgScopedParams,
                ),
            ),
            model=Model,
        )

    async def list_revisions(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListRevisionsResponse:
        """
        Lists the immutable file revisions available for a custom model, newest first.

        Args:
          project_id: Project identifier.

          id: Model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/models/{id}/revisions", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelListRevisionsResponse,
        )

    def list_supported(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        modality: Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"] | Omit = omit,
        product: Literal["PRODUCT_SERVERLESS", "PRODUCT_DEDICATED", "PRODUCT_FINE_TUNING"] | Omit = omit,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[SupportedModel, AsyncCursorPagination[SupportedModel]]:
        """
        Lists Together-hosted base models that can be deployed for dedicated inference,
        together with their capabilities and certified deployment profiles.

        Args:
          after: Cursor from a previous supported-model list response.

          limit: Maximum number of models to return.

          modality: Filter models by input modality.

          product: Filter models by product surface.

          search: Case-insensitive search across model IDs, names, and descriptions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/supported-models" if self._client._base_url_overridden else "https://api.together.ai/v2/supported-models",
            page=AsyncCursorPagination[SupportedModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "modality": modality,
                        "product": product,
                        "search": search,
                    },
                    model_list_supported_params.ModelListSupportedParams,
                ),
            ),
            model=SupportedModel,
        )

    async def retrieve_supported(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupportedModel:
        """
        Retrieves a Together-hosted base model and the certified model, configuration,
        hardware, and performance profiles available for deployment.

        Args:
          id: Supported model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/supported-models/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupportedModel,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = to_raw_response_wrapper(
            models.update,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.delete = to_raw_response_wrapper(
            models.delete,
        )
        self.list_files = to_raw_response_wrapper(
            models.list_files,
        )
        self.list_org_scoped = to_raw_response_wrapper(
            models.list_org_scoped,
        )
        self.list_revisions = to_raw_response_wrapper(
            models.list_revisions,
        )
        self.list_supported = to_raw_response_wrapper(
            models.list_supported,
        )
        self.retrieve_supported = to_raw_response_wrapper(
            models.retrieve_supported,
        )

    @cached_property
    def remote_uploads(self) -> RemoteUploadsResourceWithRawResponse:
        return RemoteUploadsResourceWithRawResponse(self._models.remote_uploads)

    @cached_property
    def configs(self) -> ConfigsResourceWithRawResponse:
        return ConfigsResourceWithRawResponse(self._models.configs)


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            models.update,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.delete = async_to_raw_response_wrapper(
            models.delete,
        )
        self.list_files = async_to_raw_response_wrapper(
            models.list_files,
        )
        self.list_org_scoped = async_to_raw_response_wrapper(
            models.list_org_scoped,
        )
        self.list_revisions = async_to_raw_response_wrapper(
            models.list_revisions,
        )
        self.list_supported = async_to_raw_response_wrapper(
            models.list_supported,
        )
        self.retrieve_supported = async_to_raw_response_wrapper(
            models.retrieve_supported,
        )

    @cached_property
    def remote_uploads(self) -> AsyncRemoteUploadsResourceWithRawResponse:
        return AsyncRemoteUploadsResourceWithRawResponse(self._models.remote_uploads)

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithRawResponse:
        return AsyncConfigsResourceWithRawResponse(self._models.configs)


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            models.update,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.delete = to_streamed_response_wrapper(
            models.delete,
        )
        self.list_files = to_streamed_response_wrapper(
            models.list_files,
        )
        self.list_org_scoped = to_streamed_response_wrapper(
            models.list_org_scoped,
        )
        self.list_revisions = to_streamed_response_wrapper(
            models.list_revisions,
        )
        self.list_supported = to_streamed_response_wrapper(
            models.list_supported,
        )
        self.retrieve_supported = to_streamed_response_wrapper(
            models.retrieve_supported,
        )

    @cached_property
    def remote_uploads(self) -> RemoteUploadsResourceWithStreamingResponse:
        return RemoteUploadsResourceWithStreamingResponse(self._models.remote_uploads)

    @cached_property
    def configs(self) -> ConfigsResourceWithStreamingResponse:
        return ConfigsResourceWithStreamingResponse(self._models.configs)


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            models.update,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            models.delete,
        )
        self.list_files = async_to_streamed_response_wrapper(
            models.list_files,
        )
        self.list_org_scoped = async_to_streamed_response_wrapper(
            models.list_org_scoped,
        )
        self.list_revisions = async_to_streamed_response_wrapper(
            models.list_revisions,
        )
        self.list_supported = async_to_streamed_response_wrapper(
            models.list_supported,
        )
        self.retrieve_supported = async_to_streamed_response_wrapper(
            models.retrieve_supported,
        )

    @cached_property
    def remote_uploads(self) -> AsyncRemoteUploadsResourceWithStreamingResponse:
        return AsyncRemoteUploadsResourceWithStreamingResponse(self._models.remote_uploads)

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithStreamingResponse:
        return AsyncConfigsResourceWithStreamingResponse(self._models.configs)
