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
        {"id": 1, "type": "image", "urls": ["https://fastly.picsum.photos/id/839/536/354.jpg?hmac=rRPD5ORZY8xibjxZvrRUuUMfyc666vf0KQrPFOcZSJA"]},
        {"id": 2, "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/wxCzTlJhNPU/2024/05/14/20/1715718355061-K672yLeSICW__optimized.webp"
,"https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/wxCzTlJhNPU/2024/05/24/21/1716584971517-FunhnzEwM8U__optimized.webp"]},
        {"id": 3, "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/CRAFTSMAN/2023/11/27/12/1701087042485-uMqAGSq44Qk__optimized.webp"]},
        {"id": 4, "type": "image", "urls": ["https://endpoints.prod.craftsmanplus.com/assets/studio/optimized/CRAFTSMAN/2024/01/23/12/1706012086458-RHCTYkh6HZp__optimized.webp"]}
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



# Streamlit UI
st.title("Playable Content Generator")

# Create two columns for inputs and outputs
col1, col2 = st.columns(2)

with col1:
    # User Inputs for authentication
    st.header("User Authentication")
    email = st.text_input("Email", value=default_email)
    password = st.text_input("Password", type="password", value=default_password)
    client_id = default_client_id #st.text_input("Client ID", value=default_client_id)

    # User Inputs for data
    st.header("Generation Data")
    theme = st.text_input("Theme", value="""
I am creating a playable about a company called Craftsman+. It is set in a dystopian sci-fi environment where advertising rules the world.
""")

    if st.button("Add Asset"):
        st.session_state.assets.append({"id": len(st.session_state.assets) + 1, "type": "image", "urls": [""]})

    if st.button("Remove Last Asset") and len(st.session_state.assets) > 1:
        st.session_state.assets.pop()

    # Dynamic Asset Management
    st.header("Assets")
    for idx, asset in enumerate(st.session_state.assets):
        st.subheader(f"Asset {idx}")
        asset['id'] = idx + 1
        asset['type'] = st.text_input(f"Asset {idx + 1} Type", value=asset['type'], key=f"type_{idx}")
        asset['urls'] = st.text_area(f"Asset {idx + 1} URLs (one per line)", value="\n".join(asset['urls']), key=f"urls_{idx}").split('\n')
        for url in asset['urls']:
            try:
                st.image(url, width=200)
            except Exception as e:
                st.warning(f"Cannot display image for Asset {idx + 1} URL: {url}")



    # Display the assets
    st.write("Current Assets:")
    st.write(st.session_state.assets)

with col2:
    st.header("Generation Output")

    # Generate Playable Content
    if st.button("Generate Playable Content"):
        if email and password and client_id and theme:
            token = get_token(email, password, client_id)
            if token:
                st.success("Authenticated successfully!")

                data = {
                    "theme": theme,
                    "assets": st.session_state.assets
                }

                # Start the generation process
                generation_response = start_generation(token, data)
                if generation_response:
                    st.success("Generated Job ID!")
                    job_id = generation_response.get('id')
                    location = generation_response.get('url')

                    if job_id and location:
                        st.write(f"Job ID: {job_id}")
                        st.write("Generation started, checking status...")

                        # Check the status with a progress bar
                        progress_bar = st.progress(0)
                        status_placeholder = st.empty()

                        while True:
                            status_response = check_status(token, job_id)
                            if status_response:
                                status_placeholder.write(status_response)
                                if status_response['phase'] == 'COMPLETED':
                                    st.success("Generation completed!")
                                    result_data = download_result(location)
                                    if result_data:
                                        st.json(result_data)
                                        for asset in result_data['assets']:
                                            for result in asset['results']:
                                                st.write(f"Prompt: {result['prompt']}")
                                                for url in result['urls']:
                                                    st.image(url, caption=result['prompt'])
                                        st.write(f"Total Cost: {result_data['cost']['totalCost']} {result_data['cost']['currency']}")
                                        st.json(result_data['cost']['costBreakdown'])
                                    break
                                elif status_response['phase'] == 'FAILED':
                                    st.error("Generation failed!")
                                    st.write(status_response.get('message'))
                                    break
                                else:
                                    progress_bar.progress(status_response.get('progress', 0) / 100)
                                    time.sleep(5)
                                    status_placeholder.empty()
                    else:
                        st.error("Failed to retrieve job ID or location URL.")
                else:
                    st.error("Failed to start generation process.")
        else:
            st.error("Please fill all the fields!")

