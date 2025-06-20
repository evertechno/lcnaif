import streamlit as st
import requests

st.set_page_config(page_title="Langflow Document Processor", page_icon="📄", layout="centered")
st.markdown(
    """
    <style>
    .main {background-color: #f9fafc;}
    .stChatMessage.user {background: #e3f1ff;}
    .stChatMessage.ai {background: #f5f5f5;}
    .ai-response {background: #f6f8fa; border-radius: 8px; padding: 16px; margin-top: 10px;}
    .praise-box {
        background: linear-gradient(90deg, #d1fae5 0%, #fef9c3 100%);
        border-radius: 10px; padding: 12px; margin-bottom: 14px;
        font-weight: 600; color: #256029; border: 1px solid #bbf7d0;
        text-align: center;
    }
    .upload-box {background: #fffbe7; border-radius: 8px; padding: 10px;}
    </style>
    """, unsafe_allow_html=True
)

# Praising note
st.markdown('<div class="praise-box">🎉 Thank you for using Langflow! Upload your regulatory documents or chat directly for instant insights. Your privacy and experience matter to us.</div>', unsafe_allow_html=True)

api_url = "https://api.langflow.astra.datastax.com/lf/edc89198-05a9-4dd1-a754-7c2ccbcc2c55/api/v1/run/bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
api_token = st.secrets["APPLICATION_TOKEN"]

def process_question(question):
    payload = {
        "input_value": question.strip(),
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
        data = response.json()
        # Try to extract the message cleanly
        message = ""
        # Check for several possible keys
        if isinstance(data, dict):
            possible_keys = [
                ("outputs", 0, "outputs", 0, "results", "message", "text"),
                ("outputs", 0, "outputs", 0, "results", "message", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message", "text"),
                ("outputs", 0, "outputs", 0, "outputs", "message"),
                ("outputs", 0, "outputs", 0, "outputs"),
                ("outputs", 0, "outputs", 0, "results", "message", "data", "text"),
                ("outputs", 0, "outputs", 0, "results", "message", "data", "message"),
                ("outputs", 0, "outputs", 0, "results", "message"),
                ("outputs", 0, "outputs", 0, "artifacts", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message", "message"),
                ("outputs", 0, "outputs", 0, "outputs", "message", "text"),
            ]
            # Try each key path
            for keys in possible_keys:
                try:
                    temp = data
                    for k in keys:
                        if isinstance(k, int):
                            temp = temp[k]
                        else:
                            temp = temp.get(k)
                    if isinstance(temp, str) and temp.strip():
                        message = temp
                        break
                except Exception:
                    continue
        # Fallback: try to get first string value in the dict
        if not message:
            import json
            text_values = [v for v in str(data).split("\\n") if v.strip()]
            message = text_values[0] if text_values else ""
        return message.strip()
    except Exception as e:
        return f"❌ Error: {e}"

tab1, tab2 = st.tabs(["💬 Chat", "📄 File Upload"])

with tab1:
    st.subheader("Chat with your document or ask regulatory questions")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    user_input = st.text_input(
        "Enter your question:",
        key="chat_input",
        placeholder="E.g. What is this document about?",
    )
    send_btn = st.button("Send", key="chat_send", help="Send your question to Langflow")
    if send_btn and user_input.strip():
        with st.spinner("Langflow is thinking..."):
            response = process_question(user_input)
        st.session_state["chat_history"].append(("You", user_input.strip()))
        st.session_state["chat_history"].append(("AI", response))
    for sender, msg in st.session_state["chat_history"]:
        if sender == "You":
            st.markdown(f"<div class='stChatMessage user'><b>🙋 {sender}:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            if msg.strip():
                st.markdown(f"<div class='ai-response'><b>🤖 {sender}:</b><br>{msg}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Upload a regulatory or legal document")
    st.markdown('<div class="upload-box">Supported formats: <b>.txt</b>, <b>.md</b>, <b>.pdf</b>, <b>.docx</b></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a document", type=["txt", "md", "pdf", "docx"])
    file_question = st.text_input(
        "Ask a question about your uploaded document (optional):",
        "What is this document about?",
        key="file_input"
    )
    if uploaded_file:
        st.write(f"**File uploaded:** {uploaded_file.name}")
        if st.button("Process Document", key="file_send"):
            with st.spinner("Langflow is analyzing your document..."):
                # NOTE: The API currently does not support direct file uploads.
                # For demonstration, only the question is sent.
                output = process_question(file_question)
            st.subheader("Langflow's Response:")
            if output.strip():
                st.markdown(f"<div class='ai-response'>{output}</div>", unsafe_allow_html=True)
            else:
                st.info("No content was returned by the API. Try a different question or check your document.")
    else:
        st.info("Upload a document to enable question answering about its content.")

# Footer for professional touch
st.markdown(
    """
    <hr>
    <div style='text-align:center;font-size:13px;color:#7b7b7b;'>
        Powered by <b>Langflow</b> &nbsp;|&nbsp; Built with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True
)
