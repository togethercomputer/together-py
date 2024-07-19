from together import Together

client = Together()

embeddings = client.embeddings.create(
    input="A cat",
    model="togethercomputer/m2-bert-80M-8k-retrieval",
)

if embeddings.data and embeddings.data[0]:
    print(embeddings.data[0].embedding)
