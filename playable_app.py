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
    st.session_state.assets = []

# Function to authenticate and get token
def get_token(email, password, client_id):
    try:
        return authenticate_and_get_token(email, password, client_id)
    except Exception as e:
        st.error(f"Error during authentication: {e}")
        return None

# Function to query the cost
def query_cost(token, params):
    try:
        url = 'https://ai.dev.craftsmanplus.com/api/cost'
        response = requests.get(url, headers={"Authorization": token}, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error querying cost: {e}")
        return None

# Function to start the generation process
def start_generation(token, data, endpoint):
    try:
        url = f'https://ai.dev.craftsmanplus.com/api/{endpoint}'
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

# Function to poll the job poller lambda
def poll_job_poller(token, job_id, inference_id=None):
    try:
        url = f'https://ai.dev.craftsmanplus.com/api/jobs/{job_id}?job_type=scenario'
        if inference_id:
            url += f"&inference_id={inference_id}"
        response = requests.get(url, headers={"Authorization": token})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error polling job status: {e}")
        return None

# Sidebar menu
st.sidebar.title("Menu")
menu_option = st.sidebar.selectbox("Select an option", ["Home", "Playable Content Generator", "Variation Generator", "Inpainting"])

# Check authentication status
is_authenticated = st.session_state.get('is_authenticated', False)

# Display authentication status at the top
status_text = "Authenticated ✔️" if is_authenticated else "Not Authenticated ❌"
st.markdown(f"<p style='font-size: 16px; color: {'green' if is_authenticated else 'red'}'>{status_text}</p>", unsafe_allow_html=True)

# Streamlit UI
st.title("Content Generator")

if menu_option == "Home":
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

elif menu_option == "Playable Content Generator":
    # Generation Data section
    st.header("Generation Data")
    
    # Dropdown for template selection
    template = st.selectbox("Select Template", ["puzzle", "memory", "item catcher", "item slicer", "claw"])
    theme = st.text_input("Theme", value=st.session_state.get('theme', "wild west"))
    
    # Dropdown for style selection
    style = st.selectbox("Style", ["cartoon"])

    data = {
        "template": template,
        "theme": theme,
        "style": style
    }
    
    # Main focus button for generation
    if st.button("Generate Playable Content"):
        st.write("Please check the status in the Results tab.")
        if 'token' in st.session_state and theme and style:
            st.session_state.theme = theme
            st.session_state.style = style
            
            generation_response = start_generation(st.session_state.token, data, "playable/generate")
            if generation_response:
                st.success("Generated Job ID!")
                job_id = generation_response.get('id')
                location = generation_response.get('url')
                if job_id and location:
                    st.session_state.playable_job_id = job_id
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

elif menu_option == "Variation Generator":
    st.header("Variation Generator")
    
    # Input fields for variation generation
    image_url = st.text_input("Image URL", "https://cdn.cloud.scenario.com/assets-transform/asset_NSnpm8HMwP42rz2HeSEDsjJf?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uY2xvdWQuc2NlbmFyaW8uY29tL2Fzc2V0cy10cmFuc2Zvcm0vYXNzZXRfTlNucG04SE13UDQycnoySGVTRURzakpmPyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3MjM2Nzk5OTl9fX1dfQ__&Key-Pair-Id=K36FIAB9LE2OLR&Signature=vAHQf-wPgc0qNFNnR19ScWP1IoA6ts6n4AKjGdZcx~j0RgJi8GJ7jYRL9i4KZ00CRVNXHyMG1gdyTj-9~Idap3Djacbdkvn97b4iB6dbhFEbxuYPH2K3azcZODevvW2jL6CbcbEd2NSRutqo-pcvKDZNomGnU41WQHiDB8HWErylAODLO2Rcykiieb6Erh5oFwChnGJC90Gb~TqJWlKWCyuqttkXiT2OhlEYq46bh4zFMUs2sxQcV99wXG7mLInfyrjcmiWYejyeQn7oHXs7OHP5-ic9mz5Mej0Koiwz9zE~~k4QRhD9jlLAdNoi-R8fSAtunXlCNizK4tldyZm56g__&quality=80&format=jpeg&width=512")
    if image_url:
        st.image(image_url, width=200)
    prompt = st.text_input("Text Prompt", "rabbit")
    reference_urls = st.text_area("Reference Image URLs (comma-separated)", "").split(',')
    # Display previews of reference URLs
    for ref_url in reference_urls:
        if ref_url.strip():
            st.image(ref_url.strip(), width=200)

    if st.button("Generate Variation"):
        if 'token' in st.session_state and image_url and prompt:
            data = {
                "image": image_url,
                "prompt": prompt,
                "reference_images": [url.strip() for url in reference_urls if url.strip()]
            }
            variation_response = start_generation(st.session_state.token, data, "images/variation")
            if variation_response:
                st.success("Variation generation started!")
                job_id = variation_response.get('jobId')  # Get the job ID from the response
                if job_id:
                    st.session_state.variation_job_id = job_id
                    st.session_state.variation_phase = "IN_PROGRESS"
                    st.rerun()
                else:
                    st.error("Failed to retrieve job ID.")
            else:
                st.error("Failed to start variation generation process.")
        else:
            st.error("Please authenticate and fill in all fields!")

elif menu_option == "Inpainting":
    st.header("Inpainting")
    
    # Input fields for inpainting
    image_url = st.text_input("Image URL", "https://i.postimg.cc/J4s0w57t/red-girl.png")
    if image_url:
        st.image(image_url, width=200)
    prompt = st.text_input("Text Prompt", "a devil girl against a surreal, magical background with floating red and black islands, surrounded by dark swirling mist, glowing red crystals, and arcane symbols")
    mask_url = st.text_input("Mask URL", "https://i.postimg.cc/d3Xc8ffC/mask-0-resize.png")
    size_option = st.selectbox("Select image size", ["256x256", "512x512", "1024x1024"], index=2)
    if size_option == "256x256":
        size = "256x256"
    elif size_option == "512x512":
        size = "512x512"
    elif size_option == "1024x1024":
        size = "1024x1024"
    if mask_url:
        st.image(mask_url, width=200)
    if st.button("Generate Inpainting"):
        if 'token' in st.session_state and image_url and prompt and mask_url:
            data = {
                "image": image_url,
                "prompt": prompt,
                "mask": mask_url,
                "size": size
            }
            inpainting_response = start_generation(st.session_state.token, data, "images/edit")
            if inpainting_response:
                st.success("Inpainting generation started!")
                image_url = inpainting_response.get('imageUrl')
                st.session_state.inpainting_image_url = image_url
                # job_id = inpainting_response.get('jobId')
                # inference_id = inpainting_response.get('inferenceId')
                # if job_id and inference_id:
                #     st.session_state.inpainting_job_id = job_id
                #     st.session_state.inpainting_inference_id = inference_id
                #     st.session_state.inpainting_phase = "IN_PROGRESS"
                #     st.rerun()
                # else:
                #     st.error("Failed to retrieve job ID or inference ID.")
            else:
                st.error("Failed to start inpainting generation process.")
        else:
            st.error("Please authenticate and fill in all fields!")

# Results tab
if 'variation_job_id' in st.session_state:
    st.header("Variation Generation Results")
    job_id = st.session_state.variation_job_id

    # Check the status with a progress bar
    progress_bar = st.progress(st.session_state.get('progress', 0))
    status_placeholder = st.empty()
    if st.session_state.variation_phase not in ["success", "failure", "canceled"]:
        while True:
            status_response = poll_job_poller(st.session_state.token, job_id)
            if status_response:
                phase = status_response.get('phase')
                message = status_response.get('message')
                status_placeholder.write(f"Phase: {phase}\nMessage: {message}")
                st.session_state.variation_phase = phase
                st.session_state.progress = int(float(status_response.get('progress', 0)))
                progress_bar.progress(st.session_state.progress)
                if phase == 'success':
                    st.success("Variation generation completed!")
                    image_url = status_response.get('filepath')
                    if image_url:
                        st.image(image_url, caption="Generated Variation", width=500)
                    else:
                        st.error("Failed to retrieve image URL.")
                    break
                elif phase == 'failure' or phase == 'canceled':
                    st.error(f'Variation generation {phase}!')
                    break
                else:
                    time.sleep(2)
                    st.rerun()

# if 'inpainting_job_id' in st.session_state:
if 'inpainting_image_url' in st.session_state:
    st.header("Inpainting Generation Results")
    job_id = st.session_state.inpainting_job_id
    inference_id = st.session_state.inpainting_inference_id
    image_url = st.session_state.inpainting_image_url
    st.image(image_url, caption="Generated Inpainting", width=500)

    # Check the status with a progress bar
    progress_bar = st.progress(st.session_state.get('progress', 0))
    status_placeholder = st.empty()
    if st.session_state.inpainting_phase not in ["success", "failure", "canceled"]:
        while True:
            status_response = poll_job_poller(st.session_state.token, job_id, inference_id)
            if status_response:
                phase = status_response.get('phase')
                message = status_response.get('message')
                status_placeholder.write(f"Phase: {phase}\nMessage: {message}")
                st.session_state.inpainting_phase = phase
                st.session_state.progress = int(float(status_response.get('progress', 0)))
                progress_bar.progress(st.session_state.progress)
                if phase == 'success':
                    st.success("Inpainting generation completed!")
                    image_url = status_response.get('filepath')
                    if image_url:
                        st.image(image_url, caption="Generated Inpainting", width=500)
                    else:
                        st.error("Failed to retrieve image URL.")
                    break
                elif phase == 'failure' or phase == 'canceled':
                    st.error(f'Inpainting generation {phase}!')
                    break
                else:
                    time.sleep(2)
                    st.rerun()

# Results tab
if 'playable_job_id' in st.session_state:
    st.header("Generation Results")
    job_id = st.session_state.playable_job_id
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
                st.session_state.progress = int(float(status_response.get('progress', 0)))
                progress_bar.progress(st.session_state.progress)
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
                    if "prompt" in result:
                        st.info(f"{result['prompt']}")
                with cols_result[1]:
                    for url in result['urls']:
                        st.image(url, width=400)
            st.divider()
        try:
            st.subheader("Cost")
            st.write(f"Total Cost: {result_data['cost']['totalCost']} {result_data['cost']['currency']}")
            st.json(result_data['cost']['costBreakdown'])
        except:
            st.subheader("Cost (No Info)")
        st.subheader("JSON Results")
        st.json(result_data)
    # progress_bar = st.progress(st.session_state.get('progress', 0))
    # status_placeholder = st.empty()
    # if st.session_state.inpainting_phase not in ["success", "failure", "canceled"]:
    #     while True:
    #         status_response = poll_job_poller(st.session_state.token, job_id, inference_id)
    #         if status_response:
    #             phase = status_response.get('phase')
    #             message = status_response.get('message')
    #             status_placeholder.write(f"Phase: {phase}\nMessage: {message}")
    #             st.session_state.inpainting_phase = phase
    #             st.session_state.progress = int(float(status_response.get('progress', 0)))
    #             progress_bar.progress(st.session_state.progress)
    #             if phase == 'success':
    #                 st.success("Inpainting generation completed!")
    #                 image_url = status_response.get('filepath')
    #                 if image_url:
    #                     st.image(image_url, caption="Generated Inpainting", width=500)
    #                 else:
    #                     st.error("Failed to retrieve image URL.")
    #                 break
    #             elif phase == 'failure' or phase == 'canceled':
    #                 st.error(f'Inpainting generation {phase}!')
    #                 break
    #             else:
    #                 time.sleep(2)
    #                 st.rerun()
