import streamlit as st
import time
import requests
from authenticate import authenticate_and_get_token
import json

st.set_page_config(layout="wide")

# Pre-filled authentication details
default_email = ""
default_password = ""
default_client_id = "4djrt5jve4ud0de66i75splf7l"

# Initialize session state for assets
if 'assets' not in st.session_state:
    st.session_state.assets = [
        {"id": "fdsj2", "type": "image", "urls": ["https://fastly.picsum.photos/id/839/536/354.jpg?hmac=rRPD5ORZY8xibjxZvrRUuUMfyc666vf0KQrPFOcZSJA"]},
        {"id": "dj3fd", "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/wxCzTlJhNPU/2024/05/14/20/1715718355061-K672yLeSICW__optimized.webp",
            "https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/wxCzTlJhNPU/2024/05/24/21/1716584971517-FunhnzEwM8U__optimized.webp"]},
        {"id": "fdskf", "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/CRAFTSMAN/2023/11/27/12/1701087042485-uMqAGSq44Qk__optimized.webp"]},
        {"id": "zcvas", "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/CRAFTSMAN/2024/01/23/12/1706012086458-RHCTYkh6HZp__optimized.webp"]}
    ]

# Function to authenticate and get token
def get_token(email, password, client_id):
    try:
        return authenticate_and_get_token(email, password, client_id)
    except Exception as e:
        st.error(f"Error during authentication: {e}")
        return None

# Function to start the generation process
def start_generation(token, data):
    try:
        url = 'https://ai.dev.craftsmanplus.com/api/playable/generate'
        for asset in data['assets']:
            asset['id'] = str(asset['id'])
        response = requests.post(url, headers={"Authorization": token}, allow_redirects=False, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error during generation: {e}")
        return None

# Function to check the status of the generation process
def check_status(token, job_id):
    try:
        url = f'https://ai.dev.craftsmanplus.com/api/jobs/{job_id}'
        response = requests.get(url, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error checking status: {e}")
        return None

# Function to download the result
def download_result(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error downloading result: {e}")
        return None

# Check authentication status
is_authenticated = st.session_state.get('is_authenticated', False)

# Display authentication status at the top
status_text = "Authenticated ✔️" if is_authenticated else "Not Authenticated ❌"
st.markdown(f"<p style='font-size: 16px; color: {'green' if is_authenticated else 'red'}'>{status_text}</p>", unsafe_allow_html=True)

# Streamlit UI
st.title("Playable Content Generator")

# Create three tabs for authentication, generation data, and results
auth_tab, gen_tab, result_tab = st.tabs(["Authentication", "Generation Data", "Results"])

with auth_tab:
    st.header("User Authentication")
    with st.form(key='auth_form'):
        email = st.text_input("Email", value=default_email)
        password = st.text_input("Password", type="password", value=default_password)
        client_id = st.text_input("Client ID", value=default_client_id, disabled=True)
        submit_auth = st.form_submit_button("Authenticate")

    if submit_auth:
        if email and password and client_id:
            with st.spinner('Authenticating...'):
                token = get_token(email, password, client_id)
            if token:
                st.success("Authenticated successfully!")
                st.session_state.token = token
                st.session_state.is_authenticated = True
                st.rerun()
            else:
                st.error("Authentication failed. Please check your credentials.")
        else:
            st.error("Please fill all the fields!")
import uuid
with gen_tab:
    st.header("Generation Data")
    theme = st.text_input("Theme", value=st.session_state.get('theme', """
wild west
"""))

    style = st.text_input("style", value=st.session_state.get('style', """
cartoon
"""))

    # Dynamic Asset Management
    st.header("Assets")
    input_json = st.text_area("Assets JSON", value=st.session_state.get('assets', "[]").replace("'", '"'))
    
    data = {
        "theme": theme,
        "assets": json.loads(input_json),
        "style": style
    }
    
    # Main focus button for generation
    if st.button("Generate Playable Content"):
        st.write("Please go to 'RESULTS' tab to check the status of the generation process.")
        if 'token' in st.session_state and theme and style:
            st.session_state.theme = theme
            st.session_state.style = style
            st.session_state.assets = input_json
            
            generation_response = start_generation(st.session_state.token, data)
            if generation_response:
                st.success("Generated Job ID!")
                job_id = generation_response.get('id')
                location = generation_response.get('url')
                if job_id and location:
                    st.session_state.job_id = job_id
                    st.session_state.location = location
                    st.session_state.progress = 0
                    st.session_state.phase = "IN_PROGRESS"
                    st.rerun()
                else:
                    st.error("Failed to retrieve job ID or location URL.")
            else:
                st.error("Failed to start generation process.")
        else:
            st.error("Please authenticate and fill in the theme and style!")
            
    st.json(data)

# Results tab
with result_tab:
    if 'job_id' in st.session_state:
        st.header("Generation Results")
        job_id = st.session_state.job_id
        location = st.session_state.location
        token = st.session_state.token

        # Check the status with a progress bar
        progress_bar = st.progress(st.session_state.get('progress', 0))
        status_placeholder = st.empty()
        
        if st.session_state.phase == "IN_PROGRESS":
            while True:
                status_response = check_status(token, job_id)
                if status_response:
                    phase = status_response.get('phase')
                    message = status_response.get('message')
                    status_placeholder.write(f"Phase: {phase}\nMessage: {message}")
                    st.session_state.phase = phase
                    if phase == 'COMPLETED':
                        st.success("Generation completed!")
                        result_data = download_result(location)
                        if result_data:
                            st.session_state.result_data = result_data
                            st.rerun()
                    elif phase == 'FAILED':
                        st.error("Generation failed!")
                        break
                    else:
                        st.session_state.progress = int(status_response.get('progress', 0)) / 100
                        progress_bar.progress(int(st.session_state.progress))
                        time.sleep(2)
                        st.rerun()
        if st.session_state.phase == "COMPLETED" and 'result_data' in st.session_state:
            result_data = st.session_state.result_data
            st.subheader("Theme")
            st.info(result_data['theme'])
            st.subheader("Style")
            st.info(result_data['style'])
            for asset in result_data['assets']:
                st.header(f"Asset {asset['id']}")
                for result in asset['results']:
                    cols_result = st.columns([1, 1])
                    st.text("Result")
                    with cols_result[0]:
                        st.info(f"{result['prompt']}")
                    with cols_result[1]:
                        for url in result['urls']:
                            st.image(url, width=400)
                st.divider()
            st.subheader("Cost")
            st.write(f"Total Cost: {result_data['cost']['totalCost']} {result_data['cost']['currency']}")
            st.json(result_data['cost']['costBreakdown'])
            st.subheader("JSON Results")
            st.json(result_data)
