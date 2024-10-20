import random
import google.generativeai as genai
from configs import GEMINI_API_KEY

genai.configure(api_key=random.choice(GEMINI_API_KEY))
model = genai.GenerativeModel("gemini-1.5-flash")


def run_gemini(image, prompt):
    response = model.generate_content([prompt, image])
    s = response.text
    return s
