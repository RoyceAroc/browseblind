from groq import Groq

client = Groq(
    api_key="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",
)


def run_groq(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content
