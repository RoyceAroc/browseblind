import os
import random
from groq import Groq
from configs import GROQ_API_KEY

client = Groq(
    api_key=random.choice(GROQ_API_KEY),
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


def run_groq_stt(filename):
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3-turbo",
            prompt="User giving instructions",
            response_format="json",
            language="en",
            temperature=0.0,
        )
    return transcription.text
