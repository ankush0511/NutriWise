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
    page_title="🍳 AI Recipe Generator",
    page_icon="🍳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #FF6B35;
    font-size: 3.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
}
.subtitle {
    text-align: center;
    color: #666;
    font-size: 1.3rem;
    margin-bottom: 3rem;
}
.input-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    color: white;
}
.input-card h3 {
    color: white;
    margin-bottom: 1rem;
}
.recipe-output {
    background-color: #fff;
    padding: 2rem;
    border-radius: 15px;
    border-left: 5px solid #FF6B35;
    margin: 2rem 0;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}
.recipe-title {
    font-size: 2rem;
    font-weight: bold;
    color: #FF6B35;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🍳 AI Recipe Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform ingredients into delicious recipes using Text, Voice, or Images</p>', unsafe_allow_html=True)

# Input Methods
st.markdown("## 📝 Choose Your Input Method")

tab1, tab2, tab3 = st.tabs(["📝 Text Input", "🎤 Voice Recording", "📸 Image Upload"])

with tab1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("### Type Your Ingredients")
    ingre_list = st.text_area(
        "List your available ingredients:",
        placeholder="e.g., paneer, rice, tomatoes, onions, spices...",
        height=120,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("### Record Your Voice")
    st.info("🎤 Click to start recording and speak your ingredients clearly")
    audio = mic_recorder(
        start_prompt="🎤 Start Recording", 
        stop_prompt="⏹️ Stop Recording", 
        key='recorder'
    )
    if audio:
        st.success("✅ Audio recorded successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("### Upload Food Image")
    uploaded_image = st.file_uploader(
        "Upload an image of ingredients or a dish:",
        type=["png", "jpg", "jpeg"]
    )
    # if uploaded_image:
        # st.image(uploaded_image, caption="Uploaded Image", width=350)
    st.markdown('</div>', unsafe_allow_html=True)

# Generate Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_btn = st.button(
        "🚀 Generate Amazing Recipe", 
        type="primary", 
        use_container_width=True,
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem;'>
    <h4>🌟 Features</h4>
    <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
        <div>🤖 AI-Powered Generation</div>
        <div>🎤 Voice Recognition</div>
        <div>📸 Image Analysis</div>
        <div>🖼️ Auto Image Generation (for text/voice)</div>
        <div>📥 Download Recipes</div>
    </div>
    <br>
    <p style='color: #666; margin-top: 2rem;'>Made with ❤️ using Streamlit & AI</p>
</div>
""", unsafe_allow_html=True)
