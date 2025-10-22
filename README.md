
# 🥗 NutriWise – AI-Powered Nutrition & Recipe Assistant
**NutriWise** is a cutting-edge **AI-powered nutrition and recipe management platform** that helps users eat smarter and live healthier.
It combines **recipe generation**, **meal planning**, **ingredient risk analysis**, and **nutritional tracking** with **voice and image intelligence** — all powered by advanced AI models like **Gemini**, **Groq**, and **Agno**.

Whether you're managing dietary restrictions or simply exploring healthy meal ideas, NutriWise adapts to your needs through real-time AI assistance.

---

## 🌟 Key Features

### 🧠 1. AI Recipe Generation

* **Text-to-Recipe:** Enter ingredients or descriptions and get structured recipes (name, ingredients, steps, tips).
* **Voice-to-Recipe:** Record your voice — AI transcribes and generates recipes (hands-free cooking!).
* **Image-to-Recipe:** Upload a dish photo or ingredient image; AI suggests possible recipes.
* **AI Image Generation:** Generate appealing food visuals with Gemini’s image model.
* **Interactive UI:** Streamlit-based with recipe download/export support.

### 🥗 2. Personalized Meal Planning

* **Daily / Weekly Plans:** Automatically create balanced meal schedules.
* **Macro Tracking:** Breaks down calories, proteins, carbs, and fats per meal.
* **Smart Nutrient Allocation:** Distributes macros (e.g., 25% breakfast, 30% lunch/dinner, 15% snacks).
* **Profile-Aware:** Aligns with your age, gender, activity level, allergies, and diet type.

### ⚕️ 3. Ingredient Risk & Allergy Analysis

* **OCR-Powered Text Extraction:** Detects ingredients from food labels or packaging.
* **Allergen Risk Scoring:** Assigns 0–1 safety scores for personalized allergen detection.
* **Safer Alternatives:** Suggests allergen-free product substitutes with reasoning.
* **Agentic Pipeline:** Multi-agent workflow (Extraction → Risk Evaluation → Alternative Generation).

### 👤 4. Smart User Profiles

* Save and load custom profiles (age, gender, diet type, allergy list).
* Automatically calculate daily nutrition goals (based on RDA values).
* Store profiles securely in `user_profiles.json` with editable Streamlit UI.

### 🧩 5. Extra Tools

* **Nutrition Lookup Agent:** Retrieves real-time nutrient data for any food item.
* **Voice & Image Integrations:** Use your microphone or camera for direct inputs.
* **Offline Export:** Download generated recipes or meal plans in Markdown or text.

---

## 🚀 Quick Start Guide

### ✅ Prerequisites

* **Python:** 3.10+ (tested on 3.12)
* **APIs:**

  * Google AI (Gemini)
  * Groq (LLaMA-3)
  * Exa (optional for web search)
* **Optional:** Microphone & webcam for live input.

### 🧰 Installation

```bash
git clone https://github.com/ankush0511/NutriWise.git
cd NutriWise
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🔐 Environment Setup

Create a `.env` file in the root folder:

```bash
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key
EXA_API_KEY=your_exa_key   # Optional for web search
```

*(For Streamlit Cloud, use “Secrets” for secure key storage.)*

### ▶️ Run the App

```bash
streamlit run app.py
```

Access it locally at **[http://localhost:8501](http://localhost:8501)**

---

## 📂 Project Structure

```
NutriWise/
├── app.py                               # Main Streamlit dashboard
├── patch_sqlite.py                      # SQLite compatibility patch
├── requirements.txt                     # Dependencies
├── .env.example                         # Example environment file
├── user_profiles.json                   # Sample user profile data
├── assets/
│   └── logo.png                         # App logo
├── meal_planner/
│   └── meal_planner_daily.py            # AI meal planner
├── recipe_generators/
│   ├── recipe_generator.py              # Text-to-recipe (Gemini)
│   ├── voice_to_recipe.py               # Voice-based recipe gen
│   ├── image_to_recipe.py               # Image-based recipe gen
│   ├── image_generation.py              # AI food image generation
│   └── recipe_generator_streamlit.py    # Streamlit recipe UI
├── risk_analyzer/
│   ├── ingredient_agent.py              # Multi-agent risk analyzer
│   ├── text_extraction.py               # OCR for ingredients
│   └── ingredient_risk_analyzer_streamlit.py
└── user_profile_streamlit.py            # User profile management
```

---

## 🧑‍🍳 How to Use

| Feature          | Command                                                             |
| ---------------- | ------------------------------------------------------------------- |
| Full App         | `streamlit run app.py`                                              |
| Recipe Generator | `streamlit run recipe_generators/recipe_generator_streamlit.py`     |
| Risk Analyzer    | `streamlit run risk_analyzer/ingredient_risk_analyzer_streamlit.py` |
| Profile Manager  | `streamlit run user_profile_streamlit.py`                           |

### Example Workflow

1. Create a profile (e.g., vegetarian, 2200 kcal/day).
2. Generate a meal plan — balanced macros auto-assigned per meal.
3. Upload a product photo → extract ingredients → check allergen risk.
4. Generate recipes via text, voice, or image.
5. Export results and reuse for tracking or planning.

---
## ScreenShot
<img width="1848" height="1070" alt="image" src="https://github.com/user-attachments/assets/5ad304c3-de3f-4ce2-9b6b-09d543c3dd01" />

<img width="1852" height="1040" alt="image" src="https://github.com/user-attachments/assets/ce6e8456-ffaa-4587-b3ca-ed5110aab296" />

<img width="1853" height="1028" alt="image" src="https://github.com/user-attachments/assets/f106bc56-32eb-4676-b84f-98c6c96d5750" />

<img width="1846" height="1035" alt="image" src="https://github.com/user-attachments/assets/a2dead7c-79eb-4658-9085-a35a6e5a971d" />

---

## 🧠 Tech Stack

| Category             | Technologies                                           |
| -------------------- | ------------------------------------------------------ |
| **Frontend**         | Streamlit                                              |
| **AI/LLMs**          | Google Gemini (text/vision), Groq LLaMA 3, Agno Agents |
| **Image Processing** | PIL, OCR                                               |
| **Audio Processing** | SpeechRecognition, streamlit_mic_recorder              |
| **Data Handling**    | Pandas, Pydantic, SQLite                               |
| **Web Search**       | DuckDuckGo, Exa, Baidu                                 |
| **Utilities**        | dotenv, json, base64, LangChain                        |

---

## 🔒 Security & Privacy

* API keys stored securely in environment variables
* User data kept locally; no personal data sent externally
* Allergen and risk analysis prioritize safety and transparency

---

## 🧩 Future Roadmap

* [ ] Weekly & Monthly meal planning
* [ ] Barcode & Nutrition Label scanning
* [ ] Recipe sharing community
* [ ] Fitness tracker integration
* [ ] Mobile app version

---

## 🧑‍💻 Contributors

* **Ankush Chaudhary** – Lead Developer & AI Engineer
  🔗 [GitHub Profile](https://github.com/ankush0511)

Contributions welcome!
Fork → Branch → Commit → PR 🎯

---

## 📝 License

This project is licensed under the **MIT License**.

---

**💡 Made with ❤️ using AI, Streamlit & real food inspiration.**

> “Eat smart, live better — with NutriWise.”
