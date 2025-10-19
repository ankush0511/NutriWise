import re
import streamlit as st
import json
import traceback
import time
from risk_analyzer.ingredent_agent import text_extractor, risk_alternate, risk_scoring
from risk_analyzer.text_extraction import configure_gemini, extract_text_from_image

# Configure page
st.set_page_config(page_title="Ingredient Risk Analyzer", page_icon="🔍")
st.title("🔍 Ingredient Risk Analyzer")

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
        help="Upload a clear image of ingredient list or product label"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
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
                
                risk_resp = risk_scoring.run(extracted_ingredients)
                
                if not hasattr(risk_resp, 'content') or not risk_resp.content:
                    status.update(label="❌ Risk analysis failed", state="error")
                    stream_write("Encountered an issue while analyzing health risks. Please try again.")
                    st.stop()
                
                status.write("✅ Risk analysis complete")
                
                # Step 4: Get alternatives
                status.write("🔍 Finding healthier alternatives...")
                st.session_state.processing_step = "Finding alternatives"
                
                alternatives_resp = risk_alternate.run(risk_resp.content)
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

# Sidebar information
with st.sidebar:
    st.header("ℹ️ How to Use")
    st.write("""
    1. 📤 Upload a clear image of ingredients
    2. ⏳ Wait for AI analysis
    3. 📊 Review risk assessment  
    4. 🌱 Check healthier alternatives
    """)
    
    st.header("💡 Tips for Best Results")
    st.write("""
    - Use good lighting when taking photos
    - Keep the image focused and clear
    - Ensure ingredient text is readable
    - Avoid glare, shadows, or blur
    - Include the entire ingredient list
    """)
    
    st.header("🔧 Troubleshooting")
    st.write("""
    - **Blurry text?** → Retake photo with better focus
    - **Poor lighting?** → Use natural light or better lamp
    - **Cut-off ingredients?** → Include full ingredient list
    - **Error messages?** → Try a different image format
    """)

    if st.button("🔄 Reset Application"):
        st.rerun()