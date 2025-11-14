import streamlit as st
import base64
import requests
from authenticate import authenticate_and_get_token
from PyPDF2 import PdfReader
import json
import streamlit_cookies_manager

st.set_page_config(page_title="Brand Guidelines Validator", layout="wide")

# Initialize cookies manager
cookies = streamlit_cookies_manager.EncryptedCookieManager(
    prefix="validation_app_",
    password="your-secret-password-here-change-in-production"
)

if not cookies.ready():
    st.stop()

# Pre-filled authentication details
default_email = "system.admin@craftsmanplus.com"
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
    # Check if we have a saved token in cookies
    saved_token = cookies.get('auth_token')
    if saved_token:
        st.session_state.is_authenticated = True
        st.session_state.token = saved_token
    else:
        st.session_state.is_authenticated = False

if 'use_default_image' not in st.session_state:
    st.session_state.use_default_image = False

# Default sample image URL (you can change this to any publicly accessible image)
DEFAULT_IMAGE_URL = "https://i.imgur.com/IsAk2ag.png"

# Page header
st.title("🎨 Brand Guidelines Validator")

# Logout button in sidebar
if st.session_state.is_authenticated:
    with st.sidebar:
        st.success("✅ Logged in")
        if st.button("🚪 Logout"):
            st.session_state.is_authenticated = False
            st.session_state.token = None
            cookies['auth_token'] = ''
            cookies.save()
            st.rerun()

# Authentication section (compact)
if not st.session_state.is_authenticated:
    with st.expander("🔐 Authentication Required", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            email = st.text_input("Email", value=default_email)
            password = st.text_input("Password", type="password", value=default_password)
        with col2:
            st.write("")
            st.write("")
            if st.button("🔓 Login", use_container_width=True):
                if email and password:
                    with st.spinner('Authenticating...'):
                        token = get_token(email, password, default_client_id)
                    if token:
                        st.session_state.token = token
                        st.session_state.is_authenticated = True
                        # Save token to cookies for persistent login
                        cookies['auth_token'] = token
                        cookies.save()
                        st.rerun()
                    else:
                        st.error("Authentication failed")
                else:
                    st.error("Please fill in credentials")
    st.stop()

# Main content (only shown when authenticated)

# Two columns layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Configuration")
    
    # Brand name
    brand_name = st.text_input(
        "Brand Name",
        value="slack",
        help="Enter the brand name"
    )
    
    # Show info about existing guidelines
    if brand_name.lower() == "slack":
        st.info("✨ Slack brand guidelines are already available in S3")
    
    # Validation mode
    use_vision = st.toggle("Use Vision-based Validation", value=True, help="Vision-based uses AI to directly analyze images against S3 guidelines. Turn off to upload custom PDF guidelines.")
    
    # Optional guidelines upload for text-based mode
    if not use_vision:
        st.caption("📤 Upload custom brand guidelines PDF (optional - will use S3 if available)")
        guidelines_file = st.file_uploader(
            "Upload Guidelines PDF",
            type=['pdf'],
            help="Upload a PDF to override S3 guidelines for text-based validation",
            label_visibility="collapsed"
        )
        guidelines_text = None
        if guidelines_file:
            with st.spinner("Reading PDF..."):
                guidelines_text = extract_pdf_text(guidelines_file)
            if guidelines_text:
                st.success(f"✅ Using uploaded PDF ({len(guidelines_text)} pages)")
        else:
            st.info("💡 Will fetch guidelines from S3 if available")

with col2:
    st.subheader("🖼️ Upload Image")
    
    # Option to use default image
    use_default = st.checkbox("Use default sample image", value=False)
    
    if use_default:
        st.info("Using default Slack logo for testing")
        st.image(DEFAULT_IMAGE_URL, use_container_width=True)
        image_file = None
        st.session_state.use_default_image = True
    else:
        st.session_state.use_default_image = False
        # Image upload
        image_file = st.file_uploader(
            "Select playable image",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )
        
        if image_file:
            st.image(image_file, use_container_width=True)

st.divider()

# Validate button
has_image = image_file is not None or st.session_state.use_default_image
if st.button("🚀 Validate Image", type="primary", use_container_width=True, disabled=not has_image):
    if not has_image:
        st.error("Please upload an image or use default image")
    else:
        with st.spinner('🔍 Validating...'):
            # Handle default image vs uploaded image
            if st.session_state.use_default_image:
                # Download default image and encode
                response = requests.get(DEFAULT_IMAGE_URL)
                if response.status_code == 200:
                    image_b64 = base64.b64encode(response.content).decode('utf-8')
                else:
                    st.error("Failed to load default image")
                    image_b64 = None
            else:
                image_file.seek(0)
                image_b64 = encode_image_to_base64(image_file)
            
            if image_b64:
                result = validate_image(
                    token=st.session_state.token,
                    image_b64=image_b64,
                    brand=brand_name,
                    guidelines=guidelines_text if not use_vision else None,
                    vision=use_vision,
                    user=""
                )
                
                if result:
                    st.divider()
                    
                    # Display results
                    compliant = result.get('compliant', False)
                    compliance = result.get('compliance')
                    reasons = result.get('reasons', [])
                    
                    # Show compliance status
                    if compliance is not None:
                        st.metric("Compliance Score", f"{compliance}%")
                    
                    if compliant:
                        st.success("✅ Image is compliant with brand guidelines")
                        st.balloons()
                    else:
                        st.error("❌ Image is not compliant")
                    
                    # Display reasons
                    if reasons and len(reasons) > 0:
                        st.subheader("Issues Found:")
                        for i, reason in enumerate(reasons, 1):
                            st.warning(f"{i}. {reason}")
                    
                    # Raw JSON in expander
                    with st.expander("View Raw Response"):
                        st.json(result)
                    
                    # Download button
                    result_json = json.dumps(result, indent=2)
                    st.download_button(
                        label="💾 Download Results",
                        data=result_json,
                        file_name=f"validation_{brand_name}.json",
                        mime="application/json"
                    )

