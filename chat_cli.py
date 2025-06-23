"""Simple command line chat interface using OpenAI."""

import openai_config


def main() -> None:
    messages = []
    print("Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user_input})
        response = openai_config.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=openai_config.TOOLS,
        )
        assistant = response.choices[0].message.content
        print("Assistant:", assistant)
        messages.append({"role": "assistant", "content": assistant})


if __name__ == "__main__":
    main()
