from together import Together

client = Together()

print("Listing all files")

# Print all files
files = client.files.list()
for file in files.data:
    print(file)

# Retrieve a file
if files.data and files.data[0]:
    print("Retrieving a file")

    file_id = files.data[0].id

    fileData = client.files.retrieve(file_id)

    print(fileData)
