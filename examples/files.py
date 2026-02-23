########################################################
# Together Files are used in various features like fine-tuning, evals, and batches.
#
# This example demonstrates how to upload, retrieve, and delete files.
# You can also download the contents of a file and stream it to write to a file.
#
########################################################

from together import Together
client = Together()

########################################################
# List all files currently uploaded
#
files = client.files.list()
print(f"Total files uploaded: {len(files.data)}")


########################################################
# Upload a file
#
# File uploads are idempotent, so you can upload the same file multiple times. It will result in one singular file upload ultimately.
#
uploaded_file = client.files.upload(
    file="examples/coqa-small.jsonl",
    # Other use cases are for features like evals and batches.
    purpose="fine-tune"
)
print("File uploaded successfully")

########################################################
# Retrieve a file
#
fileData = client.files.retrieve(uploaded_file.id)
print(f"File ID: {fileData.id}")

########################################################
# Delete a file
#
client.files.delete(uploaded_file.id)
print("File deleted successfully")

########################################################
# Download contents of the file
#
# Using the with_streaming_response context manager, we can stream the response and write to a file.
with client.files.with_streaming_response.content(uploaded_file.id) as response:
  with open("downloaded_file.jsonl", "wb") as f:
    for chunk in response.iter_bytes():
      f.write(chunk)

