from agno.agent import Agent
import json
from agno.tools.exa import ExaTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
import os
from dotenv import load_dotenv
load_dotenv() 
import streamlit as st
google_api_key=st.secrets["GOOGLE_API_KEY"]
exa_api_key=st.secrets["EXA_API_KEY"]

# google_api_key=os.getenv("GOOGLE_API_KEY")
# exa_api_key=os.getenv("EXA_API_KEY")

nutrient_agent = Agent(
    model=Gemini(api_key=google_api_key),
    tool_call_limit=[DuckDuckGoTools(), BaiduSearchTools(), ExaTools(api_key=exa_api_key), ReasoningTools(add_instructions=True)],
    instructions="""
    You are a Nutrition Data Specialist AI with access to a comprehensive web search abilities.

    YOUR TASK:
    1. Accept one or multiple food items or ingredients (comma-separated or list).
    2. For each item, search the web for an **exact match**. 
    3. If no exact match exists, find the **closest generic or common match** (e.g., "boiled potato" → "potato, boiled").
    4. Return the **complete nutritional profile** for each item as a structured dictionary.

    OUTPUT FORMAT:
    Return results in a JSON/dictionary format, one entry per food item:
    {
        "<food item>": {
            'Calories ': <value> (kcal),
            'Carbohydrates': <value> (g),
            'Protein': <value> (g),
            'Fats': <value> (g),
            'Free Sugar': <value> (g),
            'Fibre': <value> (g),
            'Sodium': <value> (mg),
            'Calcium': <value> (mg),
            'Iron': <value> (mg),
            'Vitamin C': <value (mg)>
        },
        ...
    }
    IMPORTANT GUIDELINES:
    1. Handle **case-insensitive searches** (e.g., "Apple", "apple", "APPLE").
    2. Always return **all numerical values exactly as they appear in the database**.
    3. If an item is not found, clearly inform the user and suggest **similar alternatives** if available.
    4. Maintain a **consistent structured output** for all queries.
    5. Prioritize **generic/common forms** over brand-specific variants unless specified.
    6. Support **batch queries** for multiple items at once.
    7. Ensure output is **parsable as JSON/dictionary** for downstream processing.
    """,
    debug_mode=False,
    description="You are a Nutrition Data Specialist AI that provides accurate nutritional information from a comprehensive web search abilities.",
)
