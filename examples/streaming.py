from together import Together

client = Together()

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    stream=True,
)
for chunk in stream:
    choice = chunk.choices[0]
    if choice.delta.content:
        print(choice.delta.content, end="", flush=True)
