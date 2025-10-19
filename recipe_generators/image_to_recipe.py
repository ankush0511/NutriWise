from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import base64
import os


def encode_image(uploaded_file):
    file_bytes = uploaded_file.read()  # read directly from UploadedFile
    return base64.b64encode(file_bytes).decode("utf-8")


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def pic_to_recipe(base64_image):

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text",
                    "text": "Based on the image you have to Return output with:\n"
                                "1. Recipe Name\n"
                                "2. Required Ingredients (with quantities if possible)\n"
                                "3. Step-by-Step Cooking Instructions\n"
                                "4. Optional Tips for taste/health." },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    # print(chat_completion.choices[0].message.content)
    return (chat_completion.choices[0].message.content)

