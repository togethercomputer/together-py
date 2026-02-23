########################################################
# Together Endpoints are used to deploy models on Together's infrastructure.
#
# Read more here: https://docs.together.ai/docs/dedicated-inference
########################################################

from together import Together
client = Together()

########################################################
# Create a new endpoint
#
# This creates an endpoint that inference can be ran against. The hardware available is determined by the model.
# First we query the available hardware for the model and use the first _available_ option.
available_hardware = client.endpoints.list_hardware(model="mistralai/Mixtral-8x7B-Instruct-v0.1").data
hardware = next((h.id for h in available_hardware if getattr(h.availability, "status", None) == "available"), "")

endpoint = client.endpoints.create(
    display_name="Mixtral-8x7B-Instruct-v0.1",
    autoscaling={
        "min_replicas": 1,
        "max_replicas": 8,
    },
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    hardware=hardware,

    # Automatically start the endpoint on creation
    state="STARTED",
)
print(f"Endpoint created: {endpoint.id}")

########################################################
# Stop the endpoint
#
endpoint = client.endpoints.update(endpoint.id, state="STOPPED")
print(f"Endpoint stopping...")

########################################################
# Start the endpoint
#
endpoint = client.endpoints.update(endpoint.id, state="STARTED")
print(f"Endpoint starting...")

########################################################
# Delete the endpoint
#
client.endpoints.delete(endpoint.id)
print(f"Endpoint deleted...")

########################################################
# List all endpoints
#
endpoints = client.endpoints.list()
print(f"Total endpoints: {len(endpoints.data)}")