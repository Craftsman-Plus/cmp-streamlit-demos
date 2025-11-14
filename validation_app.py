import streamlit as st
import base64
import requests
from authenticate import authenticate_and_get_token
from PyPDF2 import PdfReader
import json

st.set_page_config(page_title="Brand Guidelines Validator", layout="wide")

# Pre-filled authentication details
default_email = ""
default_password = ""
default_client_id = "4djrt5jve4ud0de66i75splf7l"

# Function to authenticate and get token
def get_token(email, password, client_id):
    try:
        return authenticate_and_get_token(email, password, client_id)
    except Exception as e:
        st.error(f"Error during authentication: {e}")
        return None

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        texts = [page.extract_text() for page in reader.pages]
        return texts
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Function to encode image to base64
def encode_image_to_base64(image_file):
    try:
        return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

# Function to validate image
def validate_image(token, image_b64, brand, guidelines=None, vision=True, user=""):
    try:
        url = 'https://ai.dev.craftsmanplus.com/api/images/validate'
        payload = {
            "image": image_b64,
            "brand": brand,
            "vision": vision,
            "user": user
        }
        if guidelines is not None:
            payload["guidelines"] = guidelines
        
        response = requests.post(
            url=url,
            json=payload,
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error during validation: {e}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response: {e.response.text}")
        return None

# Initialize session state
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False

# Sidebar menu
st.sidebar.title("🎨 Brand Guidelines Validator")
menu_option = st.sidebar.selectbox(
    "Select an option",
    ["Home", "Image Validation"]
)

# Display authentication status
status_text = "✅ Authenticated" if st.session_state.is_authenticated else "❌ Not Authenticated"
status_color = "green" if st.session_state.is_authenticated else "red"
st.sidebar.markdown(
    f"<p style='font-size: 14px; color: {status_color}; font-weight: bold;'>{status_text}</p>",
    unsafe_allow_html=True
)

# Main content
if menu_option == "Home":
    st.title("🏠 Welcome to Brand Guidelines Validator")
    st.markdown("""
    This application allows you to validate playable images against brand guidelines using AI.
    
    ### Features:
    - 📄 Upload brand guidelines as PDF
    - 🖼️ Upload playable images for validation
    - 🤖 Choose between Vision-based or Text-based validation
    - ✅ Get detailed compliance results
    
    ### How to use:
    1. **Authenticate** with your credentials below
    2. Navigate to **Image Validation** in the sidebar
    3. Upload your brand guidelines (PDF) or enter a brand name
    4. Upload an image to validate
    5. Get instant validation results!
    """)
    
    st.divider()
    
    st.header("🔐 User Authentication")
    with st.form(key='auth_form'):
        email = st.text_input("Email", value=default_email, placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", value=default_password)
        client_id = st.text_input("Client ID", value=default_client_id, disabled=True)
        submit_auth = st.form_submit_button("🔓 Authenticate")

    if submit_auth:
        if email and password and client_id:
            with st.spinner('🔄 Authenticating...'):
                token = get_token(email, password, client_id)
            if token:
                st.success("✅ Authenticated successfully!")
                st.session_state.token = token
                st.session_state.is_authenticated = True
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Authentication failed. Please check your credentials.")
        else:
            st.error("⚠️ Please fill all the fields!")

elif menu_option == "Image Validation":
    st.title("🖼️ Brand Guidelines Image Validation")
    
    if not st.session_state.is_authenticated:
        st.warning("⚠️ Please authenticate first in the Home section.")
        st.stop()
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Brand Guidelines")
        
        # Brand name input
        brand_name = st.text_input(
            "Brand Name",
            placeholder="e.g., slack, coca-cola",
            help="Enter the brand name. If guidelines are stored in S3, they will be fetched automatically."
        )
        
        # Guidelines upload option
        st.subheader("Upload Guidelines (Optional)")
        st.info("💡 If you don't upload guidelines, the system will try to fetch them from S3 using the brand name.")
        guidelines_file = st.file_uploader(
            "Upload Brand Guidelines PDF",
            type=['pdf'],
            help="Upload a PDF containing the brand guidelines"
        )
        
        guidelines_text = None
        if guidelines_file:
            with st.spinner("📖 Extracting text from PDF..."):
                guidelines_text = extract_pdf_text(guidelines_file)
            if guidelines_text:
                st.success(f"✅ Successfully extracted {len(guidelines_text)} pages from PDF")
                with st.expander("📄 Preview Guidelines Text"):
                    preview_text = "\n\n".join(guidelines_text[:2])  # Show first 2 pages
                    st.text_area("First 2 pages:", preview_text, height=200)
    
    with col2:
        st.header("🎨 Image to Validate")
        
        # Image upload
        image_file = st.file_uploader(
            "Upload Playable Image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image to validate against brand guidelines"
        )
        
        if image_file:
            st.image(image_file, caption="Uploaded Image", use_container_width=True)
    
    st.divider()
    
    # Validation options
    st.header("⚙️ Validation Settings")
    col_settings1, col_settings2 = st.columns(2)
    
    with col_settings1:
        validation_mode = st.radio(
            "Validation Mode",
            ["Vision-based (AI Vision)", "Text-based (Guidelines Text)"],
            help="Vision-based: Uses AI to directly analyze the image. Text-based: Uses extracted text from guidelines."
        )
        use_vision = validation_mode.startswith("Vision")
    
    with col_settings2:
        user_name = st.text_input(
            "User Name (Optional)",
            placeholder="Your name",
            help="Optional: Add your name for tracking purposes"
        )
    
    st.divider()
    
    # Validate button
    if st.button("🚀 Validate Image", type="primary", use_container_width=True):
        if not brand_name:
            st.error("⚠️ Please enter a brand name!")
        elif not image_file:
            st.error("⚠️ Please upload an image to validate!")
        elif not use_vision and not guidelines_text:
            st.warning("⚠️ Text-based validation requires guidelines to be uploaded. Using Vision-based validation instead...")
            use_vision = True
        
        if brand_name and image_file:
            with st.spinner('🔍 Validating image...'):
                # Reset file pointer
                image_file.seek(0)
                
                # Encode image to base64
                image_b64 = encode_image_to_base64(image_file)
                
                if image_b64:
                    # Perform validation
                    result = validate_image(
                        token=st.session_state.token,
                        image_b64=image_b64,
                        brand=brand_name,
                        guidelines=guidelines_text if not use_vision else None,
                        vision=use_vision,
                        user=user_name
                    )
                    
                    if result:
                        st.divider()
                        st.header("📊 Validation Results")
                        
                        # Display results
                        compliant = result.get('compliant', False)
                        reasons = result.get('reasons', [])
                        
                        if compliant:
                            st.success("✅ **IMAGE IS COMPLIANT** with brand guidelines!")
                            st.balloons()
                        else:
                            st.error("❌ **IMAGE IS NOT COMPLIANT** with brand guidelines")
                        
                        # Display reasons if any
                        if reasons and len(reasons) > 0:
                            st.subheader("📝 Detailed Reasons:")
                            for i, reason in enumerate(reasons, 1):
                                st.warning(f"{i}. {reason}")
                        elif not compliant:
                            st.info("No specific reasons provided.")
                        
                        # Show raw JSON response
                        with st.expander("🔍 View Raw JSON Response"):
                            st.json(result)
                        
                        # Download results option
                        st.divider()
                        result_json = json.dumps(result, indent=2)
                        st.download_button(
                            label="💾 Download Results as JSON",
                            data=result_json,
                            file_name=f"validation_results_{brand_name}.json",
                            mime="application/json"
                        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <small>Brand Guidelines Validator | Powered by OpenAI & Craftsman+</small>
</div>
""", unsafe_allow_html=True)

