from together import Together

client = Together()

print("Listing all files")

# Retrieve a file
fileData = client.files.upload(file="examples/coqa.jsonl")

print(fileData)
