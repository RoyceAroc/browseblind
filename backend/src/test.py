from llms.gemini import run_gemini
import PIL.Image
import PIL.ImageDraw
import re

user_prompt = "menu icon"
prompt = f"""
Return a bounding box where users asks "{user_prompt}". 
\n [ymin, xmin, ymax, xmax].
"""
image = PIL.Image.open("tab.png")
response = run_gemini(image, prompt)
image_width, image_height = image.size


s = response
match = re.search(r"\[(.*?)\]", s)

if match:
    bounding_box = [int(x) for x in match.group(1).split(",")]
    ymin, xmin, ymax, xmax = bounding_box
    ymin = ymin * image_height / 1000
    xmin = xmin * image_width / 1000
    ymax = ymax * image_height / 1000
    xmax = xmax * image_width / 1000

    print(f"Bounding box in original image dimensions: {ymin, xmin, ymax, xmax}")
    draw = PIL.ImageDraw.Draw(image)
    draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)
    image.show()

else:
    print("Error: Could not find a bounding box in the response.")
    print("Please check the model response format.")
