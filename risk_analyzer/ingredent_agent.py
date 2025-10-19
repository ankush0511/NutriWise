import streamlit as st
from risk_analyzer.text_extraction import configure_gemini, extract_text_from_image
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from user_profile_streamlit import render_profile_section, get_user_allergies
# st.title("Food Allergy Agent")

# Render profile section and get user allergies
# user_allergies = render_profile_section()

load_dotenv()
configure_gemini()

# ---------------- Ingredient Extraction ----------------
class IngredientList(BaseModel):
    ingredients: List[str] = Field(description="List of extracted ingredients from the image")

text_extractor = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"),temperature=0.1),

    description="Ingredient extraction agent",
    instructions=(
        "You will receive a string from user containing food package ingredients.\n"
        "Your task is to:\n"
        "1. Carefully analyze the given food package list and extract ALL ingredients clearly listed\n"
        "2. Pay special attention to allergen warnings marked with 'Contains:', 'May contain:', 'Manufactured in a facility that processes:', or similar statements\n"
        "3. Extract ingredients exactly as written - do not skip, merge, abbreviate or modify any ingredient names\n"
        "4. Include any sub-ingredients listed in parentheses\n"
        "5. Preserve the order of ingredients as they appear in the original text\n"
        "Return the result as a clean, structured JSON with:\n"
        "- 'ingredients': Array of all ingredients in order\n"
        "- 'contains': Array of explicit allergen warnings\n"
        "Be thorough and precise - the output will be used for allergy analysis." 
    ),
    debug_mode=True,
)

# resp = text_extractor.run("the image path is: assests/roasted.png").content
# print("Extracted Ingredients:", resp)

# ---------------- Risk Scoring ----------------
# allergy_list = user_allergies if user_allergies else ["nuts", "gluten", "milk"]

# risk_scoring = Agent(
#     model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"),temperature=0.1),
#     description="Food allergy risk scoring agent",
#     instructions=(
#         f"You are a food risk scoring agent. The user has the following known allergies: {allergy_list}. "
#         "Your task is to: \n"
#         "1. Compare the extracted ingredients with the allergy list.\n"
#         "2. If any allergens are found, mark them clearly.\n"
#         "3. Provide a 'Risk Score' between 0 and 1 (0 = no risk, 1 = severe risk).\n"
#         "4. Return output in JSON format with the keys: `allergens_found`, `risk_score`, `explanation`."
#     ),
# )
        # f"You are a food risk scoring agent. The user has the following known allergies: {allergy_list}. "


risk_scoring = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"), temperature=0.1),
    description="Food allergy risk scoring agent",
    instructions=(
        "you will get the ingredent and the user allergy list,it conain the user allergy item"
        "Your task is to:\n"
        "1. Compare ONLY the provided extracted ingredients given by the user against the allergy list.\n"
        "2. If an allergen is **explicitly present** in the ingredients, mark it in `allergens_found`.\n"
        "3. Do NOT assume or infer allergens (e.g., do not add 'nuts' unless clearly listed).\n"
        "4. Provide a `risk_score` between 0 and 1:\n"
        "   - 0 = no allergens found\n"
        "   - 0.1–0.4 = low risk (trace or minor presence)\n"
        "   - 0.5–0.7 = moderate risk (1–2 allergens present)\n"
        "   - 0.8–1.0 = high/severe risk (multiple allergens found)\n"
        "5. Explain briefly why the allergens were flagged.\n"
        "6. Return output strictly in JSON format with keys: `allergens_found`, `risk_score`, `explanation`."
    ),
)

# resp = risk_scoring.run(resp).content
# print("Risk Scoring:", resp)

# ---------------- Risk-Free Alternatives ----------------
risk_alternate = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"),temperature=0.1),
    description="You are an expert nutritionist and food safety specialist with deep knowledge of allergen-free products, ingredient substitutions, and healthy alternatives.",
    instructions=(
      """
        CORE REQUIREMENTS:
        - Every suggested product MUST be completely FREE of ALL detected allergens
        - ZERO tolerance for ANY form, derivative, or cross-contamination of user's allergens
        - Suggest EXACTLY 3-5 alternative products (never less than 3)
        - Focus on widely available, real products from recognizable brands
        - Prioritize healthier options with cleaner ingredient lists

        INPUT FORMAT:
        You will receive a JSON object containing:
        - `allergens_found`: Array of detected allergens
        - `risk_score`: Numerical risk assessment (0-1)
        - `explanation`: Context about why the original product is risky

        ALLERGEN SAFETY RULES:
        1. Check for ALL forms of allergens (e.g., if "milk" is detected, avoid: casein, whey, lactose, dairy, etc.)
        2. Consider cross-contamination warnings ("may contain" statements)
        3. Research ingredient derivatives and hidden sources
        4. When in doubt, exclude the product

        SUGGESTION CRITERIA:
        - Product must serve similar purpose/category as original
        - Should be nutritionally comparable or superior
        - Readily available in most grocery stores or online
        - Include both mainstream and specialty/health-focused brands
        - Consider different price points (budget to premium)
        OUTPUT FORMAT:
        """
        "Each suggestion should include: product name, reason, and allergen profile. "
        "Return strictly in JSON format with key: `alternative_suggestions`."
        
    ),
)

# resp = risk_alternate.run(resp).content
# print("Risk Scoring alternative:", resp)

        # "Every suggested product MUST be free of ALL user allergens\n"
        # "You will receive a JSON object that contains `allergens_found` and `risk_score`. "
        # "Suggest at least 3 alternative food products that avoid the allergens found. "
        # "Do NOT suggest products containing ANY form of the user's allergens\n"