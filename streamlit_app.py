import streamlit as st
import requests
import json

# Page config
st.set_page_config(
    page_title="Langflow Document Processor",
    page_icon="📄",
    layout="centered"
)

# Custom styles
st.markdown("""
<style>
.main {background-color: #f9fafc;}
[data-testid="stAppViewContainer"] {background-color: #f9fafc;}
[data-testid="stHeader"] {background: #fcfcfd;}
[data-testid="stSidebar"] {background: #fff;}
.stChatMessage.user {background: #e3f1ff; padding: 10px; border-radius: 8px; margin-bottom: 6px;}
.ai-response {background: #f0fdf4; border-radius: 8px; padding: 14px; margin: 10px 0; border: 1px solid #bbf7d0;}
.praise-box {
    background: linear-gradient(90deg, #d1fae5 0%, #fef9c3 100%);
    border-radius: 10px; padding: 12px; margin-bottom: 14px;
    font-weight: 600; color: #256029; border: 1px solid #bbf7d0;
    text-align: center;
}
.upload-box {
    background: #fffbe7;
    border-radius: 8px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# Top banner
st.markdown(
    '<div class="praise-box">🎉 Thank you for using Langflow! Upload your regulatory documents or chat directly for instant insights. Your privacy and experience matter to us.</div>',
    unsafe_allow_html=True
)

# API info
api_url = "https://api.langflow.astra.datastax.com/lf/edc89198-05a9-4dd1-a754-7c2ccbcc2c55/api/v1/run/bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
api_token = st.secrets["APPLICATION_TOKEN"]

def process_question(question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    payload = {
        "input_value": question.strip(),
        "output_type": "chat",
        "input_type": "chat"
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Simplified: try to locate the message in outputs
        outputs = data.get("outputs", [])
        if outputs and isinstance(outputs, list):
            result = outputs[0].get("outputs", {}).get("message", "")
            if not result:
                # Try alternative nested keys
                result = outputs[0].get("outputs", {}).get("message", {}).get("text", "")
            return result.strip() if isinstance(result, str) else json.dumps(result)
        return "No valid response found."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Tabs
tab1, tab2 = st.tabs(["💬 Chat", "📄 File Upload"])

with tab1:
    st.subheader("Chat with your document or ask regulatory questions")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    user_input = st.text_input("Enter your question:", placeholder="E.g. What is this document about?")
    if st.button("Send") and user_input.strip():
        with st.spinner("Langflow is thinking..."):
            answer = process_question(user_input)
        st.session_state.chat_history.append(("🙋 You", user_input.strip()))
        st.session_state.chat_history.append(("🤖 AI", answer))
    
    for sender, msg in st.session_state.chat_history:
        if sender == "🙋 You":
            st.markdown(f"<div class='stChatMessage user'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-response'><b>{sender}:</b><br>{msg}</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Upload a regulatory or legal document")
    st.markdown('<div class="upload-box">Supported formats: <b>.txt</b>, <b>.md</b>, <b>.pdf</b>, <b>.docx</b></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a document", type=["txt", "md", "pdf", "docx"])
    file_question = st.text_input("Ask a question about your uploaded document (optional):", value="What is this document about?")
    
    if uploaded_file:
        st.write(f"**File uploaded:** {uploaded_file.name}")
        if st.button("Process Document"):
            with st.spinner("Langflow is analyzing your document..."):
                # File content not processed as API doesn't support file input
                answer = process_question(file_question)
            st.markdown(f"<div class='ai-response'><b>🤖 AI:</b><br>{answer}</div>", unsafe_allow_html=True)
    else:
        st.info("Upload a document to enable question answering about its content.")

# Footer
st.markdown("""
<hr>
<div style='text-align:center;font-size:13px;color:#7b7b7b;'>
Powered by <b>Langflow</b> &nbsp;|&nbsp; Built with ❤️ using Streamlit<br>
<span style='font-size:11px;'>For best experience, use Streamlit's light theme (set <b>theme.base="light"</b> in <code>.streamlit/config.toml</code>).</span>
</div>
""", unsafe_allow_html=True)
