import time

from together import Together

client = Together()

file_id = "file-bf72b951-fa1a-41af-a152-fe385dca0201"
fine_tune_model = client.fine_tuning.create(model="meta-llama/Meta-Llama-3-8B", training_file=file_id)
print(fine_tune_model)

fine_tune_id = fine_tune_model.id

# wait for completion
while True:
    fine_tune_status = client.fine_tuning.retrieve(fine_tune_id)
    if fine_tune_status.status == "completed":
        print("completed")
        break
    else:
        print(f"waiting for completion, status: {fine_tune_status.status}")
        time.sleep(1)

# list the model events
model_events = client.fine_tuning.list_events(fine_tune_id)
for e in model_events.data:
    print(e)

# download the model
downloaded = client.fine_tuning.content(ft_id=fine_tune_id)
print(downloaded)
