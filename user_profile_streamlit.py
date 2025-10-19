import streamlit as st
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from meal_planner.meal_planner_daily import generate_meal
from nutrients import nutrient_agent
import time
import re
import streamlit as st
import json
import traceback
import time
# Removed circular import - will import dynamically when needed
from risk_analyzer.text_extraction import configure_gemini, extract_text_from_image
import streamlit as st
from recipe_generators.recipe_generator import chain, get_recipe
from recipe_generators.image_generation import recipe_image, show_image
from streamlit_mic_recorder import mic_recorder
from recipe_generators.image_to_recipe import encode_image, pic_to_recipe
from recipe_generators.voice_to_recipe import voice_to_recipe
import tempfile
import wave

# Page configuration
st.set_page_config(
    page_title="🧠 NutriWise - Smart Nutrition Platform",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS with NutriWise Branding
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

.nutriwise-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.nutriwise-logo {
    font-family: 'Poppins', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    color: white;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.nutriwise-tagline {
    font-family: 'Poppins', sans-serif;
    font-size: 1.2rem;
    color: rgba(255,255,255,0.9);
    margin-top: 0.5rem;
    font-weight: 300;
}

.main-header {
    text-align: center;
    color: #667eea;
    font-size: 3.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
    font-family: 'Poppins', sans-serif;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 1.3rem;
    margin-bottom: 3rem;
    font-family: 'Poppins', sans-serif;
}

.input-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    color: white;
    font-family: 'Poppins', sans-serif;
}

.input-card h3 {
    color: white;
    margin-bottom: 1rem;
    font-family: 'Poppins', sans-serif;
}

.recipe-output {
    background-color: #fff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 5px solid #667eea;
    margin: 2rem 0;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    font-family: 'Poppins', sans-serif;
}

.recipe-title {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 1rem;
    font-family: 'Poppins', sans-serif;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 10px;
    color: #667eea;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


class UserProfile(BaseModel):
    name: str
    age: int
    sex: str  # "male" or "female"
    allergies: List[str] = []
    dietary_restrictions: List[str] = []
    severity_level: str = "moderate"  # mild, moderate, severe
    calorie_target: Optional[int] = None
    protein_target: Optional[int] = None
    fat_target: Optional[int] = None
    carb_target: Optional[int] = None

class ProfileManager:
    def __init__(self, profile_file="user_profiles.json"):
        self.profile_file = profile_file

    def save_profile(self, profile: UserProfile):
        profiles = self.load_all_profiles()
        profiles[profile.name] = profile.model_dump()  
        with open(self.profile_file, 'w') as f:
            json.dump(profiles, f, indent=2)



    def load_profile(self, name: str) -> Optional[UserProfile]:
        profiles = self.load_all_profiles()
        if name in profiles:
            return UserProfile(**profiles[name])
        return None
    
    def load_all_profiles(self) -> dict:
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}

def get_recommended_nutrition(age: int, sex: str) -> dict:
    """Calculate recommended daily nutrition based on age and sex"""
    # Calories
    if 2 <= age <= 6:
        calories = 1200 if sex == "male" else 1100
    elif 7 <= age <= 18:
        calories = 1700 if sex == "male" else 1500
    elif 19 <= age <= 60:
        calories = 2400 if sex == "male" else 1800
    else:  # 61+
        calories = 2000 if sex == "male" else 1600
    
    # Protein
    if 1 <= age <= 3:
        protein = 13
    elif 4 <= age <= 8:
        protein = 19
    elif 9 <= age <= 13:
        protein = 34
    elif 14 <= age <= 18:
        protein = 52 if sex == "male" else 46
    else:  # 19+
        protein = 56 if sex == "male" else 46
    
    # Fat
    if 2 <= age <= 6:
        fat = 47 if sex == "male" else 43
    elif 7 <= age <= 18:
        fat = 57 if sex == "male" else 50
    elif 19 <= age <= 60:
        fat = 73 if sex == "male" else 55
    else:  # 61+
        fat = 61 if sex == "male" else 49
    
    # Carbs
    if 2 <= age <= 5:
        carbs = 250
    elif 6 <= age <= 9:
        carbs = 350
    else:  # 10+
        carbs = 400
    
    return {"calories": calories, "protein": protein, "fat": fat, "carbs": carbs}

def render_profile_section():
    st.sidebar.header("👤 User Profile")
    
    profile_manager = ProfileManager()
    
    # Profile selection
    existing_profiles = list(profile_manager.load_all_profiles().keys())
    
    if existing_profiles:
        selected_profile = st.sidebar.selectbox("Select Profile", ["New Profile"] + existing_profiles, key="profile_selector")
        if selected_profile != "New Profile":
            profile = profile_manager.load_profile(selected_profile)
            st.session_state.current_profile = profile
    
    # Profile form
    with st.sidebar.form("profile_form"):
        name = st.text_input("Name", value=getattr(st.session_state.get('current_profile'), 'name', ''))
        
        # Age and Sex
        age = st.number_input(
            "Age", 
            min_value=1, 
            max_value=120, 
            value=getattr(st.session_state.get('current_profile'), 'age', 25)
        )
        
        sex = st.selectbox(
            "Sex",
            ["male", "female"],
            index=0 if getattr(st.session_state.get('current_profile'), 'sex', 'male') == 'male' else 1,
            key="sex_selector"
        )
        
        # Common allergens
        common_allergens = ["nuts", "gluten", "milk", "eggs", "soy", "shellfish", "fish", "sesame",
                            "Corn","Mustard"]
        selected_allergies = st.multiselect(
            "Allergies", 
            common_allergens,
            default=getattr(st.session_state.get('current_profile'), 'allergies', [])
        )
        
        # Custom allergies
        custom_allergies = st.text_input("Additional Allergies (comma-separated)")
        
        # Dietary restrictions
        dietary_options = ["vegetarian", "vegan", "kosher", "halal", "low-sodium", "sugar-free"]
        dietary_restrictions = st.multiselect(
            "Dietary Restrictions",
            dietary_options,
            default=getattr(st.session_state.get('current_profile'), 'dietary_restrictions', [])
        )
        
        # Severity level
        severity = st.selectbox(
            "Allergy Severity",
            ["mild", "moderate", "severe"],
            index=["mild", "moderate", "severe"].index(
                getattr(st.session_state.get('current_profile'), 'severity_level', 'moderate')
            )
        )
        
        # Get recommended values
        recommended = get_recommended_nutrition(age, sex)
        
        st.write(f"**Recommended for {sex}, age {age}:**")
        st.write(f"Calories: {recommended['calories']}, Protein: {recommended['protein']}g")
        st.write(f"Fat: {recommended['fat']}g, Carbs: {recommended['carbs']}g")
        
        # Nutrition targets with recommendations as defaults
        calorie_target = st.number_input(
            "Daily Calorie Target",
            min_value=1000,
            max_value=5000,
            value=getattr(st.session_state.get('current_profile'), 'calorie_target', None) or recommended['calories'],
            step=50
        )
        
        protein_target = st.number_input(
            "Daily Protein Target (g)",
            min_value=10,
            max_value=200,
            value=getattr(st.session_state.get('current_profile'), 'protein_target', None) or recommended['protein'],
            step=5
        )
        
        fat_target = st.number_input(
            "Daily Fat Target (g)",
            min_value=20,
            max_value=150,
            value=getattr(st.session_state.get('current_profile'), 'fat_target', None) or recommended['fat'],
            step=5
        )
        
        carb_target = st.number_input(
            "Daily Carb Target (g)",
            min_value=100,
            max_value=600,
            value=getattr(st.session_state.get('current_profile'), 'carb_target', None) or recommended['carbs'],
            step=10
        )
        
        if st.form_submit_button("Save Profile"):
            if name:
                all_allergies = selected_allergies + [a.strip() for a in custom_allergies.split(',') if a.strip()]
                profile = UserProfile(
                    name=name,
                    age=age,
                    sex=sex,
                    allergies=all_allergies,
                    dietary_restrictions=dietary_restrictions,
                    severity_level=severity,
                    calorie_target=calorie_target,
                    protein_target=protein_target,
                    fat_target=fat_target,
                    carb_target=carb_target
                )
                profile_manager.save_profile(profile)
                st.session_state.current_profile = profile
                st.success(f"Profile saved for {name}!")
    
    # Display current profile
    if hasattr(st.session_state, 'current_profile') and st.session_state.current_profile:
        profile = st.session_state.current_profile
        st.sidebar.success(f"Active: {profile.name}")
        if profile.allergies:
            st.sidebar.write(f"🚫 Allergies: {', '.join(profile.allergies)}")
        if profile.calorie_target:
            st.sidebar.write(f"🎯 Targets: {profile.calorie_target} cal | {profile.protein_target}g protein")
            st.sidebar.write(f"📊 {profile.fat_target}g fat | {profile.carb_target}g carbs")
        return profile.allergies
    
    return []

def get_user_allergies():
    """Get current user's allergies for use in agents"""
    if hasattr(st.session_state, 'current_profile') and st.session_state.current_profile:
        return st.session_state.current_profile.allergies
    return ["nuts", "gluten", "milk"]  # default fallback

def get_user_nutrition_targets():
    """Get current user's nutrition targets"""
    if hasattr(st.session_state, 'current_profile') and st.session_state.current_profile:
        profile = st.session_state.current_profile
        return {
            "calories": profile.calorie_target,
            "protein": profile.protein_target,
            "fat": profile.fat_target,
            "carbs": profile.carb_target
        }
    return {"calories": 2000, "protein": 50, "fat": 65, "carbs": 300}

if __name__ == "__main__":
    # Initialize session state
    if 'current_profile' not in st.session_state:
        st.session_state.current_profile = None
    
    # NutriWise Header
    st.markdown("""
    <div class="nutriwise-header">
        <h1 class="nutriwise-logo">🧠 NutriWise</h1>
        <p class="nutriwise-tagline">Smart Nutrition Decisions for a Healthier You</p>
    </div>
    """, unsafe_allow_html=True)
    
    allergies = render_profile_section()
    # st.write(allergies)
    
    tab1,tab2,tab3,tab4=st.tabs(['🍳 Recipe Generator','⚠️ Ingredient Risk Analyzer','🧪 Ingredient Nutrient Analyzer','🍽️ Meal Planner'])
    with tab1:
        st.header("🍳 Recipe Generator")
        st.markdown('<p class="subtitle">Transform ingredients into delicious recipes using Text, Voice, or Images</p>', unsafe_allow_html=True)

        # Input Methods
        st.markdown("## 📝 Choose Your Input Method")

        subtab1, subtab2, subtab3 = st.tabs(["📝 Text Input", "🎤 Voice Recording", "📸 Image Upload"])

        with subtab1:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("### Type Your Ingredients")
            ingre_list = st.text_area(
                "List your available ingredients:",
                placeholder="e.g., paneer, rice, tomatoes, onions, spices...",
                height=120,
                key="recipe_text_input"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with subtab2:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("### Record Your Voice")
            st.info("🎤 Click to start recording and speak your ingredients clearly")
            audio = mic_recorder(
                start_prompt="🎤 Start Recording", 
                stop_prompt="⏹️ Stop Recording", 
                key='recipe_recorder'
            )
            if audio:
                st.success("✅ Audio recorded successfully!")
            st.markdown('</div>', unsafe_allow_html=True)

        with subtab3:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown("### Upload Food Image")
            uploaded_image = st.file_uploader(
                "Upload an image of ingredients or a dish:",
                type=["png", "jpg", "jpeg"],
                key="recipe_image_uploader"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Generate Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_btn = st.button(
                "🚀 Generate Amazing Recipe", 
                type="primary", 
                use_container_width=True,
                key="generate_recipe_btn"
            )

        # Recipe Generation Logic
        if generate_btn:
            resp = ""
            has_input = (ingre_list and ingre_list.strip()) or audio or uploaded_image
            
            if not has_input:
                st.error("❌ Please provide input using one of the methods above!")
            else:
                with st.spinner("🔮 Creating your perfect recipe..."):
                    
                    # Text input
                    if ingre_list and ingre_list.strip():
                        st.info("📝 Processing text ingredients...")
                        placeholder = st.empty()
                        for chunk in chain.stream({"text_input": ingre_list}):
                            resp += chunk.content
                            placeholder.markdown("**Generating...** ✨")
                        placeholder.empty()
                    
                    # Voice input
                    elif audio:
                        st.info("🎤 Processing voice recording...")
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                            with wave.open(tmp.name, "wb") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(16000)
                                wf.writeframes(audio["bytes"])
                            temp_filename = tmp.name
                        resp = voice_to_recipe(temp_filename)
                    
                    # Image input
                    elif uploaded_image:
                        st.info("📸 Analyzing uploaded image...")
                        base64_img = encode_image(uploaded_image)
                        resp = pic_to_recipe(base64_img)
                
                # Display Results
                if resp:
                    st.markdown('<div class="recipe-output">', unsafe_allow_html=True)
                    
                    recipe_name = get_recipe(resp)
                    st.markdown(f'<div class="recipe-title">🍽️ {recipe_name}</div>', unsafe_allow_html=True)
                    st.markdown(resp)
                    
                    # Only generate AI images if NOT image upload
                    if not uploaded_image:
                        st.markdown("### 📸 Recipe Visualization")
                        col1, col2 = st.columns(2)
                        with col1:
                            try:
                                img_query = f"generate the image of {recipe_name}"
                                response = recipe_image(img_query)
                                st.image(show_image(response), caption=f"AI Generated: {recipe_name}")
                            except Exception:
                                st.warning("⚠️ Could not generate AI image")
                        with col2:
                            width, height, seed, model = 1024, 1024, 42, 'nanobanana'
                            image_url = f"https://pollinations.ai/p/{recipe_name}?width={width}&height={height}&seed={seed}&model={model}"
                            st.image(image_url, caption=f"Alternative View: {recipe_name}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 Download Recipe as Markdown",
                            data=resp,
                            file_name=f"{recipe_name.replace(' ', '_')}_recipe.md",
                            mime="text/markdown",
                            type="secondary",
                            use_container_width=True
                        )
                    
                    st.success("🎉 Recipe generated successfully! Enjoy cooking!")
                else:
                    st.error("❌ Failed to generate recipe. Please try again.")

    with tab2:
        st.header("⚠️ Ingredient Risk Analyzer")

        # Check for user profile
        if not hasattr(st.session_state, 'current_profile') or not st.session_state.current_profile:
            st.warning("⚠️ Please create or select a user profile from the sidebar before analyzing ingredients!")
            st.info("👈 Go to the sidebar to set up your profile with allergy information and dietary restrictions.")

        # Initialize session state
        if 'processing_step' not in st.session_state:
            st.session_state.processing_step = None

        def stream_text(text, container=None, delay=0.005):
            """Stream text word by word for smooth display"""
            if container is None:
                container = st.empty()
            
            displayed_text = ""
            words = text.split()
            
            for word in words:
                displayed_text += word + " "
                container.markdown(displayed_text)
                time.sleep(delay)
            
            return container

        def stream_write(text, delay=0.005):
            """Create new container and stream text into it"""
            container = st.empty()
            return stream_text(text, container, delay)

        def safe_json_extract(text, pattern=r"```json\s*({.*?})"):
            """Safely extract JSON from text with multiple fallback patterns"""
            patterns = [
                r"```json\s*({.*?})",
                r"```\s*({.*?})",
                r"({.*?})",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.DOTALL)
                if matches:
                    try:
                        return json.loads(matches[0])
                    except json.JSONDecodeError:
                        continue
            
            try:
                return json.loads(text.strip())
            except json.JSONDecodeError:
                return None

        def display_risk_scoring_stream(risk_data):
            """Display risk scoring with streaming effect"""
            st.header("⚠️ Risk Analysis")
            
            if not risk_data:
                stream_write("❌ Could not parse the risk scoring data. Please try again with a clearer image.")
                return
            
            allergens = risk_data.get("allergens_found", [])
            score = risk_data.get("risk_score", None)
            explanation = risk_data.get("explanation", "")
            
            # Stream allergens information
            if allergens:
                allergen_text = f"**🚨 Allergens Detected:** {', '.join([f'`{a}`' for a in allergens])}"
            else:
                allergen_text = "**✅ No Common Allergens Detected**"
            
            stream_write(allergen_text)
            time.sleep(0.2)
            
            # Stream risk score
            if score is not None:
                try:
                    score_float = float(score)
                    if score_float >= 0.8:
                        emoji = "🔴"
                        risk_level = "High Risk"
                    elif score_float >= 0.5:
                        emoji = "🟡"
                        risk_level = "Medium Risk"
                    else:
                        emoji = "🟢"
                        risk_level = "Low Risk"
                    
                    score_text = f"**{emoji} Risk Score:** {score}/1.0 ({risk_level})"
                except (ValueError, TypeError):
                    score_text = f"**📊 Risk Score:** {score}"
            else:
                score_text = "**📊 Risk Score:** Not available"
            
            stream_write(score_text)
            time.sleep(0.2)
            
            # Stream explanation
            if explanation:
                explanation_text = f"**💡 Detailed Analysis:**\n\n{explanation}"
                stream_write(explanation_text)

        def display_alternatives_stream(alternatives_data):
            """Display alternatives with streaming effect"""
            st.header("🌱 Alternative Suggestions")
            
            if not alternatives_data:
                stream_write("❌ Could not find alternative suggestions at the moment. Please try again.")
                return
            
            alternatives = alternatives_data.get("alternative_suggestions", [])
            if not alternatives:
                stream_write("🤔 No specific alternative suggestions were found. Consider looking for products with simpler ingredient lists and fewer additives.")
                return
            
            stream_write(f"**Found {len(alternatives)} healthier alternatives for you:**")
            time.sleep(0.3)
            
            for i, alt in enumerate(alternatives):
                st.subheader(f"✅ Option {i+1}")
                
                product_name = alt.get('product_name', f'Alternative {i+1}')
                reason = alt.get('reason', 'No specific reason provided')
                
                # Stream product name
                product_text = f"**📦 Product:** {product_name}"
                stream_write(product_text)
                time.sleep(0.2)
                
                # Stream reason
                reason_text = f"**🎯 Why this is better:** {reason}"
                stream_write(reason_text)
                time.sleep(0.2)
                
                # Handle allergen profile
                allergen_profile = alt.get('allergen_profile', {})
                if isinstance(allergen_profile, dict) and allergen_profile:
                    profile_items = [f"{k}: {v}" for k, v in allergen_profile.items()]
                    profile_text = ", ".join(profile_items)
                    allergen_text = f"**🛡️ Allergen Profile:** {profile_text}"
                elif allergen_profile:
                    allergen_text = f"**🛡️ Allergen Profile:** {allergen_profile}"
                else:
                    allergen_text = "**🛡️ Allergen Profile:** Information not available"
                
                stream_write(allergen_text)
                
                # Add separator between alternatives
                if i < len(alternatives) - 1:
                    time.sleep(0.3)
                    st.markdown("---")

        # Main app logic
        try:
            # Configure Gemini
            st.session_state.processing_step = "Configuring Gemini"
            configure_gemini()
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload an image of ingredient list", 
                type=["png", "jpg", "jpeg"],
                help="Upload a clear image of ingredient list or product label",
                key="risk_analyzer_uploader"
            )
            
            if uploaded_file is not None:
                # Display uploaded image
                # st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                if st.button("Get Analysis"):
                
                    # Show progress with status
                    with st.status("🔍 Analyzing your image...", expanded=True) as status:
                        try:
                            # Step 1: Extract text from image
                            status.write("📖 Extracting text from image...")
                            st.session_state.processing_step = "Extracting text from image"
                            
                            i_to_text = extract_text_from_image(uploaded_file, "extract all the text from the image")
                            
                            if not i_to_text or i_to_text.strip() == "":
                                status.update(label="❌ Text extraction failed", state="error")
                                stream_write("Could not extract readable text from the image. Please try uploading a clearer photo with better lighting and focus.")
                                st.stop()
                            
                            status.write("✅ Text extracted successfully")
                            
                            # Step 2: Extract ingredients
                            status.write("🧪 Identifying ingredients...")
                            st.session_state.processing_step = "Extracting ingredients"
                            
                            # Dynamic import to avoid circular dependency
                            from risk_analyzer.ingredent_agent import text_extractor
                            ingredients_resp = text_extractor.run(f"the user input is: {i_to_text}")
                            
                            if not hasattr(ingredients_resp, 'content') or not ingredients_resp.content:
                                status.update(label="❌ Ingredient extraction failed", state="error")
                                stream_write("Could not identify ingredients from the extracted text. Please ensure the image shows a clear ingredient list.")
                                st.stop()
                            
                            extracted_ingredients = ingredients_resp.content
                            status.write("✅ Ingredients identified")
                            
                            # Step 3: Risk scoring
                            status.write("⚖️ Analyzing health risks...")
                            st.session_state.processing_step = "Analyzing risks"
                            
                            # Dynamic import to avoid circular dependency
                            from risk_analyzer.ingredent_agent import risk_scoring
                            # Get user allergies from current session
                            user_allergies = allergies if allergies else []
                            risk_resp = risk_scoring.run(f"ingredients: {extracted_ingredients}, user_allergy: {user_allergies}")

                            if not hasattr(risk_resp, 'content') or not risk_resp.content:
                                status.update(label="❌ Risk analysis failed", state="error")
                                stream_write("Encountered an issue while analyzing health risks. Please try again.")
                                st.stop()
                            
                            status.write("✅ Risk analysis complete")
                            
                            # Step 4: Get alternatives
                            status.write("🔍 Finding healthier alternatives...")
                            st.session_state.processing_step = "Finding alternatives"
                            
                            # Dynamic import to avoid circular dependency
                            from risk_analyzer.ingredent_agent import risk_alternate
                            alternatives_resp = risk_alternate.run(risk_resp.content if hasattr(risk_resp, 'content') else risk_resp)
                            status.write("✅ Analysis complete!")
                            status.update(label="✅ Analysis complete!", state="complete")
                            
                        except Exception as e:
                            status.update(label="❌ Analysis failed", state="error")
                            stream_write(f"Error during {st.session_state.processing_step}: {str(e)}")
                            with st.expander("Error Details", expanded=False):
                                st.code(traceback.format_exc())
                            st.stop()
                    
                    # Display results with streaming
                    st.success("🎉 Analysis Complete! Here are your results:")
                    
                    # Show risk analysis
                    risk_data = safe_json_extract(risk_resp.content)
                    display_risk_scoring_stream(risk_data)
                    time.sleep(0.5)
                    
                    # Show alternatives
                    if hasattr(alternatives_resp, 'content') and alternatives_resp.content:
                        alternatives_text = alternatives_resp.content.replace('```json', '').replace('```', '').strip()
                        
                        try:
                            alternatives_data = json.loads(alternatives_text)
                            display_alternatives_stream(alternatives_data)
                        except json.JSONDecodeError:
                            st.header("🌱 Alternative Suggestions")
                            stream_write("Found some alternative suggestions, but having trouble formatting them. Here's the raw information:")
                            time.sleep(0.2)
                            stream_write(alternatives_resp.content)
                    else:
                        st.header("🌱 Alternative Suggestions")
                        stream_write("⚠️ Could not generate alternative suggestions at this time. Please try again or consult with a nutritionist for personalized advice.")
                    
                    # Final message
                    time.sleep(0.5)
                    st.balloons()
                    stream_write("🏁 **Analysis Complete!** You can upload another product image to analyze more ingredients.")

        except Exception as e:
            st.error(f"❌ Application Error: {str(e)}")
            with st.expander("Error Details", expanded=False):
                st.code(traceback.format_exc())

    with tab3:
        st.header("🧪 Ingredient Nutrient Analyzer")
        inputs=st.text_input("Enter the recipe name that you want to analyze")
        if inputs:
            if st.button("get Analysis"):
                resp=nutrient_agent.run(inputs).content
                resp=resp.replace("```json","").replace("```","")

                json_obj=json.loads(resp)

                for key, value in json_obj.items():
                    st.write(f"{key}:")
                    for nutrient, amount in value.items():
                        st.write(f"  {nutrient}: {amount}")

    with tab4:
        st.header("🍽️ Meal Planner")
        if not hasattr(st.session_state, 'current_profile') or not st.session_state.current_profile:
            st.warning("⚠️ Please create or select a user profile from the sidebar before generating a meal plan!")
            st.info("👈 Go to the sidebar to set up your profile with dietary preferences and nutritional targets.")
        else:
            if st.button("Generate Meal Plan: ", key="meal_plan_generator"):
                with st.spinner('Generating meal plan...'):
                    time.sleep(2)
                profile = st.session_state.current_profile
                recipe_list=[]
                allergies_list=profile.allergies
                meal_planner_download = []

                # Breakfast

                resp=generate_meal(profile.calorie_target,
                                profile.protein_target,
                                profile.fat_target,
                                profile.carb_target
                                ,"breakfast",
                                recipe_list,allergies_list).recipes
                
                st.write("This is the meal plain for the morning i.e breakfast shift")
                meal_planner_download+=resp
                for recipe in resp:
                    st.markdown("### 🍽️ **Recipe Name:**")
                    st.subheader(recipe.recipe_name)
                    recipe_list.append(recipe.recipe_name)
                    st.markdown("#### 🧂 **Ingredients:**")

                    # Two-column layout for ingredients
                    col1, col2 = st.columns(2)

                    # Split ingredients roughly into two halves
                    half = len(recipe.ingredients) // 2 + len(recipe.ingredients) % 2
                    left_ing = recipe.ingredients[:half]
                    right_ing = recipe.ingredients[half:]

                    with col1:
                        for i in left_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")

                    with col2:
                        for i in right_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")
                    st.markdown("#### 🧮 **Nutritional Information:**")

                    # Two-column layout for nutrients
                    ncol1, ncol2 = st.columns(2)

                    with ncol1:
                        st.metric(label="🔥 Calories", value=f"{recipe.nutrients.calories:.1f} kcal")
                        st.metric(label="🍞 Carbohydrates", value=f"{recipe.nutrients.carbohydrates:.1f} g")

                    with ncol2:
                        st.metric(label="🥑 Fats", value=f"{recipe.nutrients.fats:.1f} g")
                        st.metric(label="🍗 Proteins", value=f"{recipe.nutrients.proteins:.1f} g")

                    st.markdown("---")

                # Lunch

                resp=generate_meal(profile.calorie_target,
                                profile.protein_target,
                                profile.fat_target,
                                profile.carb_target
                                ,"lunch",
                                recipe_list,allergies_list).recipes
                
                meal_planner_download+=resp
                st.write("This is the meal plain for the Lunch i.e AfterNoon shift")

                for recipe in resp:
                    st.markdown("### 🍽️ **Recipe Name:**")
                    st.subheader(recipe.recipe_name)
                    recipe_list.append(recipe.recipe_name)
                    st.markdown("#### 🧂 **Ingredients:**")

                    # Two-column layout for ingredients
                    col1, col2 = st.columns(2)

                    # Split ingredients roughly into two halves
                    half = len(recipe.ingredients) // 2 + len(recipe.ingredients) % 2
                    left_ing = recipe.ingredients[:half]
                    right_ing = recipe.ingredients[half:]

                    with col1:
                        for i in left_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")

                    with col2:
                        for i in right_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")
                    st.markdown("#### 🧮 **Nutritional Information:**")

                    # Two-column layout for nutrients
                    ncol1, ncol2 = st.columns(2)

                    with ncol1:
                        st.metric(label="🔥 Calories", value=f"{recipe.nutrients.calories:.1f} kcal")
                        st.metric(label="🍞 Carbohydrates", value=f"{recipe.nutrients.carbohydrates:.1f} g")

                    with ncol2:
                        st.metric(label="🥑 Fats", value=f"{recipe.nutrients.fats:.1f} g")
                        st.metric(label="🍗 Proteins", value=f"{recipe.nutrients.proteins:.1f} g")

                    st.markdown("---")

            
                # # Dinner

                resp=generate_meal(profile.calorie_target,
                                profile.protein_target,
                                profile.fat_target,
                                profile.carb_target
                                ,"dinner",
                                recipe_list,allergies_list).recipes
                meal_planner_download+=resp
                
                st.write("This is the meal plain for the Dinner i.e Night shift")

                for recipe in resp:
                    st.markdown("### 🍽️ **Recipe Name:**")
                    st.subheader(recipe.recipe_name)
                    recipe_list.append(recipe.recipe_name)
                    st.markdown("#### 🧂 **Ingredients:**")

                    # Two-column layout for ingredients
                    col1, col2 = st.columns(2)

                    # Split ingredients roughly into two halves
                    half = len(recipe.ingredients) // 2 + len(recipe.ingredients) % 2
                    left_ing = recipe.ingredients[:half]
                    right_ing = recipe.ingredients[half:]

                    with col1:
                        for i in left_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")

                    with col2:
                        for i in right_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")
                    st.markdown("#### 🧮 **Nutritional Information:**")

                    # Two-column layout for nutrients
                    ncol1, ncol2 = st.columns(2)

                    with ncol1:
                        st.metric(label="🔥 Calories", value=f"{recipe.nutrients.calories:.1f} kcal")
                        st.metric(label="🍞 Carbohydrates", value=f"{recipe.nutrients.carbohydrates:.1f} g")

                    with ncol2:
                        st.metric(label="🥑 Fats", value=f"{recipe.nutrients.fats:.1f} g")
                        st.metric(label="🍗 Proteins", value=f"{recipe.nutrients.proteins:.1f} g")

                    st.markdown("---")

                # # Snacks

                resp=generate_meal(profile.calorie_target,
                                profile.protein_target,
                                profile.fat_target,
                                profile.carb_target
                                ,"Snacks",
                                recipe_list,allergies_list).recipes
                
                meal_planner_download+=resp
                st.write("This is the meal plain for the Snacks")

                for recipe in resp:
                    st.markdown("### 🍽️ **Recipe Name:**")
                    st.subheader(recipe.recipe_name)
                    recipe_list.append(recipe.recipe_name)
                    st.markdown("#### 🧂 **Ingredients:**")

                    # Two-column layout for ingredients
                    col1, col2 = st.columns(2)

                    # Split ingredients roughly into two halves
                    half = len(recipe.ingredients) // 2 + len(recipe.ingredients) % 2
                    left_ing = recipe.ingredients[:half]
                    right_ing = recipe.ingredients[half:]

                    with col1:
                        for i in left_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")

                    with col2:
                        for i in right_ing:
                            st.markdown(f"- **{i.name}**: {i.quantity} {i.unit}")
                            
                    st.markdown("#### 🧮 **Nutritional Information:**")

                    # Two-column layout for nutrients
                    ncol1, ncol2 = st.columns(2)

                    with ncol1:
                        st.metric(label="🔥 Calories", value=f"{recipe.nutrients.calories:.1f} kcal")
                        st.metric(label="🍞 Carbohydrates", value=f"{recipe.nutrients.carbohydrates:.1f} g")

                    with ncol2:
                        st.metric(label="🥑 Fats", value=f"{recipe.nutrients.fats:.1f} g")
                        st.metric(label="🍗 Proteins", value=f"{recipe.nutrients.proteins:.1f} g")

                    st.markdown("---")

                # Convert list to markdown string
                markdown_content = "# Daily Meal Plan\n\n"
                for i, recipe in enumerate(meal_planner_download, 1):
                    markdown_content += f"## Recipe {i}: {recipe.recipe_name}\n\n"
                    markdown_content += "### Ingredients:\n"
                    for ing in recipe.ingredients:
                        markdown_content += f"- {ing.name}: {ing.quantity} {ing.unit}\n"
                    markdown_content += f"\n### Nutrition:\n"
                    markdown_content += f"- Calories: {recipe.nutrients.calories}\n"
                    markdown_content += f"- Carbs: {recipe.nutrients.carbohydrates}g\n"
                    markdown_content += f"- Fats: {recipe.nutrients.fats}g\n"
                    markdown_content += f"- Proteins: {recipe.nutrients.proteins}g\n\n"
                
                if markdown_content:
                    st.download_button(
                        label="Download Markdown File",
                        data=markdown_content,
                        file_name="Daily_Meal_Planner.md",
                        mime="text/markdown"
                    )

                else:
                    st.warning("No content to download.")           