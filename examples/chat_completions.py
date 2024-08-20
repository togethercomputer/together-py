from together import Together

client = Together()

with client.chat.completions.stream(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    logprobs=1,
) as stream:
    # Events are defined in src/together/lib/streaming/chat/_events.py
    for event in stream:
        if event.type == "chunk":
            print(f"Chunk: id={event.chunk.id}", flush=True)
        elif event.type == "content.delta":
            print(event.delta, flush=True)
        elif event.type == "content.done":
            print(f"Content done: {event.content}", flush=True)
        elif event.type == "logprobs.delta":
            print(f"Logprobs: delta={event.delta}", flush=True)
        elif event.type == "logprobs.content.done":
            print(f"Logprobs done", flush=True)
        elif event.type == "tool_calls.function.arguments.delta":
            print(
                f"Tool call arguments delta: {event.name}, {event.index}, {event.arguments}, {event.arguments_delta}",
                flush=True,
            )
        elif event.type == "tool_calls.function.arguments.done":
            print(f"Tool call arguments done: {event.name}, {event.index}, {event.arguments}", flush=True)
