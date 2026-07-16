# Together

Types:

```python
from together.types import WhoamiResponse
```

Methods:

- <code title="get /whoami">client.<a href="./src/together/_client.py">whoami</a>() -> <a href="./src/together/types/whoami_response.py">WhoamiResponse</a></code>

# Beta

## Endpoints

Types:

```python
from together.types.beta import (
    AbMember,
    DeploymentAutoscaling,
    DeploymentPlacementConfig,
    DeploymentStatus,
    Endpoint,
    EndpointDeployment,
    EndpointDeploymentSummary,
    EndpointTrafficSplitEntry,
    ShadowAdaptiveKeyBasedSampling,
    ShadowAdaptiveUniformSampling,
    ShadowEndpointSource,
    ShadowKeyBasedSampling,
    ShadowSource,
    ShadowUniformSampling,
    EndpointDeleteResponse,
    EndpointAnalyticsResponse,
    EndpointListEventsResponse,
)
```

Methods:

- <code title="post /projects/{projectId}/endpoints">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">create</a>(\*, project_id, \*\*<a href="src/together/types/beta/endpoint_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint.py">Endpoint</a></code>
- <code title="get /projects/{projectId}/endpoints/{id}">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/beta/endpoint.py">Endpoint</a></code>
- <code title="patch /projects/{projectId}/endpoints/{id}">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">update</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/endpoint_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint.py">Endpoint</a></code>
- <code title="get /projects/{projectId}/endpoints">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">list</a>(\*, project_id, \*\*<a href="src/together/types/beta/endpoint_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint.py">SyncCursorPagination[Endpoint]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{id}">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">delete</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/endpoint_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_delete_response.py">EndpointDeleteResponse</a></code>
- <code title="get /projects/{projectId}/endpoints/{id}/analytics">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">analytics</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/endpoint_analytics_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_analytics_response.py">EndpointAnalyticsResponse</a></code>
- <code title="get /projects/{projectId}/endpoints/{id}/events">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">list_events</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/endpoint_list_events_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_list_events_response.py">SyncCursorPagination[EndpointListEventsResponse]</a></code>
- <code title="get /organizations/{organizationId}/endpoints">client.beta.endpoints.<a href="./src/together/resources/beta/endpoints/endpoints.py">list_org_scoped</a>(organization_id, \*\*<a href="src/together/types/beta/endpoint_list_org_scoped_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint.py">SyncCursorPagination[Endpoint]</a></code>

### PlacementProfiles

Types:

```python
from together.types.beta.endpoints import PlacementProfile
```

Methods:

- <code title="get /projects/{projectId}/placement-profiles/{id}">client.beta.endpoints.placement_profiles.<a href="./src/together/resources/beta/endpoints/placement_profiles.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/beta/endpoints/placement_profile.py">PlacementProfile</a></code>
- <code title="get /projects/{projectId}/placement-profiles">client.beta.endpoints.placement_profiles.<a href="./src/together/resources/beta/endpoints/placement_profiles.py">list</a>(\*, project_id, \*\*<a href="src/together/types/beta/endpoints/placement_profile_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/placement_profile.py">SyncCursorPagination[PlacementProfile]</a></code>

### AbExperiments

Types:

```python
from together.types.beta.endpoints import AbExperiment, AbExperimentDeleteResponse
```

Methods:

- <code title="post /projects/{projectId}/endpoints/{endpointId}/abExperiments">client.beta.endpoints.ab_experiments.<a href="./src/together/resources/beta/endpoints/ab_experiments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/ab_experiment_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.beta.endpoints.ab_experiments.<a href="./src/together/resources/beta/endpoints/ab_experiments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/beta/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="patch /projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.beta.endpoints.ab_experiments.<a href="./src/together/resources/beta/endpoints/ab_experiments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/ab_experiment_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/abExperiments">client.beta.endpoints.ab_experiments.<a href="./src/together/resources/beta/endpoints/ab_experiments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/ab_experiment_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/ab_experiment.py">SyncCursorPagination[AbExperiment]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.beta.endpoints.ab_experiments.<a href="./src/together/resources/beta/endpoints/ab_experiments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/ab_experiment_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/ab_experiment_delete_response.py">AbExperimentDeleteResponse</a></code>

### ShadowExperiments

Types:

```python
from together.types.beta.endpoints import ShadowExperiment, ShadowExperimentDeleteResponse
```

Methods:

- <code title="post /projects/{projectId}/endpoints/{endpointId}/shadowExperiments">client.beta.endpoints.shadow_experiments.<a href="./src/together/resources/beta/endpoints/shadow_experiments/shadow_experiments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiment_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.beta.endpoints.shadow_experiments.<a href="./src/together/resources/beta/endpoints/shadow_experiments/shadow_experiments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/beta/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="patch /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.beta.endpoints.shadow_experiments.<a href="./src/together/resources/beta/endpoints/shadow_experiments/shadow_experiments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiment_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/shadowExperiments">client.beta.endpoints.shadow_experiments.<a href="./src/together/resources/beta/endpoints/shadow_experiments/shadow_experiments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiment_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiment.py">SyncCursorPagination[ShadowExperiment]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.beta.endpoints.shadow_experiments.<a href="./src/together/resources/beta/endpoints/shadow_experiments/shadow_experiments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiment_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiment_delete_response.py">ShadowExperimentDeleteResponse</a></code>

#### Targets

Types:

```python
from together.types.beta.endpoints.shadow_experiments import (
    ShadowExperimentTarget,
    TargetDeleteResponse,
)
```

Methods:

- <code title="post /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets">client.beta.endpoints.shadow_experiments.targets.<a href="./src/together/resources/beta/endpoints/shadow_experiments/targets.py">create</a>(\*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiments/target_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.beta.endpoints.shadow_experiments.targets.<a href="./src/together/resources/beta/endpoints/shadow_experiments/targets.py">retrieve</a>(id, \*, project_id, endpoint_id, experiment_id) -> <a href="./src/together/types/beta/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="patch /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.beta.endpoints.shadow_experiments.targets.<a href="./src/together/resources/beta/endpoints/shadow_experiments/targets.py">update</a>(id, \*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiments/target_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets">client.beta.endpoints.shadow_experiments.targets.<a href="./src/together/resources/beta/endpoints/shadow_experiments/targets.py">list</a>(endpoint_id, experiment_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiments/target_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiments/shadow_experiment_target.py">SyncCursorPagination[ShadowExperimentTarget]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.beta.endpoints.shadow_experiments.targets.<a href="./src/together/resources/beta/endpoints/shadow_experiments/targets.py">delete</a>(id, \*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/beta/endpoints/shadow_experiments/target_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/shadow_experiments/target_delete_response.py">TargetDeleteResponse</a></code>

### Hardware

Types:

```python
from together.types.beta.endpoints import InferenceInstanceType, HardwareListResponse
```

Methods:

- <code title="get /public/inference-instance-types/{id}">client.beta.endpoints.hardware.<a href="./src/together/resources/beta/endpoints/hardware.py">retrieve</a>(id) -> <a href="./src/together/types/beta/endpoints/inference_instance_type.py">InferenceInstanceType</a></code>
- <code title="get /public/inference-instance-types">client.beta.endpoints.hardware.<a href="./src/together/resources/beta/endpoints/hardware.py">list</a>() -> <a href="./src/together/types/beta/endpoints/hardware_list_response.py">HardwareListResponse</a></code>

### Adapters

Types:

```python
from together.types.beta.endpoints import (
    AdapterCreateResponse,
    AdapterRetrieveResponse,
    AdapterUpdateResponse,
    AdapterListResponse,
    AdapterDeleteResponse,
)
```

Methods:

- <code title="post /projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters">client.beta.endpoints.adapters.<a href="./src/together/resources/beta/endpoints/adapters.py">create</a>(\*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/beta/endpoints/adapter_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/adapter_create_response.py">AdapterCreateResponse</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.beta.endpoints.adapters.<a href="./src/together/resources/beta/endpoints/adapters.py">retrieve</a>(id, \*, project_id, endpoint_id, deployment_id) -> <a href="./src/together/types/beta/endpoints/adapter_retrieve_response.py">AdapterRetrieveResponse</a></code>
- <code title="patch /projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.beta.endpoints.adapters.<a href="./src/together/resources/beta/endpoints/adapters.py">update</a>(id, \*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/beta/endpoints/adapter_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/adapter_update_response.py">AdapterUpdateResponse</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters">client.beta.endpoints.adapters.<a href="./src/together/resources/beta/endpoints/adapters.py">list</a>(endpoint_id, deployment_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/adapter_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/adapter_list_response.py">SyncCursorPagination[AdapterListResponse]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.beta.endpoints.adapters.<a href="./src/together/resources/beta/endpoints/adapters.py">delete</a>(id, \*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/beta/endpoints/adapter_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/adapter_delete_response.py">AdapterDeleteResponse</a></code>

### Deployments

Types:

```python
from together.types.beta.endpoints import DeploymentDeleteResponse
```

Methods:

- <code title="post /projects/{projectId}/endpoints/{endpointId}/deployments">client.beta.endpoints.deployments.<a href="./src/together/resources/beta/endpoints/deployments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/deployment_create_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.beta.endpoints.deployments.<a href="./src/together/resources/beta/endpoints/deployments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/beta/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="patch /projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.beta.endpoints.deployments.<a href="./src/together/resources/beta/endpoints/deployments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/deployment_update_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="get /projects/{projectId}/endpoints/{endpointId}/deployments">client.beta.endpoints.deployments.<a href="./src/together/resources/beta/endpoints/deployments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/beta/endpoints/deployment_list_params.py">params</a>) -> <a href="./src/together/types/beta/endpoint_deployment.py">SyncCursorPagination[EndpointDeployment]</a></code>
- <code title="delete /projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.beta.endpoints.deployments.<a href="./src/together/resources/beta/endpoints/deployments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/beta/endpoints/deployment_delete_params.py">params</a>) -> <a href="./src/together/types/beta/endpoints/deployment_delete_response.py">DeploymentDeleteResponse</a></code>

## Models

Types:

```python
from together.types.beta import (
    Model,
    SupportedModel,
    SupportedModelDeploymentProfile,
    SupportedModelPerformanceBenchmarks,
    ModelDeleteResponse,
    ModelListFilesResponse,
    ModelListRevisionsResponse,
)
```

Methods:

- <code title="post /projects/{projectId}/models">client.beta.models.<a href="./src/together/resources/beta/models/models.py">create</a>(\*, project_id, \*\*<a href="src/together/types/beta/model_create_params.py">params</a>) -> <a href="./src/together/types/beta/model.py">Model</a></code>
- <code title="get /projects/{projectId}/models/{id}">client.beta.models.<a href="./src/together/resources/beta/models/models.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/beta/model.py">Model</a></code>
- <code title="patch /projects/{projectId}/models/{id}">client.beta.models.<a href="./src/together/resources/beta/models/models.py">update</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/model_update_params.py">params</a>) -> <a href="./src/together/types/beta/model.py">Model</a></code>
- <code title="get /projects/{projectId}/models">client.beta.models.<a href="./src/together/resources/beta/models/models.py">list</a>(\*, project_id, \*\*<a href="src/together/types/beta/model_list_params.py">params</a>) -> <a href="./src/together/types/beta/model.py">SyncCursorPagination[Model]</a></code>
- <code title="delete /projects/{projectId}/models/{id}">client.beta.models.<a href="./src/together/resources/beta/models/models.py">delete</a>(id, \*, project_id) -> <a href="./src/together/types/beta/model_delete_response.py">ModelDeleteResponse</a></code>
- <code title="get /projects/{projectId}/models/{id}/files">client.beta.models.<a href="./src/together/resources/beta/models/models.py">list_files</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/model_list_files_params.py">params</a>) -> <a href="./src/together/types/beta/model_list_files_response.py">ModelListFilesResponse</a></code>
- <code title="get /organizations/{organizationId}/models">client.beta.models.<a href="./src/together/resources/beta/models/models.py">list_org_scoped</a>(organization_id, \*\*<a href="src/together/types/beta/model_list_org_scoped_params.py">params</a>) -> <a href="./src/together/types/beta/model.py">SyncCursorPagination[Model]</a></code>
- <code title="get /projects/{projectId}/models/{id}/revisions">client.beta.models.<a href="./src/together/resources/beta/models/models.py">list_revisions</a>(id, \*, project_id) -> <a href="./src/together/types/beta/model_list_revisions_response.py">ModelListRevisionsResponse</a></code>
- <code title="get /supported-models">client.beta.models.<a href="./src/together/resources/beta/models/models.py">list_supported</a>(\*\*<a href="src/together/types/beta/model_list_supported_params.py">params</a>) -> <a href="./src/together/types/beta/supported_model.py">SyncCursorPagination[SupportedModel]</a></code>
- <code title="get /supported-models/{id}">client.beta.models.<a href="./src/together/resources/beta/models/models.py">retrieve_supported</a>(id) -> <a href="./src/together/types/beta/supported_model.py">SupportedModel</a></code>

### RemoteUploads

Types:

```python
from together.types.beta.models import (
    RemoteUploadCreateResponse,
    RemoteUploadRetrieveResponse,
    RemoteUploadListResponse,
    RemoteUploadEventsResponse,
)
```

Methods:

- <code title="post /projects/{projectId}/models/uploads">client.beta.models.remote_uploads.<a href="./src/together/resources/beta/models/remote_uploads.py">create</a>(\*, project_id, \*\*<a href="src/together/types/beta/models/remote_upload_create_params.py">params</a>) -> <a href="./src/together/types/beta/models/remote_upload_create_response.py">RemoteUploadCreateResponse</a></code>
- <code title="get /projects/{projectId}/models/uploads/{id}">client.beta.models.remote_uploads.<a href="./src/together/resources/beta/models/remote_uploads.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/beta/models/remote_upload_retrieve_response.py">RemoteUploadRetrieveResponse</a></code>
- <code title="get /projects/{projectId}/models/uploads">client.beta.models.remote_uploads.<a href="./src/together/resources/beta/models/remote_uploads.py">list</a>(\*, project_id, \*\*<a href="src/together/types/beta/models/remote_upload_list_params.py">params</a>) -> <a href="./src/together/types/beta/models/remote_upload_list_response.py">SyncCursorPagination[RemoteUploadListResponse]</a></code>
- <code title="get /projects/{projectId}/models/uploads/{id}/events">client.beta.models.remote_uploads.<a href="./src/together/resources/beta/models/remote_uploads.py">events</a>(id, \*, project_id, \*\*<a href="src/together/types/beta/models/remote_upload_events_params.py">params</a>) -> <a href="./src/together/types/beta/models/remote_upload_events_response.py">RemoteUploadEventsResponse</a></code>

### Configs

Types:

```python
from together.types.beta.models import Config
```

Methods:

- <code title="get /projects/{projectId}/configs/{id}">client.beta.models.configs.<a href="./src/together/resources/beta/models/configs.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/beta/models/config.py">Config</a></code>
- <code title="get /projects/{projectId}/configs">client.beta.models.configs.<a href="./src/together/resources/beta/models/configs.py">list</a>(\*, project_id, \*\*<a href="src/together/types/beta/models/config_list_params.py">params</a>) -> <a href="./src/together/types/beta/models/config.py">SyncCursorPagination[Config]</a></code>

## Jig

Types:

```python
from together.types.beta import (
    ContainerDeploymentStatus,
    Deployment,
    DeploymentLogs,
    JigListResponse,
)
```

Methods:

- <code title="get /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve</a>(id) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="patch /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">update</a>(id, \*\*<a href="src/together/types/beta/jig_update_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="get /deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">list</a>() -> <a href="./src/together/types/beta/jig_list_response.py">JigListResponse</a></code>
- <code title="post /deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">deploy</a>(\*\*<a href="src/together/types/beta/jig_deploy_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="delete /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">destroy</a>(id) -> object</code>
- <code title="get /deployments/{id}/logs">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve_logs</a>(id, \*\*<a href="src/together/types/beta/jig_retrieve_logs_params.py">params</a>) -> <a href="./src/together/types/beta/deployment_logs.py">DeploymentLogs</a></code>

### Queue

Types:

```python
from together.types.beta.jig import (
    QueueRetrieveResponse,
    QueueCancelResponse,
    QueueClearResponse,
    QueueMetricsResponse,
    QueueSubmitResponse,
)
```

Methods:

- <code title="get /queue/status">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">retrieve</a>(\*\*<a href="src/together/types/beta/jig/queue_retrieve_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_retrieve_response.py">QueueRetrieveResponse</a></code>
- <code title="post /queue/cancel">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">cancel</a>(\*\*<a href="src/together/types/beta/jig/queue_cancel_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_cancel_response.py">QueueCancelResponse</a></code>
- <code title="post /queue/clear">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">clear</a>(\*\*<a href="src/together/types/beta/jig/queue_clear_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_clear_response.py">QueueClearResponse</a></code>
- <code title="get /queue/metrics">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">metrics</a>(\*\*<a href="src/together/types/beta/jig/queue_metrics_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_metrics_response.py">QueueMetricsResponse</a></code>
- <code title="post /queue/submit">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">submit</a>(\*\*<a href="src/together/types/beta/jig/queue_submit_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_submit_response.py">QueueSubmitResponse</a></code>

### Volumes

Types:

```python
from together.types.beta.jig import Volume, VolumeListResponse
```

Methods:

- <code title="post /deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">create</a>(\*\*<a href="src/together/types/beta/jig/volume_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">retrieve</a>(id, \*\*<a href="src/together/types/beta/jig/volume_retrieve_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="patch /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/volume_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">list</a>() -> <a href="./src/together/types/beta/jig/volume_list_response.py">VolumeListResponse</a></code>
- <code title="delete /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">delete</a>(id) -> object</code>

### Secrets

Types:

```python
from together.types.beta.jig import Secret, SecretListResponse
```

Methods:

- <code title="post /deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">create</a>(\*\*<a href="src/together/types/beta/jig/secret_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">retrieve</a>(id) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="patch /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/secret_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">list</a>() -> <a href="./src/together/types/beta/jig/secret_list_response.py">SecretListResponse</a></code>
- <code title="delete /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">delete</a>(id) -> object</code>

## Clusters

Types:

```python
from together.types.beta import (
    Cluster,
    ClusterListResponse,
    ClusterDeleteResponse,
    ClusterListRegionsResponse,
)
```

Methods:

- <code title="post /compute/clusters">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">create</a>(\*\*<a href="src/together/types/beta/cluster_create_params.py">params</a>) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="get /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">retrieve</a>(cluster_id) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="put /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">update</a>(cluster_id, \*\*<a href="src/together/types/beta/cluster_update_params.py">params</a>) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="get /compute/clusters">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">list</a>(\*\*<a href="src/together/types/beta/cluster_list_params.py">params</a>) -> <a href="./src/together/types/beta/cluster_list_response.py">ClusterListResponse</a></code>
- <code title="delete /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">delete</a>(cluster_id) -> <a href="./src/together/types/beta/cluster_delete_response.py">ClusterDeleteResponse</a></code>
- <code title="get /compute/regions">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">list_regions</a>() -> <a href="./src/together/types/beta/cluster_list_regions_response.py">ClusterListRegionsResponse</a></code>

### Remediations

Types:

```python
from together.types.beta.clusters import Remediation, RemediationListResponse
```

Methods:

- <code title="post /compute/clusters/{cluster_id}/instances/{instance_id}/remediations">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">create</a>(instance_id, \*, cluster_id, \*\*<a href="src/together/types/beta/clusters/remediation_create_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/remediation.py">Remediation</a></code>
- <code title="get /compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">retrieve</a>(remediation_id, \*, cluster_id, instance_id) -> <a href="./src/together/types/beta/clusters/remediation.py">Remediation</a></code>
- <code title="get /compute/clusters/{cluster_id}/instances/{instance_id}/remediations">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">list</a>(instance_id, \*, cluster_id, \*\*<a href="src/together/types/beta/clusters/remediation_list_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/remediation_list_response.py">RemediationListResponse</a></code>
- <code title="post /compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/approve">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">approve</a>(remediation_id, \*, cluster_id, instance_id, \*\*<a href="src/together/types/beta/clusters/remediation_approve_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/remediation.py">Remediation</a></code>
- <code title="post /compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/cancel">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">cancel</a>(remediation_id, \*, cluster_id, instance_id) -> <a href="./src/together/types/beta/clusters/remediation.py">Remediation</a></code>
- <code title="post /compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/reject">client.beta.clusters.remediations.<a href="./src/together/resources/beta/clusters/remediations.py">reject</a>(remediation_id, \*, cluster_id, instance_id, \*\*<a href="src/together/types/beta/clusters/remediation_reject_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/remediation.py">Remediation</a></code>

### Storage

Types:

```python
from together.types.beta.clusters import ClusterStorage, StorageListResponse, StorageDeleteResponse
```

Methods:

- <code title="post /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">create</a>(\*\*<a href="src/together/types/beta/clusters/storage_create_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /compute/clusters/storage/volumes/{volume_id}">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">retrieve</a>(volume_id) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="put /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">update</a>(\*\*<a href="src/together/types/beta/clusters/storage_update_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">list</a>(\*\*<a href="src/together/types/beta/clusters/storage_list_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/storage_list_response.py">StorageListResponse</a></code>
- <code title="delete /compute/clusters/storage/volumes/{volume_id}">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">delete</a>(volume_id) -> <a href="./src/together/types/beta/clusters/storage_delete_response.py">StorageDeleteResponse</a></code>

# Chat

## Completions

Types:

```python
from together.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionPrompt,
    ChatCompletionStructuredMessageImageURL,
    ChatCompletionStructuredMessageText,
    ChatCompletionStructuredMessageVideoURL,
    ChatCompletionUsage,
    ChatCompletionWarning,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/together/resources/chat/completions.py">create</a>(\*\*<a href="src/together/types/chat/completion_create_params.py">params</a>) -> <a href="./src/together/types/chat/chat_completion.py">ChatCompletion</a></code>

# Completions

Types:

```python
from together.types import Completion, CompletionChunk, LogProbs, ToolChoice, Tools
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/together/resources/completions.py">create</a>(\*\*<a href="src/together/types/completion_create_params.py">params</a>) -> <a href="./src/together/types/completion.py">Completion</a></code>

# Embeddings

Types:

```python
from together.types import Embedding
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/together/resources/embeddings.py">create</a>(\*\*<a href="src/together/types/embedding_create_params.py">params</a>) -> <a href="./src/together/types/embedding.py">Embedding</a></code>

# Files

Types:

```python
from together.types import FileList, FilePurpose, FileResponse, FileType, FileDeleteResponse
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/together/resources/files.py">retrieve</a>(id) -> <a href="./src/together/types/file_response.py">FileResponse</a></code>
- <code title="get /files">client.files.<a href="./src/together/resources/files.py">list</a>() -> <a href="./src/together/types/file_list.py">FileList</a></code>
- <code title="delete /files/{id}">client.files.<a href="./src/together/resources/files.py">delete</a>(id) -> <a href="./src/together/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /files/{id}/content">client.files.<a href="./src/together/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>

# FineTuning

Types:

```python
from together.types import (
    FinetuneEvent,
    FinetuneEventType,
    FinetuneModelLimits,
    FinetuneResponse,
    FineTuningListResponse,
    FineTuningDeleteResponse,
    FineTuningCancelResponse,
    FineTuningEstimatePriceResponse,
    FineTuningListCheckpointsResponse,
    FineTuningListEventsResponse,
    FineTuningListMetricsResponse,
    FineTuningModelLimitsResponse,
)
```

Methods:

- <code title="get /fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">retrieve</a>(id) -> <a href="./src/together/types/finetune_response.py">FinetuneResponse</a></code>
- <code title="get /fine-tunes">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list</a>() -> <a href="./src/together/types/fine_tuning_list_response.py">FineTuningListResponse</a></code>
- <code title="delete /fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">delete</a>(id, \*\*<a href="src/together/types/fine_tuning_delete_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_delete_response.py">FineTuningDeleteResponse</a></code>
- <code title="post /fine-tunes/{id}/cancel">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">cancel</a>(id) -> <a href="./src/together/types/fine_tuning_cancel_response.py">FineTuningCancelResponse</a></code>
- <code title="get /finetune/download">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">content</a>(\*\*<a href="src/together/types/fine_tuning_content_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="post /fine-tunes/estimate-price">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">estimate_price</a>(\*\*<a href="src/together/types/fine_tuning_estimate_price_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_estimate_price_response.py">FineTuningEstimatePriceResponse</a></code>
- <code title="get /fine-tunes/{id}/checkpoints">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_checkpoints</a>(id) -> <a href="./src/together/types/fine_tuning_list_checkpoints_response.py">FineTuningListCheckpointsResponse</a></code>
- <code title="get /fine-tunes/{id}/events">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_events</a>(id) -> <a href="./src/together/types/fine_tuning_list_events_response.py">FineTuningListEventsResponse</a></code>
- <code title="get /fine-tunes/{id}/metrics">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_metrics</a>(id, \*\*<a href="src/together/types/fine_tuning_list_metrics_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_list_metrics_response.py">FineTuningListMetricsResponse</a></code>
- <code title="get /fine-tunes/models/limits">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">model_limits</a>(\*\*<a href="src/together/types/fine_tuning_model_limits_params.py">params</a>) -> <a href="./src/together/types/finetune_model_limits.py">FinetuneModelLimits</a></code>

# CodeInterpreter

Types:

```python
from together.types import ExecuteResponse
```

Methods:

- <code title="post /tci/execute">client.code_interpreter.<a href="./src/together/resources/code_interpreter/code_interpreter.py">execute</a>(\*\*<a href="src/together/types/code_interpreter_execute_params.py">params</a>) -> <a href="./src/together/types/execute_response.py">ExecuteResponse</a></code>

## Sessions

Types:

```python
from together.types.code_interpreter import SessionListResponse
```

Methods:

- <code title="get /tci/sessions">client.code_interpreter.sessions.<a href="./src/together/resources/code_interpreter/sessions.py">list</a>() -> <a href="./src/together/types/code_interpreter/session_list_response.py">SessionListResponse</a></code>

# Images

Types:

```python
from together.types import ImageDataB64, ImageDataURL, ImageFile
```

Methods:

- <code title="post /images/generations">client.images.<a href="./src/together/resources/images.py">generate</a>(\*\*<a href="src/together/types/image_generate_params.py">params</a>) -> <a href="./src/together/types/image_file.py">ImageFile</a></code>

# Videos

Types:

```python
from together.types import VideoJob
```

Methods:

- <code title="post /videos">client.videos.<a href="./src/together/resources/videos.py">create</a>(\*\*<a href="src/together/types/video_create_params.py">params</a>) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>
- <code title="get /videos/{id}">client.videos.<a href="./src/together/resources/videos.py">retrieve</a>(id) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>

# Audio

Types:

```python
from together.types import AudioFile, AudioSpeechStreamChunk
```

## Speech

Methods:

- <code title="post /audio/speech">client.audio.speech.<a href="./src/together/resources/audio/speech.py">create</a>(\*\*<a href="src/together/types/audio/speech_create_params.py">params</a>) -> BinaryAPIResponse</code>

## Voices

Types:

```python
from together.types.audio import VoiceListResponse
```

Methods:

- <code title="get /voices">client.audio.voices.<a href="./src/together/resources/audio/voices.py">list</a>() -> <a href="./src/together/types/audio/voice_list_response.py">VoiceListResponse</a></code>

## Transcriptions

Types:

```python
from together.types.audio import TranscriptionCreateResponse
```

Methods:

- <code title="post /audio/transcriptions">client.audio.transcriptions.<a href="./src/together/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/together/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/together/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>

## Translations

Types:

```python
from together.types.audio import TranslationCreateResponse
```

Methods:

- <code title="post /audio/translations">client.audio.translations.<a href="./src/together/resources/audio/translations.py">create</a>(\*\*<a href="src/together/types/audio/translation_create_params.py">params</a>) -> <a href="./src/together/types/audio/translation_create_response.py">TranslationCreateResponse</a></code>

# Models

Types:

```python
from together.types import ModelObject, ModelListResponse, ModelUploadResponse
```

Methods:

- <code title="get /models">client.models.<a href="./src/together/resources/models/models.py">list</a>(\*\*<a href="src/together/types/model_list_params.py">params</a>) -> <a href="./src/together/types/model_list_response.py">ModelListResponse</a></code>
- <code title="post /models">client.models.<a href="./src/together/resources/models/models.py">upload</a>(\*\*<a href="src/together/types/model_upload_params.py">params</a>) -> <a href="./src/together/types/model_upload_response.py">ModelUploadResponse</a></code>

## Uploads

Types:

```python
from together.types.models import UploadStatusResponse
```

Methods:

- <code title="get /jobs/{jobId}">client.models.uploads.<a href="./src/together/resources/models/uploads.py">status</a>(job_id) -> <a href="./src/together/types/models/upload_status_response.py">UploadStatusResponse</a></code>

# Endpoints

Types:

```python
from together.types import (
    Autoscaling,
    DedicatedEndpoint,
    EndpointListResponse,
    EndpointListAvzonesResponse,
    EndpointListHardwareResponse,
)
```

Methods:

- <code title="post /endpoints">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">create</a>(\*\*<a href="src/together/types/endpoint_create_params.py">params</a>) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="get /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">retrieve</a>(endpoint_id) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="patch /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">update</a>(endpoint_id, \*\*<a href="src/together/types/endpoint_update_params.py">params</a>) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="get /endpoints">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list</a>(\*\*<a href="src/together/types/endpoint_list_params.py">params</a>) -> <a href="./src/together/types/endpoint_list_response.py">EndpointListResponse</a></code>
- <code title="delete /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">delete</a>(endpoint_id) -> None</code>
- <code title="get /clusters/availability-zones">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list_avzones</a>() -> <a href="./src/together/types/endpoint_list_avzones_response.py">EndpointListAvzonesResponse</a></code>
- <code title="get /hardware">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list_hardware</a>(\*\*<a href="src/together/types/endpoint_list_hardware_params.py">params</a>) -> <a href="./src/together/types/endpoint_list_hardware_response.py">EndpointListHardwareResponse</a></code>

## Adapters

Types:

```python
from together.types.endpoints import AdapterListResponse, AdapterAddResponse, AdapterRemoveResponse
```

Methods:

- <code title="get /endpoints/{endpointId}/adapters">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">list</a>(endpoint_id) -> <a href="./src/together/types/endpoints/adapter_list_response.py">AdapterListResponse</a></code>
- <code title="post /endpoints/{endpointId}/adapters">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">add</a>(endpoint_id, \*\*<a href="src/together/types/endpoints/adapter_add_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_add_response.py">AdapterAddResponse</a></code>
- <code title="delete /endpoints/{endpointId}/adapters">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">remove</a>(endpoint_id, \*\*<a href="src/together/types/endpoints/adapter_remove_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_remove_response.py">AdapterRemoveResponse</a></code>

# Rerank

Types:

```python
from together.types import RerankCreateResponse
```

Methods:

- <code title="post /rerank">client.rerank.<a href="./src/together/resources/rerank.py">create</a>(\*\*<a href="src/together/types/rerank_create_params.py">params</a>) -> <a href="./src/together/types/rerank_create_response.py">RerankCreateResponse</a></code>

# Batches

Types:

```python
from together.types import BatchJob, BatchCreateResponse, BatchListResponse
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/together/resources/batches.py">create</a>(\*\*<a href="src/together/types/batch_create_params.py">params</a>) -> <a href="./src/together/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batches/{id}">client.batches.<a href="./src/together/resources/batches.py">retrieve</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>
- <code title="get /batches">client.batches.<a href="./src/together/resources/batches.py">list</a>() -> <a href="./src/together/types/batch_list_response.py">BatchListResponse</a></code>
- <code title="post /batches/{id}/cancel">client.batches.<a href="./src/together/resources/batches.py">cancel</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>

# Evals

Types:

```python
from together.types import EvaluationJob, EvalCreateResponse, EvalListResponse, EvalStatusResponse
```

Methods:

- <code title="post /evaluation">client.evals.<a href="./src/together/resources/evals.py">create</a>(\*\*<a href="src/together/types/eval_create_params.py">params</a>) -> <a href="./src/together/types/eval_create_response.py">EvalCreateResponse</a></code>
- <code title="get /evaluation/{id}">client.evals.<a href="./src/together/resources/evals.py">retrieve</a>(id) -> <a href="./src/together/types/evaluation_job.py">EvaluationJob</a></code>
- <code title="get /evaluation">client.evals.<a href="./src/together/resources/evals.py">list</a>(\*\*<a href="src/together/types/eval_list_params.py">params</a>) -> <a href="./src/together/types/eval_list_response.py">EvalListResponse</a></code>
- <code title="get /evaluation/{id}/status">client.evals.<a href="./src/together/resources/evals.py">status</a>(id) -> <a href="./src/together/types/eval_status_response.py">EvalStatusResponse</a></code>
