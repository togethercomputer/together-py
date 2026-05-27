from together import Together

client = Together()

# Request the list of all models and print them
models = client.models.list()
for model in models:
    print(model)
