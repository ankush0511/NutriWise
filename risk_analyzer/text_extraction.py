import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

def configure_gemini():
    """Configure the Gemini API with the API key."""
    try:
        # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]
        if not GOOGLE_API_KEY:
            raise KeyError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=GOOGLE_API_KEY)
    except KeyError as e:
        print(f"Error: {e}")
        exit()

def extract_text_from_image(image_file, prompt):
    """
    Uses Gemini Pro Vision to extract text from an image.

    Args:
        image_file: The uploaded image file (Streamlit file_uploader object).
        prompt (str): The instruction for the model.

    Returns:
        str: The extracted text from the image.
    """
    print("Extracting text from image...")

    try:
        img = Image.open(image_file)
    except Exception as e:
        return f"Error loading image: {e}"

    model = genai.GenerativeModel('gemini-2.5-pro')
    print("Sending request to Gemini API...")

    try:
        response = model.generate_content([prompt, img])
        return response.text
    except ValueError as e:
        return f"Response was blocked. Feedback: {response.prompt_feedback}"
    except Exception as e:
        return f"Error processing image: {e}"

def process_text_input(text_input):
    """
    Process user-provided text input directly.

    Args:
        text_input (str): The text provided by the user.

    Returns:
        str: The processed text (same as input, with basic validation).
    """
    if not text_input or not text_input.strip():
        return "Error: No text provided."
    return text_input.strip()

# if __name__ == "__main__":
    # configure_gemini()
    # # Example usage
    # ans=extract_text_from_image('ingredent.png', "extract the text from the image")
    # print(ans)