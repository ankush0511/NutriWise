import time
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
import os
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()

class Nutrients(BaseModel):
    calories: float = Field(..., description="Calories in kcal")
    carbohydrates: float = Field(..., description="Carbs in grams")
    fats: float = Field(..., description="Fats in grams")
    proteins: float = Field(..., description="Proteins in grams")

class Ingredient(BaseModel):
    name: str = Field(..., description="Ingredient name")
    quantity: float = Field(..., description="Quantity of ingredient")
    unit: str = Field(..., description="Unit of measurement (g, ml, tbsp, etc.)")

class Recipe(BaseModel):
    recipe_name: str = Field(..., description="Name of the recipe")
    ingredients: List[Ingredient] = Field(..., description="Ingredients with quantities and units")
    nutrients: Nutrients = Field(..., description="Macronutrient breakdown of this recipe")

class MealPlan(BaseModel):
    recipes: List[Recipe] = Field(..., description="A list of recipes for the meal plan")
    total_nutrients: Nutrients = Field(..., description="Total nutrients across all recipes in the plan")


def get_nutrients_value(meal_type):
    if meal_type == 'breakfast':
        return 0.25
    elif meal_type == 'lunch':
        return 0.30
    elif meal_type == 'dinner':
        return 0.30
    else:
        return 0.15


def generate_meal(cal,pro,fa,carb,meal_type,recipe_list,allerges):
    perccent=get_nutrients_value(meal_type)
    cal*=perccent
    pro*=perccent
    fa*=perccent
    carb*=perccent
    
    agent = Agent(
    description="An AI assistant that generates personalized meal plans based on user nutrient targets and allergies.",
    model=Groq(temperature=0.7 ,api_key=os.getenv('GROQ_API_KEY')),
    instructions=f"""
    You are a nutrition planning assistant.

    Create a {meal_type} meal plan matching these exact targets (±5% tolerance):
    - Calories: {cal} kcal
    - Carbs: {carb}g
    - Fats: {fa}g
    - Protein: {pro}g

    EXCLUDE: {allerges}
    EXCLUDE: {recipe_list}

    For each recipe provide:
    1. Recipe name
    2. Ingredients (quantities in grams/ml)
    3. Macros (cal, carbs, fats, protein)

    Requirements:
    - Use common, simple ingredients only
    - Must avoid all allergens completely
    - Explain any deviations from targets

        """,
    output_schema=MealPlan
    )

    resp=agent.run("what is the meal plan for me?").content
    return resp

# if __name__ == "__main__":
#     # Example usage
#     allerges=['fish','milk']
#     recipe_list=[]
#     resp = generate_meal(2400,56,73,400,"breakfast",recipe_list,allerges)

#     print("This is the meal plain for the morning i.e breakfast shift")
#     tp = resp.recipes
#     for recipe in tp:
#         print("Recipe Name:", recipe.recipe_name)
#         recipe_list.append(recipe.recipe_name)
#         print("Ingredients:", recipe.ingredients)
#         for i in recipe.ingredients:
#             print(i.name+" "+str(i.quantity)+" "+i.unit)
#         print("Nutrients:", recipe.nutrients)
#         print('='*100)

#     print(resp.total_nutrients)
#     resp = generate_meal(2400,56,73,400,"Lunch",recipe_list,allerges)

#     print("This is the meal plain for the Lunch i.e breakfast shift")
#     tp = resp.recipes
#     for recipe in tp:
#         print("Recipe Name:", recipe.recipe_name)
#         recipe_list.append(recipe.recipe_name)
#         print("Ingredients:", recipe.ingredients)
#         for i in recipe.ingredients:
#             print(i.name+" "+str(i.quantity)+" "+i.unit)
#         print("Nutrients:", recipe.nutrients)
#         print('='*100)

#     print(resp.total_nutrients)
#     resp = generate_meal(2400,56,73,400,"dinner",recipe_list,allerges)

#     print("This is the meal plain for the dinner i.e breakfast shift")
#     tp = resp.recipes
#     for recipe in tp:
#         print("Recipe Name:", recipe.recipe_name)
#         recipe_list.append(recipe.recipe_name)
#         print("Ingredients:", recipe.ingredients)
#         for i in recipe.ingredients:
#             print(i.name+" "+str(i.quantity)+" "+i.unit)
#         print("Nutrients:", recipe.nutrients)
#         print('='*100)

#     print(resp.total_nutrients)
#     resp = generate_meal(2400,56,73,400,"snacks",recipe_list,allerges)

#     print("This is the meal plain for the Snacks i.e breakfast shift")
#     tp = resp.recipes
#     for recipe in tp:
#         print("Recipe Name:", recipe.recipe_name)
#         recipe_list.append(recipe.recipe_name)
#         print("Ingredients:", recipe.ingredients)
#         for i in recipe.ingredients:
#             print(i.name+" "+str(i.quantity)+" "+i.unit)
#         print("Nutrients:", recipe.nutrients)
#         print('='*100)

#     print(resp.total_nutrients)
