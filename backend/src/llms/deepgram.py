import requests
import random
from configs import DEEPGRAM_TOKEN

url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
headers = {
    "Authorization": f"Token {random.choice(DEEPGRAM_TOKEN)}",
    "Content-Type": "text/plain",
}


def make_audio(data):
    response = requests.post(url, headers=headers, data=data)

    with open("audio.mp3", "wb") as f:
        f.write(response.content)

    return "audio.mp3"
