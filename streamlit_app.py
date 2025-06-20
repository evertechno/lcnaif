import streamlit as st
import requests

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
            color: #333;
            font-family: "Segoe UI", sans-serif;
        }
        .stAlert {
            background-color: #e0f7fa !important;
            border-left: 5px solid #00bcd4;
            margin-bottom: 1em;
        }
        footer {
            text-align: center;
            font-size: 0.8em;
            color: #888;
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("📄 Langflow Document Analyzer")

# --- Praise Message ---
st.success("🎉 Thank you for using our app! Upload your document or enter text to get started.")

# --- Input Options ---
st.sidebar.header("🔧 Settings")
input_method = st.sidebar.radio("Input Method", ("Upload File", "Enter Text"))

input_text = ""
if input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md", "csv"])
    if uploaded_file:
        file_contents = uploaded_file.read().decode("utf-8")
        input_text = file_contents.strip()
elif input_method == "Enter Text":
    input_text = st.text_area("Enter your text here")

# --- Analyze Button ---
if st.button("🔍 Analyze"):
    if input_text.strip():
        url = "https://api.langflow.astra.datastax.com/lf/edc89198-05a9-4dd1-a754-7c2ccbcc2c55/api/v1/run/bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.secrets['API_TOKEN']}"
        }
        payload = {
            "input_value": input_text,
            "output_type": "chat",
            "input_type": "chat"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result_json = response.json()

            output = result_json.get("output", "").strip()
            if output:
                st.subheader("📤 AI Response")
                st.code(output, language="text")
            else:
                st.warning("⚠️ The response was empty or contained only whitespace.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API Request failed: {e}")
        except ValueError as e:
            st.error(f"❌ Error parsing response: {e}")
    else:
        st.warning("⚠️ Please upload a file or enter some text.")

# --- Footer ---
st.markdown("---")
st.markdown("<footer>Langflow Streamlit Frontend © 2025</footer>", unsafe_allow_html=True)
