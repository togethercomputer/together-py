# Together

Types:

```python
from together.types import (
    WhoamiAPIKey,
    WhoamiOrgAPIKey,
    WhoamiOrganization,
    WhoamiProject,
    WhoamiProjectAPIKey,
    WhoamiResponse,
    WhoamiUser,
    WhoamiUserJwt,
    WhoamiUserOrgJwt,
    WhoamiUserOrgProjectJwt,
)
```

Methods:

- <code title="get /v3/whoami">client.<a href="./src/together/_client.py">whoami</a>() -> <a href="./src/together/types/whoami_response.py">WhoamiResponse</a></code>

# Beta

## Jig

Types:

```python
from together.types.beta import (
    ContainerDeploymentStatus,
    Deployment,
    DeploymentLogs,
    DeploymentRevision,
    DeploymentRevisionEvent,
    DeploymentRevisionEventList,
    JigListResponse,
)
```

Methods:

- <code title="get /v1/deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve</a>(id) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="patch /v1/deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">update</a>(id, \*\*<a href="src/together/types/beta/jig_update_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="get /v1/deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">list</a>() -> <a href="./src/together/types/beta/jig_list_response.py">JigListResponse</a></code>
- <code title="post /v1/deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">deploy</a>(\*\*<a href="src/together/types/beta/jig_deploy_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="delete /v1/deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">destroy</a>(id) -> object</code>
- <code title="get /v1/deployments/{id}/revisions">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">list_revisions</a>(id, \*\*<a href="src/together/types/beta/jig_list_revisions_params.py">params</a>) -> <a href="./src/together/types/beta/deployment_revision_event_list.py">DeploymentRevisionEventList</a></code>
- <code title="get /v1/deployments/{id}/logs">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve_logs</a>(id, \*\*<a href="src/together/types/beta/jig_retrieve_logs_params.py">params</a>) -> <a href="./src/together/types/beta/deployment_logs.py">DeploymentLogs</a></code>
- <code title="get /v1/deployments/{id}/revisions/{revisionIdentifier}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve_revision</a>(revision_identifier, \*, id) -> <a href="./src/together/types/beta/deployment_revision.py">DeploymentRevision</a></code>
- <code title="post /v1/deployments/{id}/rollback">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">rollback</a>(id, \*\*<a href="src/together/types/beta/jig_rollback_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>

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

- <code title="get /v1/queue/status">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">retrieve</a>(\*\*<a href="src/together/types/beta/jig/queue_retrieve_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_retrieve_response.py">QueueRetrieveResponse</a></code>
- <code title="post /v1/queue/cancel">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">cancel</a>(\*\*<a href="src/together/types/beta/jig/queue_cancel_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_cancel_response.py">QueueCancelResponse</a></code>
- <code title="post /v1/queue/clear">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">clear</a>(\*\*<a href="src/together/types/beta/jig/queue_clear_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_clear_response.py">QueueClearResponse</a></code>
- <code title="get /v1/queue/metrics">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">metrics</a>(\*\*<a href="src/together/types/beta/jig/queue_metrics_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_metrics_response.py">QueueMetricsResponse</a></code>
- <code title="post /v1/queue/submit">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">submit</a>(\*\*<a href="src/together/types/beta/jig/queue_submit_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_submit_response.py">QueueSubmitResponse</a></code>

### Volumes

Types:

```python
from together.types.beta.jig import S3Origin, Volume, VolumeOrigin, VolumeStatus, VolumeListResponse
```

Methods:

- <code title="post /v1/deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">create</a>(\*\*<a href="src/together/types/beta/jig/volume_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /v1/deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">retrieve</a>(id, \*\*<a href="src/together/types/beta/jig/volume_retrieve_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="patch /v1/deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/volume_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /v1/deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">list</a>() -> <a href="./src/together/types/beta/jig/volume_list_response.py">VolumeListResponse</a></code>
- <code title="delete /v1/deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">delete</a>(id) -> object</code>

### Secrets

Types:

```python
from together.types.beta.jig import Secret, SecretListResponse
```

Methods:

- <code title="post /v1/deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">create</a>(\*\*<a href="src/together/types/beta/jig/secret_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /v1/deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">retrieve</a>(id) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="patch /v1/deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/secret_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /v1/deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">list</a>() -> <a href="./src/together/types/beta/jig/secret_list_response.py">SecretListResponse</a></code>
- <code title="delete /v1/deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">delete</a>(id) -> object</code>

# Organization

## Usage

Types:

```python
from together.types.organization import BillingUsageLineItem, BillingUsageReport, BillingUsageWindow
```

### Costs

Methods:

- <code title="get /v1/billing/usage">client.organization.usage.costs.<a href="./src/together/resources/organization/usage/costs.py">list</a>(\*\*<a href="src/together/types/organization/usage/cost_list_params.py">params</a>) -> <a href="./src/together/types/organization/billing_usage_window.py">SyncCursorPagination[BillingUsageWindow]</a></code>

# PostTraining

## Sessions

Types:

```python
from together.types.post_training import (
    InferenceCheckpoint,
    LoraConfig,
    ModelRegistryArtifact,
    Session,
    SessionError,
    SessionErrorCode,
    SessionMetadata,
    SessionStatus,
    SessionsListResponse,
    TrainingCheckpoint,
    WandbMetadata,
)
```

Methods:

- <code title="post /v1/rl/training-sessions">client.post_training.sessions.<a href="./src/together/resources/post_training/sessions.py">create</a>(\*\*<a href="src/together/types/post_training/session_create_params.py">params</a>) -> <a href="./src/together/types/post_training/session.py">Session</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}">client.post_training.sessions.<a href="./src/together/resources/post_training/sessions.py">retrieve</a>(session_id) -> <a href="./src/together/types/post_training/session.py">Session</a></code>
- <code title="patch /v1/rl/training-sessions/{session_id}">client.post_training.sessions.<a href="./src/together/resources/post_training/sessions.py">update</a>(session_id, \*\*<a href="src/together/types/post_training/session_update_params.py">params</a>) -> <a href="./src/together/types/post_training/session.py">Session</a></code>
- <code title="get /v1/rl/training-sessions">client.post_training.sessions.<a href="./src/together/resources/post_training/sessions.py">list</a>(\*\*<a href="src/together/types/post_training/session_list_params.py">params</a>) -> <a href="./src/together/types/post_training/sessions_list_response.py">SessionsListResponse</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/stop">client.post_training.sessions.<a href="./src/together/resources/post_training/sessions.py">stop</a>(session_id) -> <a href="./src/together/types/post_training/session.py">Session</a></code>

## Operations

Types:

```python
from together.types.post_training import (
    AdamParams,
    CispoLossParams,
    CrossEntropyLossParams,
    CustomForwardBackwardOperation,
    CustomForwardBackwardResult,
    DType,
    DppoLossParams,
    DroLossParams,
    EncodedTextChunk,
    ForwardBackwardOperation,
    ForwardBackwardResult,
    GrpoLossAggregationType,
    GrpoLossParams,
    GrpoLossRatioType,
    InferenceCheckpointOperation,
    InferenceCheckpointResult,
    LossConfig,
    LossFnOutput,
    LossType,
    ModelInput,
    ModelInputChunk,
    MuonParams,
    OperationError,
    OperationErrorCode,
    OperationStatus,
    OptimStepOperation,
    OptimStepResult,
    PolicyVersionSegment,
    PpoLossParams,
    PromptTopLogprobs,
    SampleOperation,
    SampleResult,
    SampledSequence,
    SamplingParams,
    StopReason,
    TensorData,
    TrainingCheckpointOperation,
    TrainingCheckpointResult,
    WeightSyncType,
    WeightsSyncOperation,
    WeightsSyncResult,
)
```

Methods:

- <code title="post /v1/rl/training-sessions/{session_id}/operations/inference-checkpoint">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">create_inference_checkpoint</a>(session_id) -> <a href="./src/together/types/post_training/inference_checkpoint_operation.py">InferenceCheckpointOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/training-checkpoint">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">create_training_checkpoint</a>(session_id) -> <a href="./src/together/types/post_training/training_checkpoint_operation.py">TrainingCheckpointOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/custom-forward-backward">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">custom_forward_backward</a>(session_id, \*\*<a href="src/together/types/post_training/operation_custom_forward_backward_params.py">params</a>) -> <a href="./src/together/types/post_training/custom_forward_backward_operation.py">CustomForwardBackwardOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/forward-backward">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">forward_backward</a>(session_id, \*\*<a href="src/together/types/post_training/operation_forward_backward_params.py">params</a>) -> <a href="./src/together/types/post_training/forward_backward_operation.py">ForwardBackwardOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/optim-step">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">optim_step</a>(session_id, \*\*<a href="src/together/types/post_training/operation_optim_step_params.py">params</a>) -> <a href="./src/together/types/post_training/optim_step_operation.py">OptimStepOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/custom-forward-backward/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_custom_forward_backward</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/custom_forward_backward_operation.py">CustomForwardBackwardOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/forward-backward/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_forward_backward</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/forward_backward_operation.py">ForwardBackwardOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/inference-checkpoint/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_inference_checkpoint</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/inference_checkpoint_operation.py">InferenceCheckpointOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/optim-step/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_optim_step</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/optim_step_operation.py">OptimStepOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/sample/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_sample</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/sample_operation.py">SampleOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/training-checkpoint/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_training_checkpoint</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/training_checkpoint_operation.py">TrainingCheckpointOperation</a></code>
- <code title="get /v1/rl/training-sessions/{session_id}/operations/weights-sync/{operation_id}">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">retrieve_weights_sync</a>(operation_id, \*, session_id) -> <a href="./src/together/types/post_training/weights_sync_operation.py">WeightsSyncOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/sample">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">sample</a>(session_id, \*\*<a href="src/together/types/post_training/operation_sample_params.py">params</a>) -> <a href="./src/together/types/post_training/sample_operation.py">SampleOperation</a></code>
- <code title="post /v1/rl/training-sessions/{session_id}/operations/weights-sync">client.post_training.operations.<a href="./src/together/resources/post_training/operations.py">weights_sync</a>(session_id, \*\*<a href="src/together/types/post_training/operation_weights_sync_params.py">params</a>) -> <a href="./src/together/types/post_training/weights_sync_operation.py">WeightsSyncOperation</a></code>

## Checkpoints

Types:

```python
from together.types.post_training import (
    Checkpoint,
    CheckpointDownloadResponse,
    CheckpointFile,
    CheckpointType,
    CheckpointVariant,
    CheckpointsListResponse,
)
```

Methods:

- <code title="get /v1/rl/checkpoints/{id}">client.post_training.checkpoints.<a href="./src/together/resources/post_training/checkpoints.py">retrieve</a>(id) -> <a href="./src/together/types/post_training/checkpoint.py">Checkpoint</a></code>
- <code title="get /v1/rl/checkpoints">client.post_training.checkpoints.<a href="./src/together/resources/post_training/checkpoints.py">list</a>(\*\*<a href="src/together/types/post_training/checkpoint_list_params.py">params</a>) -> <a href="./src/together/types/post_training/checkpoints_list_response.py">CheckpointsListResponse</a></code>
- <code title="get /v1/rl/checkpoints/{id}/download">client.post_training.checkpoints.<a href="./src/together/resources/post_training/checkpoints.py">download</a>(id, \*\*<a href="src/together/types/post_training/checkpoint_download_params.py">params</a>) -> <a href="./src/together/types/post_training/checkpoint_download_response.py">CheckpointDownloadResponse</a></code>

## PrepareForFp4Inference

Types:

```python
from together.types.post_training import (
    QuantizationEstimate,
    QuantizationEvent,
    QuantizationJob,
    QuantizationResults,
    ShapingJobStatus,
    ShapingJobType,
    PrepareForFp4InferenceListResponse,
    PrepareForFp4InferenceListEventsResponse,
)
```

Methods:

- <code title="post /v1/shaping/prepare-for-fp4-inference">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">create</a>(\*\*<a href="src/together/types/post_training/prepare_for_fp4_inference_create_params.py">params</a>) -> <a href="./src/together/types/post_training/quantization_job.py">QuantizationJob</a></code>
- <code title="get /v1/shaping/{id}">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">retrieve</a>(id) -> <a href="./src/together/types/post_training/quantization_job.py">QuantizationJob</a></code>
- <code title="get /v1/shaping">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">list</a>() -> <a href="./src/together/types/post_training/prepare_for_fp4_inference_list_response.py">PrepareForFp4InferenceListResponse</a></code>
- <code title="post /v1/shaping/{id}/cancel">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">cancel</a>(id) -> <a href="./src/together/types/post_training/quantization_job.py">QuantizationJob</a></code>
- <code title="post /v1/shaping/prepare-for-fp4-inference/estimate">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">estimate_cost</a>(\*\*<a href="src/together/types/post_training/prepare_for_fp4_inference_estimate_cost_params.py">params</a>) -> <a href="./src/together/types/post_training/quantization_estimate.py">QuantizationEstimate</a></code>
- <code title="get /v1/shaping/{id}/events">client.post_training.prepare_for_fp4_inference.<a href="./src/together/resources/post_training/prepare_for_fp4_inference.py">list_events</a>(id) -> <a href="./src/together/types/post_training/prepare_for_fp4_inference_list_events_response.py">PrepareForFp4InferenceListEventsResponse</a></code>

## ModelResources

Types:

```python
from together.types.post_training import (
    AdamConfig,
    ModelResources,
    ModelResourcesError,
    ModelResourcesErrorCode,
    ModelResourcesEstimateCostResponse,
    ModelResourcesListResponse,
    ModelResourcesStatus,
    MuonConfig,
    MuonScalingStrategy,
    OptimizerConfig,
)
```

Methods:

- <code title="post /v1/rl/model-resources">client.post_training.model_resources.<a href="./src/together/resources/post_training/model_resources.py">create</a>(\*\*<a href="src/together/types/post_training/model_resource_create_params.py">params</a>) -> <a href="./src/together/types/post_training/model_resources.py">ModelResources</a></code>
- <code title="get /v1/rl/model-resources/{model_resources_id}">client.post_training.model_resources.<a href="./src/together/resources/post_training/model_resources.py">retrieve</a>(model_resources_id) -> <a href="./src/together/types/post_training/model_resources.py">ModelResources</a></code>
- <code title="get /v1/rl/model-resources">client.post_training.model_resources.<a href="./src/together/resources/post_training/model_resources.py">list</a>(\*\*<a href="src/together/types/post_training/model_resource_list_params.py">params</a>) -> <a href="./src/together/types/post_training/model_resources_list_response.py">ModelResourcesListResponse</a></code>
- <code title="post /v1/rl/model-resources/estimate-cost">client.post_training.model_resources.<a href="./src/together/resources/post_training/model_resources.py">estimate_cost</a>(\*\*<a href="src/together/types/post_training/model_resource_estimate_cost_params.py">params</a>) -> <a href="./src/together/types/post_training/model_resources_estimate_cost_response.py">ModelResourcesEstimateCostResponse</a></code>
- <code title="post /v1/rl/model-resources/{model_resources_id}/stop">client.post_training.model_resources.<a href="./src/together/resources/post_training/model_resources.py">stop</a>(model_resources_id, \*\*<a href="src/together/types/post_training/model_resource_stop_params.py">params</a>) -> <a href="./src/together/types/post_training/model_resources.py">ModelResources</a></code>

## SupportedModels

Types:

```python
from together.types.post_training import RlSupportedModel, RlSupportedModels
```

Methods:

- <code title="get /v1/rl/supported-models">client.post_training.supported_models.<a href="./src/together/resources/post_training/supported_models.py">get</a>() -> <a href="./src/together/types/post_training/rl_supported_models.py">RlSupportedModels</a></code>

# Clusters

Types:

```python
from together.types import (
    Cluster,
    ClusterListResponse,
    ClusterDeleteResponse,
    ClusterListRegionsResponse,
)
```

Methods:

- <code title="post /v1/compute/clusters">client.clusters.<a href="./src/together/resources/clusters/clusters.py">create</a>(\*\*<a href="src/together/types/cluster_create_params.py">params</a>) -> <a href="./src/together/types/cluster.py">Cluster</a></code>
- <code title="get /v1/compute/clusters/{cluster_id}">client.clusters.<a href="./src/together/resources/clusters/clusters.py">retrieve</a>(cluster_id) -> <a href="./src/together/types/cluster.py">Cluster</a></code>
- <code title="put /v1/compute/clusters/{cluster_id}">client.clusters.<a href="./src/together/resources/clusters/clusters.py">update</a>(cluster_id, \*\*<a href="src/together/types/cluster_update_params.py">params</a>) -> <a href="./src/together/types/cluster.py">Cluster</a></code>
- <code title="get /v1/compute/clusters">client.clusters.<a href="./src/together/resources/clusters/clusters.py">list</a>(\*\*<a href="src/together/types/cluster_list_params.py">params</a>) -> <a href="./src/together/types/cluster_list_response.py">ClusterListResponse</a></code>
- <code title="delete /v1/compute/clusters/{cluster_id}">client.clusters.<a href="./src/together/resources/clusters/clusters.py">delete</a>(cluster_id) -> <a href="./src/together/types/cluster_delete_response.py">ClusterDeleteResponse</a></code>
- <code title="get /v1/compute/regions">client.clusters.<a href="./src/together/resources/clusters/clusters.py">list_regions</a>() -> <a href="./src/together/types/cluster_list_regions_response.py">ClusterListRegionsResponse</a></code>

## Remediations

Types:

```python
from together.types.clusters import Remediation, RemediationListResponse
```

Methods:

- <code title="post /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">create</a>(instance_id, \*, cluster_id, \*\*<a href="src/together/types/clusters/remediation_create_params.py">params</a>) -> <a href="./src/together/types/clusters/remediation.py">Remediation</a></code>
- <code title="get /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">retrieve</a>(remediation_id, \*, cluster_id, instance_id) -> <a href="./src/together/types/clusters/remediation.py">Remediation</a></code>
- <code title="get /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">list</a>(instance_id, \*, cluster_id, \*\*<a href="src/together/types/clusters/remediation_list_params.py">params</a>) -> <a href="./src/together/types/clusters/remediation_list_response.py">RemediationListResponse</a></code>
- <code title="post /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/approve">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">approve</a>(remediation_id, \*, cluster_id, instance_id, \*\*<a href="src/together/types/clusters/remediation_approve_params.py">params</a>) -> <a href="./src/together/types/clusters/remediation.py">Remediation</a></code>
- <code title="post /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/cancel">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">cancel</a>(remediation_id, \*, cluster_id, instance_id) -> <a href="./src/together/types/clusters/remediation.py">Remediation</a></code>
- <code title="post /v1/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/reject">client.clusters.remediations.<a href="./src/together/resources/clusters/remediations.py">reject</a>(remediation_id, \*, cluster_id, instance_id, \*\*<a href="src/together/types/clusters/remediation_reject_params.py">params</a>) -> <a href="./src/together/types/clusters/remediation.py">Remediation</a></code>

## Storage

Types:

```python
from together.types.clusters import ClusterStorage, StorageListResponse, StorageDeleteResponse
```

Methods:

- <code title="post /v1/compute/clusters/storage/volumes">client.clusters.storage.<a href="./src/together/resources/clusters/storage.py">create</a>(\*\*<a href="src/together/types/clusters/storage_create_params.py">params</a>) -> <a href="./src/together/types/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /v1/compute/clusters/storage/volumes/{volume_id}">client.clusters.storage.<a href="./src/together/resources/clusters/storage.py">retrieve</a>(volume_id) -> <a href="./src/together/types/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="put /v1/compute/clusters/storage/volumes">client.clusters.storage.<a href="./src/together/resources/clusters/storage.py">update</a>(\*\*<a href="src/together/types/clusters/storage_update_params.py">params</a>) -> <a href="./src/together/types/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /v1/compute/clusters/storage/volumes">client.clusters.storage.<a href="./src/together/resources/clusters/storage.py">list</a>(\*\*<a href="src/together/types/clusters/storage_list_params.py">params</a>) -> <a href="./src/together/types/clusters/storage_list_response.py">StorageListResponse</a></code>
- <code title="delete /v1/compute/clusters/storage/volumes/{volume_id}">client.clusters.storage.<a href="./src/together/resources/clusters/storage.py">delete</a>(volume_id) -> <a href="./src/together/types/clusters/storage_delete_response.py">StorageDeleteResponse</a></code>

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

- <code title="post /v1/chat/completions">client.chat.completions.<a href="./src/together/resources/chat/completions.py">create</a>(\*\*<a href="src/together/types/chat/completion_create_params.py">params</a>) -> <a href="./src/together/types/chat/chat_completion.py">ChatCompletion</a></code>

# Completions

Types:

```python
from together.types import Completion, CompletionChunk, LogProbs, ToolChoice, Tools
```

Methods:

- <code title="post /v1/completions">client.completions.<a href="./src/together/resources/completions.py">create</a>(\*\*<a href="src/together/types/completion_create_params.py">params</a>) -> <a href="./src/together/types/completion.py">Completion</a></code>

# Embeddings

Types:

```python
from together.types import Embedding
```

Methods:

- <code title="post /v1/embeddings">client.embeddings.<a href="./src/together/resources/embeddings.py">create</a>(\*\*<a href="src/together/types/embedding_create_params.py">params</a>) -> <a href="./src/together/types/embedding.py">Embedding</a></code>

# Files

Types:

```python
from together.types import FileList, FilePurpose, FileResponse, FileType, FileDeleteResponse
```

Methods:

- <code title="get /v1/files/{id}">client.files.<a href="./src/together/resources/files.py">retrieve</a>(id) -> <a href="./src/together/types/file_response.py">FileResponse</a></code>
- <code title="get /v1/files">client.files.<a href="./src/together/resources/files.py">list</a>() -> <a href="./src/together/types/file_list.py">FileList</a></code>
- <code title="delete /v1/files/{id}">client.files.<a href="./src/together/resources/files.py">delete</a>(id) -> <a href="./src/together/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /v1/files/{id}/content">client.files.<a href="./src/together/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>

# FineTuning

Types:

```python
from together.types import (
    FineTunePreviewResponse,
    FineTunePreviewRow,
    FineTuneTokenizedDatasetRetrieveResponse,
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

- <code title="get /v1/fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">retrieve</a>(id) -> <a href="./src/together/types/finetune_response.py">FinetuneResponse</a></code>
- <code title="get /v1/fine-tunes">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list</a>() -> <a href="./src/together/types/fine_tuning_list_response.py">FineTuningListResponse</a></code>
- <code title="delete /v1/fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">delete</a>(id) -> <a href="./src/together/types/fine_tuning_delete_response.py">FineTuningDeleteResponse</a></code>
- <code title="post /v1/fine-tunes/{id}/cancel">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">cancel</a>(id) -> <a href="./src/together/types/fine_tuning_cancel_response.py">FineTuningCancelResponse</a></code>
- <code title="get /v1/finetune/download">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">content</a>(\*\*<a href="src/together/types/fine_tuning_content_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="post /v1/fine-tunes/estimate-price">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">estimate_price</a>(\*\*<a href="src/together/types/fine_tuning_estimate_price_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_estimate_price_response.py">FineTuningEstimatePriceResponse</a></code>
- <code title="get /v1/fine-tunes/{id}/checkpoints">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_checkpoints</a>(id) -> <a href="./src/together/types/fine_tuning_list_checkpoints_response.py">FineTuningListCheckpointsResponse</a></code>
- <code title="get /v1/fine-tunes/{id}/events">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_events</a>(id) -> <a href="./src/together/types/fine_tuning_list_events_response.py">FineTuningListEventsResponse</a></code>
- <code title="get /v1/fine-tunes/{id}/metrics">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_metrics</a>(id, \*\*<a href="src/together/types/fine_tuning_list_metrics_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_list_metrics_response.py">FineTuningListMetricsResponse</a></code>
- <code title="get /v1/fine-tunes/models/limits">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">model_limits</a>(\*\*<a href="src/together/types/fine_tuning_model_limits_params.py">params</a>) -> <a href="./src/together/types/finetune_model_limits.py">FinetuneModelLimits</a></code>
- <code title="post /v1/fine-tunes/preview">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">preview</a>(\*\*<a href="src/together/types/fine_tuning_preview_params.py">params</a>) -> <a href="./src/together/types/fine_tune_preview_response.py">FineTunePreviewResponse</a></code>
- <code title="get /v1/fine-tunes/{id}/download-tokenized-dataset">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">retrieve_tokenized_dataset</a>(id) -> <a href="./src/together/types/fine_tune_tokenized_dataset_retrieve_response.py">FineTuneTokenizedDatasetRetrieveResponse</a></code>

# Images

Types:

```python
from together.types import ImageDataB64, ImageDataURL, ImageFile
```

Methods:

- <code title="post /v1/images/generations">client.images.<a href="./src/together/resources/images.py">generate</a>(\*\*<a href="src/together/types/image_generate_params.py">params</a>) -> <a href="./src/together/types/image_file.py">ImageFile</a></code>

# Videos

Types:

```python
from together.types import VideoJob
```

Methods:

- <code title="post /v2/videos">client.videos.<a href="./src/together/resources/videos.py">create</a>(\*\*<a href="src/together/types/video_create_params.py">params</a>) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>
- <code title="get /v2/videos/{id}">client.videos.<a href="./src/together/resources/videos.py">retrieve</a>(id) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>

# Audio

Types:

```python
from together.types import AudioFile, AudioSpeechStreamChunk
```

## Speech

Methods:

- <code title="post /v1/audio/speech">client.audio.speech.<a href="./src/together/resources/audio/speech.py">create</a>(\*\*<a href="src/together/types/audio/speech_create_params.py">params</a>) -> BinaryAPIResponse</code>

## Voices

Types:

```python
from together.types.audio import VoiceListResponse
```

Methods:

- <code title="get /v1/voices">client.audio.voices.<a href="./src/together/resources/audio/voices.py">list</a>() -> <a href="./src/together/types/audio/voice_list_response.py">VoiceListResponse</a></code>

## Transcriptions

Types:

```python
from together.types.audio import TranscriptionCreateResponse
```

Methods:

- <code title="post /v1/audio/transcriptions">client.audio.transcriptions.<a href="./src/together/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/together/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/together/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>

## Translations

Types:

```python
from together.types.audio import TranslationCreateResponse
```

Methods:

- <code title="post /v1/audio/translations">client.audio.translations.<a href="./src/together/resources/audio/translations.py">create</a>(\*\*<a href="src/together/types/audio/translation_create_params.py">params</a>) -> <a href="./src/together/types/audio/translation_create_response.py">TranslationCreateResponse</a></code>

# Models

Types:

```python
from together.types import (
    Model,
    ModelDtypeCount,
    ModelParameters,
    ModelWeights,
    SupportedModel,
    SupportedModelDeploymentProfile,
    SupportedModelPerformanceBenchmarks,
    ModelDeleteResponse,
    ModelListFilesResponse,
    ModelListRevisionsResponse,
)
```

Methods:

- <code title="post /v2/projects/{projectId}/models">client.models.<a href="./src/together/resources/models/models.py">create</a>(\*, project_id, \*\*<a href="src/together/types/model_create_params.py">params</a>) -> <a href="./src/together/types/model.py">Model</a></code>
- <code title="get /v2/projects/{projectId}/models/{id}">client.models.<a href="./src/together/resources/models/models.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/model.py">Model</a></code>
- <code title="patch /v2/projects/{projectId}/models/{id}">client.models.<a href="./src/together/resources/models/models.py">update</a>(id, \*, project_id, \*\*<a href="src/together/types/model_update_params.py">params</a>) -> <a href="./src/together/types/model.py">Model</a></code>
- <code title="get /v2/projects/{projectId}/models">client.models.<a href="./src/together/resources/models/models.py">list</a>(\*, project_id, \*\*<a href="src/together/types/model_list_params.py">params</a>) -> <a href="./src/together/types/model.py">SyncCursorPagination[Model]</a></code>
- <code title="delete /v2/projects/{projectId}/models/{id}">client.models.<a href="./src/together/resources/models/models.py">delete</a>(id, \*, project_id) -> <a href="./src/together/types/model_delete_response.py">ModelDeleteResponse</a></code>
- <code title="get /v2/projects/{projectId}/models/{id}/files">client.models.<a href="./src/together/resources/models/models.py">list_files</a>(id, \*, project_id, \*\*<a href="src/together/types/model_list_files_params.py">params</a>) -> <a href="./src/together/types/model_list_files_response.py">ModelListFilesResponse</a></code>
- <code title="get /v2/organizations/{organizationId}/models">client.models.<a href="./src/together/resources/models/models.py">list_org_scoped</a>(organization_id, \*\*<a href="src/together/types/model_list_org_scoped_params.py">params</a>) -> <a href="./src/together/types/model.py">SyncCursorPagination[Model]</a></code>
- <code title="get /v2/projects/{projectId}/models/{id}/revisions">client.models.<a href="./src/together/resources/models/models.py">list_revisions</a>(id, \*, project_id) -> <a href="./src/together/types/model_list_revisions_response.py">ModelListRevisionsResponse</a></code>
- <code title="get /v2/supported-models">client.models.<a href="./src/together/resources/models/models.py">list_supported</a>(\*\*<a href="src/together/types/model_list_supported_params.py">params</a>) -> <a href="./src/together/types/supported_model.py">SyncCursorPagination[SupportedModel]</a></code>
- <code title="get /v2/supported-models/{id}">client.models.<a href="./src/together/resources/models/models.py">retrieve_supported</a>(id) -> <a href="./src/together/types/supported_model.py">SupportedModel</a></code>

## RemoteUploads

Types:

```python
from together.types.models import (
    RemoteUploadCreateResponse,
    RemoteUploadRetrieveResponse,
    RemoteUploadListResponse,
    RemoteUploadEventsResponse,
)
```

Methods:

- <code title="post /v2/projects/{projectId}/models/uploads">client.models.remote_uploads.<a href="./src/together/resources/models/remote_uploads.py">create</a>(\*, project_id, \*\*<a href="src/together/types/models/remote_upload_create_params.py">params</a>) -> <a href="./src/together/types/models/remote_upload_create_response.py">RemoteUploadCreateResponse</a></code>
- <code title="get /v2/projects/{projectId}/models/uploads/{id}">client.models.remote_uploads.<a href="./src/together/resources/models/remote_uploads.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/models/remote_upload_retrieve_response.py">RemoteUploadRetrieveResponse</a></code>
- <code title="get /v2/projects/{projectId}/models/uploads">client.models.remote_uploads.<a href="./src/together/resources/models/remote_uploads.py">list</a>(\*, project_id, \*\*<a href="src/together/types/models/remote_upload_list_params.py">params</a>) -> <a href="./src/together/types/models/remote_upload_list_response.py">SyncCursorPagination[RemoteUploadListResponse]</a></code>
- <code title="get /v2/projects/{projectId}/models/uploads/{id}/events">client.models.remote_uploads.<a href="./src/together/resources/models/remote_uploads.py">events</a>(id, \*, project_id, \*\*<a href="src/together/types/models/remote_upload_events_params.py">params</a>) -> <a href="./src/together/types/models/remote_upload_events_response.py">RemoteUploadEventsResponse</a></code>

## Configs

Types:

```python
from together.types.models import Certification, Config, Selector
```

Methods:

- <code title="get /v2/projects/{projectId}/configs/{id}">client.models.configs.<a href="./src/together/resources/models/configs.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/models/config.py">Config</a></code>
- <code title="get /v2/projects/{projectId}/configs">client.models.configs.<a href="./src/together/resources/models/configs.py">list</a>(\*, project_id, \*\*<a href="src/together/types/models/config_list_params.py">params</a>) -> <a href="./src/together/types/models/config.py">SyncCursorPagination[Config]</a></code>

# Endpoints

Types:

```python
from together.types import (
    AbMember,
    DeploymentAutoscaling,
    DeploymentMetrics,
    DeploymentPlacementConfig,
    DeploymentStatus,
    Endpoint,
    EndpointDeployment,
    EndpointDeploymentSummary,
    EndpointTrafficSplitEntry,
    ErrorMetrics,
    LatencyMetrics,
    MetricsTimeRange,
    RequestMetrics,
    ResourceUtilization,
    RuntimeInfo,
    ScalingMetric,
    ScalingPolicy,
    ScalingRules,
    ShadowAdaptiveKeyBasedSampling,
    ShadowAdaptiveKeyBasedSamplingResponse,
    ShadowAdaptiveUniformSampling,
    ShadowAdaptiveUniformSamplingResponse,
    ShadowEndpointSource,
    ShadowEndpointSourceResponse,
    ShadowKeyBasedSampling,
    ShadowKeyBasedSamplingResponse,
    ShadowSource,
    ShadowSourceResponse,
    ShadowUniformSampling,
    ShadowUniformSamplingResponse,
    ThroughputMetrics,
    TimeSeriesDataPoint,
    TokenMetrics,
    EndpointDeleteResponse,
    EndpointAnalyticsResponse,
    EndpointListEventsResponse,
)
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">create</a>(\*, project_id, \*\*<a href="src/together/types/endpoint_create_params.py">params</a>) -> <a href="./src/together/types/endpoint.py">Endpoint</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{id}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/endpoint.py">Endpoint</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{id}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">update</a>(id, \*, project_id, \*\*<a href="src/together/types/endpoint_update_params.py">params</a>) -> <a href="./src/together/types/endpoint.py">Endpoint</a></code>
- <code title="get /v2/projects/{projectId}/endpoints">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list</a>(\*, project_id, \*\*<a href="src/together/types/endpoint_list_params.py">params</a>) -> <a href="./src/together/types/endpoint.py">SyncCursorPagination[Endpoint]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{id}">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">delete</a>(id, \*, project_id, \*\*<a href="src/together/types/endpoint_delete_params.py">params</a>) -> <a href="./src/together/types/endpoint_delete_response.py">EndpointDeleteResponse</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{id}/analytics">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">analytics</a>(id, \*, project_id, \*\*<a href="src/together/types/endpoint_analytics_params.py">params</a>) -> <a href="./src/together/types/endpoint_analytics_response.py">EndpointAnalyticsResponse</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{id}/events">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list_events</a>(id, \*, project_id, \*\*<a href="src/together/types/endpoint_list_events_params.py">params</a>) -> <a href="./src/together/types/endpoint_list_events_response.py">SyncCursorPagination[EndpointListEventsResponse]</a></code>
- <code title="get /v2/organizations/{organizationId}/endpoints">client.endpoints.<a href="./src/together/resources/endpoints/endpoints.py">list_org_scoped</a>(organization_id, \*\*<a href="src/together/types/endpoint_list_org_scoped_params.py">params</a>) -> <a href="./src/together/types/endpoint.py">SyncCursorPagination[Endpoint]</a></code>

## PlacementProfiles

Types:

```python
from together.types.endpoints import PlacementProfile
```

Methods:

- <code title="get /v2/projects/{projectId}/placement-profiles/{id}">client.endpoints.placement_profiles.<a href="./src/together/resources/endpoints/placement_profiles.py">retrieve</a>(id, \*, project_id) -> <a href="./src/together/types/endpoints/placement_profile.py">PlacementProfile</a></code>
- <code title="get /v2/projects/{projectId}/placement-profiles">client.endpoints.placement_profiles.<a href="./src/together/resources/endpoints/placement_profiles.py">list</a>(\*, project_id, \*\*<a href="src/together/types/endpoints/placement_profile_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/placement_profile.py">SyncCursorPagination[PlacementProfile]</a></code>

## AbExperiments

Types:

```python
from together.types.endpoints import AbExperiment, AbExperimentDeleteResponse
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/abExperiments">client.endpoints.ab_experiments.<a href="./src/together/resources/endpoints/ab_experiments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/ab_experiment_create_params.py">params</a>) -> <a href="./src/together/types/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.endpoints.ab_experiments.<a href="./src/together/resources/endpoints/ab_experiments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.endpoints.ab_experiments.<a href="./src/together/resources/endpoints/ab_experiments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/ab_experiment_update_params.py">params</a>) -> <a href="./src/together/types/endpoints/ab_experiment.py">AbExperiment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/abExperiments">client.endpoints.ab_experiments.<a href="./src/together/resources/endpoints/ab_experiments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/ab_experiment_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/ab_experiment.py">SyncCursorPagination[AbExperiment]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/abExperiments/{id}">client.endpoints.ab_experiments.<a href="./src/together/resources/endpoints/ab_experiments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/ab_experiment_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/ab_experiment_delete_response.py">AbExperimentDeleteResponse</a></code>

## ShadowExperiments

Types:

```python
from together.types.endpoints import ShadowExperiment, ShadowExperimentDeleteResponse
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments">client.endpoints.shadow_experiments.<a href="./src/together/resources/endpoints/shadow_experiments/shadow_experiments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/shadow_experiment_create_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.endpoints.shadow_experiments.<a href="./src/together/resources/endpoints/shadow_experiments/shadow_experiments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.endpoints.shadow_experiments.<a href="./src/together/resources/endpoints/shadow_experiments/shadow_experiments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/shadow_experiment_update_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiment.py">ShadowExperiment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments">client.endpoints.shadow_experiments.<a href="./src/together/resources/endpoints/shadow_experiments/shadow_experiments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/shadow_experiment_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiment.py">SyncCursorPagination[ShadowExperiment]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{id}">client.endpoints.shadow_experiments.<a href="./src/together/resources/endpoints/shadow_experiments/shadow_experiments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/shadow_experiment_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiment_delete_response.py">ShadowExperimentDeleteResponse</a></code>

### Targets

Types:

```python
from together.types.endpoints.shadow_experiments import ShadowExperimentTarget, TargetDeleteResponse
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets">client.endpoints.shadow_experiments.targets.<a href="./src/together/resources/endpoints/shadow_experiments/targets.py">create</a>(\*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/endpoints/shadow_experiments/target_create_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.endpoints.shadow_experiments.targets.<a href="./src/together/resources/endpoints/shadow_experiments/targets.py">retrieve</a>(id, \*, project_id, endpoint_id, experiment_id) -> <a href="./src/together/types/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.endpoints.shadow_experiments.targets.<a href="./src/together/resources/endpoints/shadow_experiments/targets.py">update</a>(id, \*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/endpoints/shadow_experiments/target_update_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiments/shadow_experiment_target.py">ShadowExperimentTarget</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets">client.endpoints.shadow_experiments.targets.<a href="./src/together/resources/endpoints/shadow_experiments/targets.py">list</a>(endpoint_id, experiment_id, \*, project_id, \*\*<a href="src/together/types/endpoints/shadow_experiments/target_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiments/shadow_experiment_target.py">SyncCursorPagination[ShadowExperimentTarget]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/shadowExperiments/{experimentId}/targets/{id}">client.endpoints.shadow_experiments.targets.<a href="./src/together/resources/endpoints/shadow_experiments/targets.py">delete</a>(id, \*, project_id, endpoint_id, experiment_id, \*\*<a href="src/together/types/endpoints/shadow_experiments/target_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/shadow_experiments/target_delete_response.py">TargetDeleteResponse</a></code>

## Rollouts

Types:

```python
from together.types.endpoints import (
    BlueGreenConfig,
    CanaryConfig,
    MetricResult,
    MetricRule,
    PauseInfo,
    RegressionCheck,
    RollingConfig,
    Rollout,
    RolloutCondition,
    RolloutDefaultsPreview,
    RolloutStatus,
    RolloutStep,
    RolloutStepStatus,
    ThresholdCheck,
    RolloutDeleteResponse,
)
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/rollout_create_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/rollouts">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/rollout_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">SyncCursorPagination[Rollout]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/rollout_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout_delete_response.py">RolloutDeleteResponse</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}/cancel">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">cancel</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/rollout_cancel_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}/pause">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">pause</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/rollout_pause_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/preview-defaults">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">preview_defaults</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/rollout_preview_defaults_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout_defaults_preview.py">RolloutDefaultsPreview</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}/promote">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">promote</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/rollout_promote_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}/resume">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">resume</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/rollout_resume_params.py">params</a>) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>
- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/rollouts/{id}/start">client.endpoints.rollouts.<a href="./src/together/resources/endpoints/rollouts.py">start</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/endpoints/rollout.py">Rollout</a></code>

## Hardware

Types:

```python
from together.types.endpoints import InferenceInstanceType, HardwareListResponse
```

Methods:

- <code title="get /v2/public/inference-instance-types/{id}">client.endpoints.hardware.<a href="./src/together/resources/endpoints/hardware.py">retrieve</a>(id) -> <a href="./src/together/types/endpoints/inference_instance_type.py">InferenceInstanceType</a></code>
- <code title="get /v2/public/inference-instance-types">client.endpoints.hardware.<a href="./src/together/resources/endpoints/hardware.py">list</a>() -> <a href="./src/together/types/endpoints/hardware_list_response.py">HardwareListResponse</a></code>

## Adapters

Types:

```python
from together.types.endpoints import (
    DeploymentAdapterStatus,
    AdapterCreateResponse,
    AdapterRetrieveResponse,
    AdapterUpdateResponse,
    AdapterListResponse,
    AdapterDeleteResponse,
)
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">create</a>(\*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/endpoints/adapter_create_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_create_response.py">AdapterCreateResponse</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">retrieve</a>(id, \*, project_id, endpoint_id, deployment_id) -> <a href="./src/together/types/endpoints/adapter_retrieve_response.py">AdapterRetrieveResponse</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">update</a>(id, \*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/endpoints/adapter_update_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_update_response.py">AdapterUpdateResponse</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">list</a>(endpoint_id, deployment_id, \*, project_id, \*\*<a href="src/together/types/endpoints/adapter_list_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_list_response.py">SyncCursorPagination[AdapterListResponse]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{deploymentId}/adapters/{id}">client.endpoints.adapters.<a href="./src/together/resources/endpoints/adapters.py">delete</a>(id, \*, project_id, endpoint_id, deployment_id, \*\*<a href="src/together/types/endpoints/adapter_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/adapter_delete_response.py">AdapterDeleteResponse</a></code>

## Deployments

Types:

```python
from together.types.endpoints import DeploymentDeleteResponse
```

Methods:

- <code title="post /v2/projects/{projectId}/endpoints/{endpointId}/deployments">client.endpoints.deployments.<a href="./src/together/resources/endpoints/deployments.py">create</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/deployment_create_params.py">params</a>) -> <a href="./src/together/types/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.endpoints.deployments.<a href="./src/together/resources/endpoints/deployments.py">retrieve</a>(id, \*, project_id, endpoint_id) -> <a href="./src/together/types/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="patch /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.endpoints.deployments.<a href="./src/together/resources/endpoints/deployments.py">update</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/deployment_update_params.py">params</a>) -> <a href="./src/together/types/endpoint_deployment.py">EndpointDeployment</a></code>
- <code title="get /v2/projects/{projectId}/endpoints/{endpointId}/deployments">client.endpoints.deployments.<a href="./src/together/resources/endpoints/deployments.py">list</a>(endpoint_id, \*, project_id, \*\*<a href="src/together/types/endpoints/deployment_list_params.py">params</a>) -> <a href="./src/together/types/endpoint_deployment.py">SyncCursorPagination[EndpointDeployment]</a></code>
- <code title="delete /v2/projects/{projectId}/endpoints/{endpointId}/deployments/{id}">client.endpoints.deployments.<a href="./src/together/resources/endpoints/deployments.py">delete</a>(id, \*, project_id, endpoint_id, \*\*<a href="src/together/types/endpoints/deployment_delete_params.py">params</a>) -> <a href="./src/together/types/endpoints/deployment_delete_response.py">DeploymentDeleteResponse</a></code>

# Projects

Types:

```python
from together.types import Project
```

Methods:

- <code title="get /v1/projects">client.projects.<a href="./src/together/resources/projects.py">list</a>(\*\*<a href="src/together/types/project_list_params.py">params</a>) -> <a href="./src/together/types/project.py">SyncCursorPagination[Project]</a></code>

# Rerank

Types:

```python
from together.types import RerankCreateResponse
```

Methods:

- <code title="post /v1/rerank">client.rerank.<a href="./src/together/resources/rerank.py">create</a>(\*\*<a href="src/together/types/rerank_create_params.py">params</a>) -> <a href="./src/together/types/rerank_create_response.py">RerankCreateResponse</a></code>

# Batches

Types:

```python
from together.types import BatchJob, BatchCreateResponse, BatchListResponse
```

Methods:

- <code title="post /v1/batches">client.batches.<a href="./src/together/resources/batches.py">create</a>(\*\*<a href="src/together/types/batch_create_params.py">params</a>) -> <a href="./src/together/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /v1/batches/{id}">client.batches.<a href="./src/together/resources/batches.py">retrieve</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>
- <code title="get /v1/batches">client.batches.<a href="./src/together/resources/batches.py">list</a>() -> <a href="./src/together/types/batch_list_response.py">BatchListResponse</a></code>
- <code title="post /v1/batches/{id}/cancel">client.batches.<a href="./src/together/resources/batches.py">cancel</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>

# Evals

Types:

```python
from together.types import EvaluationJob, EvalCreateResponse, EvalListResponse, EvalStatusResponse
```

Methods:

- <code title="post /v1/evaluation">client.evals.<a href="./src/together/resources/evals.py">create</a>(\*\*<a href="src/together/types/eval_create_params.py">params</a>) -> <a href="./src/together/types/eval_create_response.py">EvalCreateResponse</a></code>
- <code title="get /v1/evaluation/{id}">client.evals.<a href="./src/together/resources/evals.py">retrieve</a>(id) -> <a href="./src/together/types/evaluation_job.py">EvaluationJob</a></code>
- <code title="get /v1/evaluation">client.evals.<a href="./src/together/resources/evals.py">list</a>(\*\*<a href="src/together/types/eval_list_params.py">params</a>) -> <a href="./src/together/types/eval_list_response.py">EvalListResponse</a></code>
- <code title="get /v1/evaluation/{id}/status">client.evals.<a href="./src/together/resources/evals.py">status</a>(id) -> <a href="./src/together/types/eval_status_response.py">EvalStatusResponse</a></code>
