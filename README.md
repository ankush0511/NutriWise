# NutriWise

NutriWise is a comprehensive recipe and meal planning application that combines nutrition analysis, recipe generation, and meal planning capabilities with advanced features like voice input and image recognition.

## 🌟 Features

### 1. Recipe Generation
- Voice-to-Recipe conversion
- Image-to-Recipe conversion
- AI-powered recipe generation
- Interactive Streamlit interface

### 2. Meal Planning
- Daily meal planning
- Weekly meal planning
- Nutritional tracking
- Customizable meal schedules

### 3. Risk Analysis
- Ingredient risk assessment
- Automated text extraction
- Ingredient compatibility checking
- Smart ingredient agent

### 4. User Profiles
- Personalized user experiences
- Profile management through Streamlit
- Dietary preferences tracking
- Nutrition goals monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Streamlit
- Required Python packages (listed in requirements.txt)

### Installation
1. Clone the repository
```bash
git clone [repository-url]
cd nutriwise
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## 📂 Project Structure

```
nutriwise/
├── app.py                          # Main application file
├── csv_to_sql.py                   # Database utilities
├── Nutrients.csv                   # Nutrition data
├── nutrients.py                    # Nutrition processing
├── user_profile_streamlit.py       # User profile interface
├── user_profiles.json              # User data storage
├── assets/                         # Media assets
├── meal_planner/                   # Meal planning modules
│   ├── meal_planner_daily.py
│   └── meal_planner_weekly.py
├── recipe_generators/              # Recipe generation modules
│   ├── image_generation.py
│   ├── image_to_recipe.py
│   ├── recipe_generator.py
│   ├── recipe_generator_streamlit.py
│   └── voice_to_recipe.py
└── risk_analyzer/                  # Risk analysis modules
    ├── ingredient_agent.py
    ├── ingredient_risk_analyzer_streamlit.py
    └── text_extraction.py
```

## 🎯 Usage

1. Start the main application:
```bash
streamlit run app.py
```

2. For specific features:
- Recipe Generation: `streamlit run recipe_generators/recipe_generator_streamlit.py`
- Risk Analysis: `streamlit run risk_analyzer/ingredient_risk_analyzer_streamlit.py`
- User Profiles: `streamlit run user_profile_streamlit.py`

## 🛠️ Technologies Used

- Python
- Streamlit
- Machine Learning
- Image Processing
- Voice Recognition
- Natural Language Processing

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- [Your Name]
- [Other Contributors]

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📮 Contact

Project Link: [repository-url]