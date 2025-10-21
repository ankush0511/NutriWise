import streamlit as st
from risk_analyzer.text_extraction import configure_gemini, extract_text_from_image
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
groq_api_key=st.secrets["GROQ_API_KEY"]
google_api_key=st.secrets["GOOGLE_API_KEY"]


load_dotenv()
configure_gemini()

# ---------------- Ingredient Extraction ----------------
class IngredientList(BaseModel):
    ingredients: List[str] = Field(description="List of extracted ingredients from the image")

text_extractor = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=groq_api_key,temperature=0.1),

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
    debug_mode=False,
)




risk_scoring = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=google_api_key, temperature=0.1),
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

# ---------------- Risk-Free Alternatives ----------------
risk_alternate = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=google_api_key,temperature=0.1),
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
