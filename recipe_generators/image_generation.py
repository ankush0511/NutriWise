from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
google_api_key=st.secrets["GOOGLE_API_KEY"]

client = genai.Client(api_key=google_api_key)
def recipe_image(contents):

  response = client.models.generate_content(
      model="gemini-2.0-flash-preview-image-generation",
      contents=contents,
      config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
      )
  )
  return response

def show_image(response):
  for part in response.candidates[0].content.parts:
    if part.text is not None:
      print(part.text)
    elif part.inline_data is not None:
      image = Image.open(BytesIO((part.inline_data.data)))
      # image.show()
      return image
      