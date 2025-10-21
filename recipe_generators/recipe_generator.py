from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from recipe_generators.image_generation import recipe_image,show_image
import os
import json
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
api_key = st.secrets["GOOGLE_API_KEY"]
# api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

# ingredients = "how to make aloo paratha?"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "respond only if you recive the query related to ingredents if not simply rely the user to give the ingredents list."
     "dont add redundant content simply start with recipe name"
     "You are a master chef. Generate a structured recipe based on the given ingredients .give in short way in 250 words"
     "Return output with proper title and its content\n"
     "1. Recipe Name\n"
     "2. Required Ingredients\n"
     "3. Step-by-Step Cooking Instructions\n"),
    ("user", "{text_input}")
])

chain = prompt | llm


def get_recipe(resp):
    prompt=f"""
    Extract the only the recipe from the following text,
    return only the recipe name in json format.
    text={resp[:100]}
    """
    resp=llm.invoke(prompt).content
    resp=resp.replace("```json","").replace("```","")

    json_obj=json.loads(resp)
    # print(json_obj['recipe_name'])
    return json_obj['recipe_name']

# img_qury=f"generate the image of {json_obj['recipe_name']}"
# response=recipe_image(img_qury)
# show_image(response)