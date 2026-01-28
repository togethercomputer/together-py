# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from .queue import (
    QueueResource,
    AsyncQueueResource,
    QueueResourceWithRawResponse,
    AsyncQueueResourceWithRawResponse,
    QueueResourceWithStreamingResponse,
    AsyncQueueResourceWithStreamingResponse,
)
from .secrets import (
    SecretsResource,
    AsyncSecretsResource,
    SecretsResourceWithRawResponse,
    AsyncSecretsResourceWithRawResponse,
    SecretsResourceWithStreamingResponse,
    AsyncSecretsResourceWithStreamingResponse,
)
from .volumes import (
    VolumesResource,
    AsyncVolumesResource,
    VolumesResourceWithRawResponse,
    AsyncVolumesResourceWithRawResponse,
    VolumesResourceWithStreamingResponse,
    AsyncVolumesResourceWithStreamingResponse,
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
from ....types.beta import jig_deploy_params, jig_update_params, jig_retrieve_logs_params
from ...._base_client import make_request_options
from ....types.beta.deployment import Deployment
from ....types.beta.deployment_logs import DeploymentLogs
from ....types.beta.jig_list_response import JigListResponse

__all__ = ["JigResource", "AsyncJigResource"]


class JigResource(SyncAPIResource):
    @cached_property
    def queue(self) -> QueueResource:
        return QueueResource(self._client)

    @cached_property
    def volumes(self) -> VolumesResource:
        return VolumesResource(self._client)

    @cached_property
    def secrets(self) -> SecretsResource:
        return SecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> JigResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return JigResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JigResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return JigResourceWithStreamingResponse(self)

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
    ) -> Deployment:
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
            cast_to=Deployment,
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
        environment_variables: Iterable[jig_update_params.EnvironmentVariable] | Omit = omit,
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
        volumes: Iterable[jig_update_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
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
                jig_update_params.JigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
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
    ) -> JigListResponse:
        """Get a list of all deployments in your project"""
        return self._get(
            "/deployments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JigListResponse,
        )

    def deploy(
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
        environment_variables: Iterable[jig_deploy_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        health_check_path: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[jig_deploy_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
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
                jig_deploy_params.JigDeployParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
        )

    def destroy(
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

    def retrieve_logs(
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
    ) -> DeploymentLogs:
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
                    jig_retrieve_logs_params.JigRetrieveLogsParams,
                ),
            ),
            cast_to=DeploymentLogs,
        )


class AsyncJigResource(AsyncAPIResource):
    @cached_property
    def queue(self) -> AsyncQueueResource:
        return AsyncQueueResource(self._client)

    @cached_property
    def volumes(self) -> AsyncVolumesResource:
        return AsyncVolumesResource(self._client)

    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        return AsyncSecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncJigResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncJigResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJigResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncJigResourceWithStreamingResponse(self)

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
    ) -> Deployment:
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
            cast_to=Deployment,
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
        environment_variables: Iterable[jig_update_params.EnvironmentVariable] | Omit = omit,
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
        volumes: Iterable[jig_update_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
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
                jig_update_params.JigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
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
    ) -> JigListResponse:
        """Get a list of all deployments in your project"""
        return await self._get(
            "/deployments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JigListResponse,
        )

    async def deploy(
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
        environment_variables: Iterable[jig_deploy_params.EnvironmentVariable] | Omit = omit,
        gpu_count: int | Omit = omit,
        health_check_path: str | Omit = omit,
        max_replicas: int | Omit = omit,
        memory: float | Omit = omit,
        min_replicas: int | Omit = omit,
        port: int | Omit = omit,
        storage: int | Omit = omit,
        termination_grace_period_seconds: int | Omit = omit,
        volumes: Iterable[jig_deploy_params.Volume] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
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
                jig_deploy_params.JigDeployParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
        )

    async def destroy(
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

    async def retrieve_logs(
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
    ) -> DeploymentLogs:
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
                    jig_retrieve_logs_params.JigRetrieveLogsParams,
                ),
            ),
            cast_to=DeploymentLogs,
        )


class JigResourceWithRawResponse:
    def __init__(self, jig: JigResource) -> None:
        self._jig = jig

        self.retrieve = to_raw_response_wrapper(
            jig.retrieve,
        )
        self.update = to_raw_response_wrapper(
            jig.update,
        )
        self.list = to_raw_response_wrapper(
            jig.list,
        )
        self.deploy = to_raw_response_wrapper(
            jig.deploy,
        )
        self.destroy = to_raw_response_wrapper(
            jig.destroy,
        )
        self.retrieve_logs = to_raw_response_wrapper(
            jig.retrieve_logs,
        )

    @cached_property
    def queue(self) -> QueueResourceWithRawResponse:
        return QueueResourceWithRawResponse(self._jig.queue)

    @cached_property
    def volumes(self) -> VolumesResourceWithRawResponse:
        return VolumesResourceWithRawResponse(self._jig.volumes)

    @cached_property
    def secrets(self) -> SecretsResourceWithRawResponse:
        return SecretsResourceWithRawResponse(self._jig.secrets)


class AsyncJigResourceWithRawResponse:
    def __init__(self, jig: AsyncJigResource) -> None:
        self._jig = jig

        self.retrieve = async_to_raw_response_wrapper(
            jig.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            jig.update,
        )
        self.list = async_to_raw_response_wrapper(
            jig.list,
        )
        self.deploy = async_to_raw_response_wrapper(
            jig.deploy,
        )
        self.destroy = async_to_raw_response_wrapper(
            jig.destroy,
        )
        self.retrieve_logs = async_to_raw_response_wrapper(
            jig.retrieve_logs,
        )

    @cached_property
    def queue(self) -> AsyncQueueResourceWithRawResponse:
        return AsyncQueueResourceWithRawResponse(self._jig.queue)

    @cached_property
    def volumes(self) -> AsyncVolumesResourceWithRawResponse:
        return AsyncVolumesResourceWithRawResponse(self._jig.volumes)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithRawResponse:
        return AsyncSecretsResourceWithRawResponse(self._jig.secrets)


class JigResourceWithStreamingResponse:
    def __init__(self, jig: JigResource) -> None:
        self._jig = jig

        self.retrieve = to_streamed_response_wrapper(
            jig.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            jig.update,
        )
        self.list = to_streamed_response_wrapper(
            jig.list,
        )
        self.deploy = to_streamed_response_wrapper(
            jig.deploy,
        )
        self.destroy = to_streamed_response_wrapper(
            jig.destroy,
        )
        self.retrieve_logs = to_streamed_response_wrapper(
            jig.retrieve_logs,
        )

    @cached_property
    def queue(self) -> QueueResourceWithStreamingResponse:
        return QueueResourceWithStreamingResponse(self._jig.queue)

    @cached_property
    def volumes(self) -> VolumesResourceWithStreamingResponse:
        return VolumesResourceWithStreamingResponse(self._jig.volumes)

    @cached_property
    def secrets(self) -> SecretsResourceWithStreamingResponse:
        return SecretsResourceWithStreamingResponse(self._jig.secrets)


class AsyncJigResourceWithStreamingResponse:
    def __init__(self, jig: AsyncJigResource) -> None:
        self._jig = jig

        self.retrieve = async_to_streamed_response_wrapper(
            jig.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            jig.update,
        )
        self.list = async_to_streamed_response_wrapper(
            jig.list,
        )
        self.deploy = async_to_streamed_response_wrapper(
            jig.deploy,
        )
        self.destroy = async_to_streamed_response_wrapper(
            jig.destroy,
        )
        self.retrieve_logs = async_to_streamed_response_wrapper(
            jig.retrieve_logs,
        )

    @cached_property
    def queue(self) -> AsyncQueueResourceWithStreamingResponse:
        return AsyncQueueResourceWithStreamingResponse(self._jig.queue)

    @cached_property
    def volumes(self) -> AsyncVolumesResourceWithStreamingResponse:
        return AsyncVolumesResourceWithStreamingResponse(self._jig.volumes)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithStreamingResponse:
        return AsyncSecretsResourceWithStreamingResponse(self._jig.secrets)
