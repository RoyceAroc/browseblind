import google.generativeai as genai

genai.configure(api_key="AIzaSyAg216xspoLnCCe1Xn8vRsGw7xk-A76wd4")
model = genai.GenerativeModel("gemini-1.5-flash")


def run_gemini(image, prompt):
    response = model.generate_content([prompt, image])
    s = response.text
    return s
