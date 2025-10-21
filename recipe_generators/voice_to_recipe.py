import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
import streamlit as st
google_api_key=st.secrets["GOOGLE_API_KEY"]

client = genai.Client(api_key=google_api_key)


def voice_to_recipe(filename):
      myfile = client.files.upload(file=filename)

      response = client.models.generate_content(
      model="gemini-2.5-flash", contents=["Return output with:\n"
                  "1. Recipe Name\n"
                  "2. Required Ingredients (with quantities if possible)\n"
                  "3. Step-by-Step Cooking Instructions\n"
                  "4. Optional Tips for taste/health.", myfile]
      )

      # print(response.text)
      return response.text
