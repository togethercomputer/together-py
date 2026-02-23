########################################################
# Together Embeddings are used to generate vector embeddings for text input.
#
# This example demonstrates how to generate a single embedding for a given text input.
########################################################
from together import Together
client = Together()

embeddings = client.embeddings.create(
    input="A cat",
    model="togethercomputer/m2-bert-80M-8k-retrieval",
)

if embeddings.data and embeddings.data[0]:
    print(embeddings.data[0].embedding)
