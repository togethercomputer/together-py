from together import Together

USE_HELPERS = True

client = Together()
model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

if USE_HELPERS:
    print("Using helpers")

    with client.chat.completions.stream(
        messages=[
            {
                "role": "user",
                "content": "write me a poem about javascript",
            }
        ],
        model=model,
        logprobs=1,
    ) as stream_manager:
        for event in stream_manager:
            print(f"[{event.type}]: {event.model_dump_json(indent=2)}")

        final_completion = stream_manager.get_final_completion()
        print(f"[final_completion] {final_completion.model_dump_json(indent=2)}")

else:
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model=model,
        stream=True,
    )
    for chunk in completion:
        choice = chunk.choices[0]
        if choice.delta.content:
            print(f"Content Delta: {choice.delta.content}")
