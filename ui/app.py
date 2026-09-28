import streamlit as st
import os
import sys
import tempfile

# Add the project root to the Python path so we can import from other folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import init_db
from db.feedback_store import init_feedback_db, log_feedback
from rag.ingest import ingest_pdf_file
from agent.enterprise_agent import run_enterprise_pipeline

st.set_page_config(page_title="Enterprise Agentic RAG", layout="wide")

# Initialize databases on startup
@st.cache_resource
def setup_databases():
    init_db()
    init_feedback_db()
    return True

setup_databases()

# Simulated SSO Data
USERS = {
    "Employee": {
        "EMP101": "Alice Smith",
        "EMP102": "Bob Jones",
        "EMP103": "Charlie Brown"
    },
    "HR": {
        "HR201": "Diana Prince",
        "HR202": "Clark Kent"
    }
}

# -----------------
# Sidebar
# -----------------
with st.sidebar:
    st.header("Simulated SSO")
    user_role = st.selectbox("Select Role", ["Employee", "HR"])
    
    available_users = USERS[user_role]
    selected_emp_code = st.selectbox("Select User", list(available_users.keys()))
    auth_emp_name = available_users[selected_emp_code]
    st.write(f"Logged in as: **{auth_emp_name}** ({user_role})")
    
    st.divider()
    
    if user_role == "HR":
        st.header("Knowledge Base Management")
        uploaded_files = st.file_uploader("Upload Policy PDFs", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            if len(uploaded_files) < 10:
                st.info("You requested to process a minimum of 10 PDFs at a time. Please upload more files.")
            if st.button(f"Ingest {len(uploaded_files)} Document(s)"):
                with st.spinner(f"Ingesting {len(uploaded_files)} document(s) to Pinecone..."):
                    success_count = 0
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        try:
                            # Pass the original filename to maintain clean metadata
                            ingest_pdf_file(tmp_path, original_filename=uploaded_file.name)
                            success_count += 1
                        except Exception as e:
                            st.error(f"Error ingesting {uploaded_file.name}: {str(e)}")
                        finally:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                    
                    if success_count > 0:
                        st.success(f"Successfully ingested {success_count} document(s)!")

# -----------------
# Main Chat
# -----------------
st.title("Enterprise AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        # Feedback UI for assistant messages
        if msg["role"] == "assistant" and idx > 0:
            col1, col2, col3 = st.columns([1, 1, 10])
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    log_feedback(st.session_state.messages[idx-1]["content"], msg["content"], 1, "")
                    st.toast("Positive feedback logged!")
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state[f"show_feedback_form_{idx}"] = True
                    
            if st.session_state.get(f"show_feedback_form_{idx}", False):
                with st.form(key=f"feedback_form_{idx}"):
                    notes = st.text_input("What was wrong with this response?", key=f"notes_{idx}")
                    submit_feedback = st.form_submit_button("Submit Correction")
                    if submit_feedback:
                        log_feedback(st.session_state.messages[idx-1]["content"], msg["content"], -1, notes)
                        st.success("Correction learned! This will be incorporated into future responses.")
                        st.session_state[f"show_feedback_form_{idx}"] = False
                        st.rerun()

# -----------------
# Chat Input
# -----------------
if prompt := st.chat_input("Ask me about company policies or your employment records..."):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user's message immediately!
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate and stream the assistant's response
    with st.chat_message("assistant"):
        response = st.write_stream(run_enterprise_pipeline(prompt, selected_emp_code, auth_emp_name))
            
    # Store response and rerun to update UI with feedback buttons
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
