from dotenv import load_dotenv, dotenv_values

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

import PIL

config = dotenv_values(".env")
MY_SECRET_KEY = config['SECRET_KEY']
GOOGLE_API_KEY = config['GOOGLE_API_KEY']

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key=GOOGLE_API_KEY)

# ------------- Check which models are available -------------
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)


# ------------- TEXT -------------
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("Ok, do you remember my last question? what was it?")
# answer = response.text
# print(answer)


# ------------- IMAGE -------------
model = genai.GenerativeModel('gemini-pro-vision')
img_octo = PIL.Image.open('octo.jpg')
img_shark = PIL.Image.open('shark.jpg')
url_img = "https://inaturalist-open-data.s3.amazonaws.com/photos/261649646/medium.jpg"
json_structure = "{'number of people': ,'time of the day': ,'location', 'animals': ,'background:'}"
dive_text = "הזכרתי כבר פעם כמה אני אוהב את החוף הצפוני באילת? שנירקול זריחה הבוקר, מעל הכלים האמפיביים 19.1.24"
response = model.generate_content([f"I am giving you a text and an image about diving, return a json file in the next format: {json_structure}. if some information is missing type none. the text: {dive_text}", img_shark], stream=True)
# response = model.generate_content(['what animal is in the image?', img_shark], stream=True)
response.resolve()
print(response.text)
