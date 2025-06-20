import streamlit as st
import requests
import json

# Title and description
st.title("Langflow Document Processor")
st.write(
    """
    Upload a document and interact with it using the Langflow API.
    Your API token is securely loaded from Streamlit secrets.
    """
)

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf", "docx"])

# Optional: User input for chat
user_query = st.text_input("Ask a question about your document:", "What is this document about?")

# Load API token from Streamlit secrets
api_token = st.secrets["APPLICATION_TOKEN"]  # Add APPLICATION_TOKEN to your .streamlit/secrets.toml

# API endpoint URL (as per your sample)
api_url = "https://api.langflow.astra.datastax.com/lf/edc89198-05a9-4dd1-a754-7c2ccbcc2c55/api/v1/run/bdb15b27-ac48-4581-9a9c-bb9eb3299e08"

def process_document(file_bytes, question):
    # Prepare the payload, assuming the API expects file content as part of input_value
    # You may need to change this if the API expects a different structure
    payload = {
        "input_value": question,
        "output_type": "chat",
        "input_type": "chat"
    }
    # If API supports file content in input_value, you could do:
    # payload['input_value'] = file_bytes.decode(errors="ignore") + "\n" + question

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error making API request: {e}"
    except ValueError as e:
        return f"Error parsing response: {e}"

if uploaded_file:
    file_bytes = uploaded_file.read()
    st.write("File uploaded:", uploaded_file.name)
    if st.button("Process Document"):
        with st.spinner("Processing..."):
            # You may want to update this to send file content depending on your API's requirements
            output = process_document(file_bytes, user_query)
        st.subheader("API Response:")
        st.write(output)
else:
    st.info("Please upload a document to begin.")
