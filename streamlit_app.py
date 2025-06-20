import streamlit as st
import requests
import os

# Title and description
st.title("Langflow Document Processor")
st.write(
    """
    Upload a document OR chat about your document using the Langflow API.
    Your API token is securely loaded from Streamlit secrets.
    """
)

# Sidebar for API Token status (optional)
with st.sidebar:
    st.markdown("### API Token Status")
    if "APPLICATION_TOKEN" in st.secrets:
        st.success("API Token Loaded")
    else:
        st.error("API Token not found in secrets!")

# API endpoint URL
api_url = "https://api.langflow.astra.datastax.com/lf/edc89198-05a9-4dd1-a754-7c2ccbcc2c55/api/v1/run/bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
api_token = st.secrets["APPLICATION_TOKEN"]

# Tabs for "Chat" and "File Upload"
tab1, tab2 = st.tabs(["💬 Chat", "📄 File Upload"])

def process_question(question):
    payload = {
        "input_value": question,
        "output_type": "chat",
        "input_type": "chat"
    }
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

with tab1:
    st.subheader("Chat Interface")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    user_input = st.text_input("Enter your question:", key="chat_input")
    if st.button("Send", key="chat_send") and user_input:
        with st.spinner("Processing..."):
            response = process_question(user_input)
        st.session_state["chat_history"].append(("You", user_input))
        st.session_state["chat_history"].append(("Langflow", response))
    # Display chat history
    for sender, msg in st.session_state["chat_history"]:
        if sender == "You":
            st.markdown(f"**{sender}:** {msg}")
        else:
            st.markdown(f"<div style='background:#f0f2f6; padding:8px; border-radius:6px; margin-bottom:5px;'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("File Upload")
    uploaded_file = st.file_uploader("Upload a document", type=["txt", "md", "pdf", "docx"])
    file_question = st.text_input("Ask a question about your document (optional):", "What is this document about?", key="file_input")
    if uploaded_file:
        file_bytes = uploaded_file.read()
        st.write("File uploaded:", uploaded_file.name)
        # For demonstration, we just use the question, not file content, in API call.
        # To actually process file content, API should support it.
        if st.button("Process Document", key="file_send"):
            with st.spinner("Processing..."):
                output = process_question(file_question)
            st.subheader("API Response:")
            st.write(output)
    else:
        st.info("Please upload a document to begin.")
