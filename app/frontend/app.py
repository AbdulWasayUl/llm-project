import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Change if your backend URL differs

st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("💬 RAG Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# === Sidebar: File upload and QA/Context selection ===
st.sidebar.header("📄 Upload Data")

uploaded_file = st.sidebar.file_uploader("Upload a file", type=["pdf", "txt", "docx", "xlsx"])
is_qa = st.sidebar.radio("Select data type", options=["QA Pairs", "Context"]) == "QA Pairs"

if uploaded_file:
    is_word = uploaded_file.name.endswith(".docx")

    if is_qa and is_word:
        st.sidebar.error("❌ Word documents are not allowed for QA mode.")
    else:
        if st.sidebar.button("📤 Upload to RAG", use_container_width=True):
            with st.spinner("Uploading file..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                data = {"is_qa": str(is_qa).lower()}  # send as 'true' or 'false' string
                try:
                    response = requests.post(f"{API_URL}/add_data", files=files, data=data)
                    if response.status_code == 200:
                        st.sidebar.success("✅ File uploaded successfully.")
                    else:
                        st.sidebar.error(f"❌ Failed to upload the file: {response.text}")
                except Exception as e:
                    st.sidebar.error(f"❌ Error during upload: {e}")

# === Chat interface ===
st.subheader("🧠 Ask the RAG LLM")

# Display chat messages
for i, msg in enumerate(st.session_state.messages):
    role = msg["role"]  # 'user' or 'assistant'
    with st.chat_message(role):
        st.markdown(msg["content"])

# Input new user message with send button
new_message = st.chat_input("Type your message here...")

if new_message:
    # Add user message instantly
    st.session_state.messages.append({"role": "user", "content": new_message})
    with st.chat_message("user"):
        st.markdown(new_message)

    # Query the backend
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                res = requests.post(f"{API_URL}/ask", json={"query": new_message})
                if res.status_code == 200:
                    answer = res.json().get("response", "No response content.")
                else:
                    answer = f"❌ Error: {res.status_code} - {res.text}"
            except Exception as e:
                answer = f"❌ Could not reach the backend: {e}"

            st.markdown(answer)
            # Save assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})