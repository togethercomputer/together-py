# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from .secrets import (
    SecretsResource,
    AsyncSecretsResource,
    SecretsResourceWithRawResponse,
    AsyncSecretsResourceWithRawResponse,
    SecretsResourceWithStreamingResponse,
    AsyncSecretsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.beta import deployment_create_params, deployment_update_params, deployment_get_logs_params
from ...._base_client import make_request_options
from .storage.storage import (
    StorageResource,
    AsyncStorageResource,
    StorageResourceWithRawResponse,
    AsyncStorageResourceWithRawResponse,
    StorageResourceWithStreamingResponse,
    AsyncStorageResourceWithStreamingResponse,
)
from .image_repositories import (
    ImageRepositoriesResource,
    AsyncImageRepositoriesResource,
    ImageRepositoriesResourceWithRawResponse,
    AsyncImageRepositoriesResourceWithRawResponse,
    ImageRepositoriesResourceWithStreamingResponse,
    AsyncImageRepositoriesResourceWithStreamingResponse,
)
from ....types.beta.deployment_list_response import DeploymentListResponse
from ....types.beta.deployment_create_response import DeploymentCreateResponse
from ....types.beta.deployment_update_response import DeploymentUpdateResponse
from ....types.beta.deployment_get_logs_response import DeploymentGetLogsResponse
from ....types.beta.deployment_retrieve_response import DeploymentRetrieveResponse

__all__ = ["DeploymentsResource", "AsyncDeploymentsResource"]


class DeploymentsResource(SyncAPIResource):
    @cached_property
    def image_repositories(self) -> ImageRepositoriesResource:
        return ImageRepositoriesResource(self._client)

    @cached_property
    def secrets(self) -> SecretsResource:
        return SecretsResource(self._client)

    @cached_property
    def storage(self) -> StorageResource:
        return StorageResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return DeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return DeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        gpu_type: Literal["h100-80gb", " a100-80gb"],
        image: str,
        name: str,
        args: SequenceNotStr[str] | Omit = omit,
        autoscaling: Dict[str, str] | Omit = omit,
        command: SequenceNotStr[str] | Omit = omit,
        cpu: float | Omit = omit,
        description: str | Omit = omit,
        environment_variables: Iterable[deployment_create_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        health_check_path: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[deployment_create_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentCreateResponse:
        """
        Create a new deployment with specified configuration

        Args:
          gpu_type: GPUType specifies the GPU hardware to use (e.g., "h100-80gb").

          image: Image is the container image to deploy from registry.together.ai.

          name: Name is the unique identifier for your deployment. Must contain only
              alphanumeric characters, underscores, or hyphens (1-100 characters)

          args: Args overrides the container's CMD. Provide as an array of arguments (e.g.,
              ["python", "app.py"])

          autoscaling:
              Autoscaling configuration as key-value pairs. Example: {"metric":
              "QueueBacklogPerWorker", "target": "10"} to scale based on queue backlog

          command: Command overrides the container's ENTRYPOINT. Provide as an array (e.g.,
              ["/bin/sh", "-c"])

          cpu: CPU is the number of CPU cores to allocate per container instance (e.g., 0.1 =
              100 milli cores)

          description: Description is an optional human-readable description of your deployment

          environment_variables: EnvironmentVariables is a list of environment variables to set in the container.
              Each must have a name and either a value or value_from_secret

          gpu_count: GPUCount is the number of GPUs to allocate per container instance. Defaults to 0
              if not specified

          health_check_path: HealthCheckPath is the HTTP path for health checks (e.g., "/health"). If set,
              the platform will check this endpoint to determine container health

          max_replicas: MaxReplicas is the maximum number of container instances that can be scaled up
              to. If not set, will be set to MinReplicas

          memory: Memory is the amount of RAM to allocate per container instance in GiB (e.g., 0.5
              = 512MiB)

          min_replicas: MinReplicas is the minimum number of container instances to run. Defaults to 1
              if not specified

          port: Port is the container port your application listens on (e.g., 8080 for web
              servers). Required if your application serves traffic

          storage: Storage is the amount of ephemeral disk storage to allocate per container
              instance (e.g., 10 = 10GiB)

          termination_grace_period_seconds: TerminationGracePeriodSeconds is the time in seconds to wait for graceful
              shutdown before forcefully terminating the replica

          volumes: Volumes is a list of volume mounts to attach to the container. Each mount must
              reference an existing volume by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/deployments",
            body=maybe_transform(
                {
                    "gpu_type": gpu_type,
                    "image": image,
                    "name": name,
                    "args": args,
                    "autoscaling": autoscaling,
                    "command": command,
                    "cpu": cpu,
                    "description": description,
                    "environment_variables": environment_variables,
                    "gpu_count": gpu_count,
                    "health_check_path": health_check_path,
                    "max_replicas": max_replicas,
                    "memory": memory,
                    "min_replicas": min_replicas,
                    "port": port,
                    "storage": storage,
                    "termination_grace_period_seconds": termination_grace_period_seconds,
                    "volumes": volumes,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentRetrieveResponse:
        """
        Retrieve details of a specific deployment by its ID or name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/deployments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        args: SequenceNotStr[str] | Omit = omit,
        autoscaling: Dict[str, str] | Omit = omit,
        command: SequenceNotStr[str] | Omit = omit,
        cpu: float | Omit = omit,
        description: str | Omit = omit,
        environment_variables: Iterable[deployment_update_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        gpu_type: Literal["h100-80gb", " a100-80gb"] | Omit = omit,
        health_check_path: str | Omit = omit,
        image: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        name: str | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[deployment_update_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentUpdateResponse:
        """
        Update an existing deployment configuration

        Args:
          args: Args overrides the container's CMD. Provide as an array of arguments (e.g.,
              ["python", "app.py"])

          autoscaling:
              Autoscaling configuration as key-value pairs. Example: {"metric":
              "QueueBacklogPerWorker", "target": "10"} to scale based on queue backlog

          command: Command overrides the container's ENTRYPOINT. Provide as an array (e.g.,
              ["/bin/sh", "-c"])

          cpu: CPU is the number of CPU cores to allocate per container instance (e.g., 0.1 =
              100 milli cores)

          description: Description is an optional human-readable description of your deployment

          environment_variables: EnvironmentVariables is a list of environment variables to set in the container.
              This will replace all existing environment variables

          gpu_count: GPUCount is the number of GPUs to allocate per container instance

          gpu_type: GPUType specifies the GPU hardware to use (e.g., "h100-80gb")

          health_check_path: HealthCheckPath is the HTTP path for health checks (e.g., "/health"). Set to
              empty string to disable health checks

          image: Image is the container image to deploy from registry.together.ai.

          max_replicas: MaxReplicas is the maximum number of replicas that can be scaled up to.

          memory: Memory is the amount of RAM to allocate per container instance in GiB (e.g., 0.5
              = 512MiB)

          min_replicas: MinReplicas is the minimum number of replicas to run

          name: Name is the new unique identifier for your deployment. Must contain only
              alphanumeric characters, underscores, or hyphens (1-100 characters)

          port: Port is the container port your application listens on (e.g., 8080 for web
              servers)

          storage: Storage is the amount of ephemeral disk storage to allocate per container
              instance (e.g., 10 = 10GiB)

          termination_grace_period_seconds: TerminationGracePeriodSeconds is the time in seconds to wait for graceful
              shutdown before forcefully terminating the replica

          volumes: Volumes is a list of volume mounts to attach to the container. This will replace
              all existing volumes

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/deployments/{id}",
            body=maybe_transform(
                {
                    "args": args,
                    "autoscaling": autoscaling,
                    "command": command,
                    "cpu": cpu,
                    "description": description,
                    "environment_variables": environment_variables,
                    "gpu_count": gpu_count,
                    "gpu_type": gpu_type,
                    "health_check_path": health_check_path,
                    "image": image,
                    "max_replicas": max_replicas,
                    "memory": memory,
                    "min_replicas": min_replicas,
                    "name": name,
                    "port": port,
                    "storage": storage,
                    "termination_grace_period_seconds": termination_grace_period_seconds,
                    "volumes": volumes,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentUpdateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentListResponse:
        """Get a list of all deployments in your project"""
        return self._get(
            "/deployments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete an existing deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/deployments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get_logs(
        self,
        id: str,
        *,
        follow: bool | Omit = omit,
        replica_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentGetLogsResponse:
        """Retrieve logs from a deployment, optionally filtered by replica ID.

        Use
        follow=true to stream logs in real-time.

        Args:
          follow: Stream logs in real-time (ndjson format)

          replica_id: Replica ID to filter logs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/deployments/{id}/logs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "follow": follow,
                        "replica_id": replica_id,
                    },
                    deployment_get_logs_params.DeploymentGetLogsParams,
                ),
            ),
            cast_to=DeploymentGetLogsResponse,
        )


class AsyncDeploymentsResource(AsyncAPIResource):
    @cached_property
    def image_repositories(self) -> AsyncImageRepositoriesResource:
        return AsyncImageRepositoriesResource(self._client)

    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        return AsyncSecretsResource(self._client)

    @cached_property
    def storage(self) -> AsyncStorageResource:
        return AsyncStorageResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        gpu_type: Literal["h100-80gb", " a100-80gb"],
        image: str,
        name: str,
        args: SequenceNotStr[str] | Omit = omit,
        autoscaling: Dict[str, str] | Omit = omit,
        command: SequenceNotStr[str] | Omit = omit,
        cpu: float | Omit = omit,
        description: str | Omit = omit,
        environment_variables: Iterable[deployment_create_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        health_check_path: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[deployment_create_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentCreateResponse:
        """
        Create a new deployment with specified configuration

        Args:
          gpu_type: GPUType specifies the GPU hardware to use (e.g., "h100-80gb").

          image: Image is the container image to deploy from registry.together.ai.

          name: Name is the unique identifier for your deployment. Must contain only
              alphanumeric characters, underscores, or hyphens (1-100 characters)

          args: Args overrides the container's CMD. Provide as an array of arguments (e.g.,
              ["python", "app.py"])

          autoscaling:
              Autoscaling configuration as key-value pairs. Example: {"metric":
              "QueueBacklogPerWorker", "target": "10"} to scale based on queue backlog

          command: Command overrides the container's ENTRYPOINT. Provide as an array (e.g.,
              ["/bin/sh", "-c"])

          cpu: CPU is the number of CPU cores to allocate per container instance (e.g., 0.1 =
              100 milli cores)

          description: Description is an optional human-readable description of your deployment

          environment_variables: EnvironmentVariables is a list of environment variables to set in the container.
              Each must have a name and either a value or value_from_secret

          gpu_count: GPUCount is the number of GPUs to allocate per container instance. Defaults to 0
              if not specified

          health_check_path: HealthCheckPath is the HTTP path for health checks (e.g., "/health"). If set,
              the platform will check this endpoint to determine container health

          max_replicas: MaxReplicas is the maximum number of container instances that can be scaled up
              to. If not set, will be set to MinReplicas

          memory: Memory is the amount of RAM to allocate per container instance in GiB (e.g., 0.5
              = 512MiB)

          min_replicas: MinReplicas is the minimum number of container instances to run. Defaults to 1
              if not specified

          port: Port is the container port your application listens on (e.g., 8080 for web
              servers). Required if your application serves traffic

          storage: Storage is the amount of ephemeral disk storage to allocate per container
              instance (e.g., 10 = 10GiB)

          termination_grace_period_seconds: TerminationGracePeriodSeconds is the time in seconds to wait for graceful
              shutdown before forcefully terminating the replica

          volumes: Volumes is a list of volume mounts to attach to the container. Each mount must
              reference an existing volume by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/deployments",
            body=await async_maybe_transform(
                {
                    "gpu_type": gpu_type,
                    "image": image,
                    "name": name,
                    "args": args,
                    "autoscaling": autoscaling,
                    "command": command,
                    "cpu": cpu,
                    "description": description,
                    "environment_variables": environment_variables,
                    "gpu_count": gpu_count,
                    "health_check_path": health_check_path,
                    "max_replicas": max_replicas,
                    "memory": memory,
                    "min_replicas": min_replicas,
                    "port": port,
                    "storage": storage,
                    "termination_grace_period_seconds": termination_grace_period_seconds,
                    "volumes": volumes,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentRetrieveResponse:
        """
        Retrieve details of a specific deployment by its ID or name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/deployments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        args: SequenceNotStr[str] | Omit = omit,
        autoscaling: Dict[str, str] | Omit = omit,
        command: SequenceNotStr[str] | Omit = omit,
        cpu: float | Omit = omit,
        description: str | Omit = omit,
        environment_variables: Iterable[deployment_update_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        gpu_type: Literal["h100-80gb", " a100-80gb"] | Omit = omit,
        health_check_path: str | Omit = omit,
        image: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        name: str | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[deployment_update_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentUpdateResponse:
        """
        Update an existing deployment configuration

        Args:
          args: Args overrides the container's CMD. Provide as an array of arguments (e.g.,
              ["python", "app.py"])

          autoscaling:
              Autoscaling configuration as key-value pairs. Example: {"metric":
              "QueueBacklogPerWorker", "target": "10"} to scale based on queue backlog

          command: Command overrides the container's ENTRYPOINT. Provide as an array (e.g.,
              ["/bin/sh", "-c"])

          cpu: CPU is the number of CPU cores to allocate per container instance (e.g., 0.1 =
              100 milli cores)

          description: Description is an optional human-readable description of your deployment

          environment_variables: EnvironmentVariables is a list of environment variables to set in the container.
              This will replace all existing environment variables

          gpu_count: GPUCount is the number of GPUs to allocate per container instance

          gpu_type: GPUType specifies the GPU hardware to use (e.g., "h100-80gb")

          health_check_path: HealthCheckPath is the HTTP path for health checks (e.g., "/health"). Set to
              empty string to disable health checks

          image: Image is the container image to deploy from registry.together.ai.

          max_replicas: MaxReplicas is the maximum number of replicas that can be scaled up to.

          memory: Memory is the amount of RAM to allocate per container instance in GiB (e.g., 0.5
              = 512MiB)

          min_replicas: MinReplicas is the minimum number of replicas to run

          name: Name is the new unique identifier for your deployment. Must contain only
              alphanumeric characters, underscores, or hyphens (1-100 characters)

          port: Port is the container port your application listens on (e.g., 8080 for web
              servers)

          storage: Storage is the amount of ephemeral disk storage to allocate per container
              instance (e.g., 10 = 10GiB)

          termination_grace_period_seconds: TerminationGracePeriodSeconds is the time in seconds to wait for graceful
              shutdown before forcefully terminating the replica

          volumes: Volumes is a list of volume mounts to attach to the container. This will replace
              all existing volumes

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/deployments/{id}",
            body=await async_maybe_transform(
                {
                    "args": args,
                    "autoscaling": autoscaling,
                    "command": command,
                    "cpu": cpu,
                    "description": description,
                    "environment_variables": environment_variables,
                    "gpu_count": gpu_count,
                    "gpu_type": gpu_type,
                    "health_check_path": health_check_path,
                    "image": image,
                    "max_replicas": max_replicas,
                    "memory": memory,
                    "min_replicas": min_replicas,
                    "name": name,
                    "port": port,
                    "storage": storage,
                    "termination_grace_period_seconds": termination_grace_period_seconds,
                    "volumes": volumes,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentUpdateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentListResponse:
        """Get a list of all deployments in your project"""
        return await self._get(
            "/deployments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete an existing deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/deployments/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get_logs(
        self,
        id: str,
        *,
        follow: bool | Omit = omit,
        replica_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentGetLogsResponse:
        """Retrieve logs from a deployment, optionally filtered by replica ID.

        Use
        follow=true to stream logs in real-time.

        Args:
          follow: Stream logs in real-time (ndjson format)

          replica_id: Replica ID to filter logs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/deployments/{id}/logs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "follow": follow,
                        "replica_id": replica_id,
                    },
                    deployment_get_logs_params.DeploymentGetLogsParams,
                ),
            ),
            cast_to=DeploymentGetLogsResponse,
        )


class DeploymentsResourceWithRawResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployments.update,
        )
        self.list = to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            deployments.delete,
        )
        self.get_logs = to_raw_response_wrapper(
            deployments.get_logs,
        )

    @cached_property
    def image_repositories(self) -> ImageRepositoriesResourceWithRawResponse:
        return ImageRepositoriesResourceWithRawResponse(self._deployments.image_repositories)

    @cached_property
    def secrets(self) -> SecretsResourceWithRawResponse:
        return SecretsResourceWithRawResponse(self._deployments.secrets)

    @cached_property
    def storage(self) -> StorageResourceWithRawResponse:
        return StorageResourceWithRawResponse(self._deployments.storage)


class AsyncDeploymentsResourceWithRawResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployments.delete,
        )
        self.get_logs = async_to_raw_response_wrapper(
            deployments.get_logs,
        )

    @cached_property
    def image_repositories(self) -> AsyncImageRepositoriesResourceWithRawResponse:
        return AsyncImageRepositoriesResourceWithRawResponse(self._deployments.image_repositories)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithRawResponse:
        return AsyncSecretsResourceWithRawResponse(self._deployments.secrets)

    @cached_property
    def storage(self) -> AsyncStorageResourceWithRawResponse:
        return AsyncStorageResourceWithRawResponse(self._deployments.storage)


class DeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get_logs = to_streamed_response_wrapper(
            deployments.get_logs,
        )

    @cached_property
    def image_repositories(self) -> ImageRepositoriesResourceWithStreamingResponse:
        return ImageRepositoriesResourceWithStreamingResponse(self._deployments.image_repositories)

    @cached_property
    def secrets(self) -> SecretsResourceWithStreamingResponse:
        return SecretsResourceWithStreamingResponse(self._deployments.secrets)

    @cached_property
    def storage(self) -> StorageResourceWithStreamingResponse:
        return StorageResourceWithStreamingResponse(self._deployments.storage)


class AsyncDeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get_logs = async_to_streamed_response_wrapper(
            deployments.get_logs,
        )

    @cached_property
    def image_repositories(self) -> AsyncImageRepositoriesResourceWithStreamingResponse:
        return AsyncImageRepositoriesResourceWithStreamingResponse(self._deployments.image_repositories)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithStreamingResponse:
        return AsyncSecretsResourceWithStreamingResponse(self._deployments.secrets)

    @cached_property
    def storage(self) -> AsyncStorageResourceWithStreamingResponse:
        return AsyncStorageResourceWithStreamingResponse(self._deployments.storage)
