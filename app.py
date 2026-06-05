import streamlit as st
import httpx
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Base configurations
API_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="Secure Enterprise Knowledge Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Premium font style */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header card design */
    .header-card {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }
    
    /* Metric container styling */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 4px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tag styles */
    .role-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .role-admin { background-color: #ef4444; color: white; }
    .role-hr { background-color: #ec4899; color: white; }
    .role-finance { background-color: #10b981; color: white; }
    .role-engineering { background-color: #3b82f6; color: white; }
    .role-compliance { background-color: #f59e0b; color: white; }
    
    /* Access level tags */
    .access-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .access-public { background-color: #22c55e; color: white; }
    .access-internal { background-color: #64748b; color: white; }
    .access-confidential { background-color: #eab308; color: black; }
    .access-restricted { background-color: #9333ea; color: white; }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "department" not in st.session_state:
    st.session_state.department = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def logout_user():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.department = None
    st.session_state.chat_history = []
    st.rerun()

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ----------------- LOGIN PAGE -----------------
if not st.session_state.token:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #6366f1; font-size: 2.8rem; font-weight: 700; margin-bottom: 10px;'>
                🛡️ Secure Enterprise Knowledge Assistant
            </h1>
            <p style='color: #94a3b8; font-size: 1.1rem;'>
                AI Knowledge Engine & Secure Role-Based Access Control
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        login_tab, demo_tab = st.tabs(["🔐 Standard Login", "🚀 Quick Demo Profiles"])
        
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        try:
                            res = httpx.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.token = data["access_token"]
                                st.session_state.username = data["username"]
                                st.session_state.role = data["role"]
                                st.session_state.department = data["department"]
                                st.success(f"Logged in as {username}!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Incorrect username or password")
                        except Exception as e:
                            st.error(f"Cannot connect to Backend API. Please ensure it is running on port 8000. Error: {e}")
        
        with demo_tab:
            st.info("Click one of the profiles below to immediately bypass manual login and experience the platform with that role's clearance.")
            profiles = [
                {"name": "Administrator (Full Access)", "user": "admin", "pwd": "admin123", "role": "Admin", "dept": "General"},
                {"name": "HR Specialist (HR and Handbook)", "user": "alice", "pwd": "alice123", "role": "HR", "dept": "HR"},
                {"name": "Finance Analyst (Revenue & Projections)", "user": "bob", "pwd": "bob123", "role": "Finance", "dept": "Finance"},
                {"name": "Software Engineer (Coding & Repos)", "user": "charlie", "pwd": "charlie123", "role": "Engineering", "dept": "Engineering"},
                {"name": "Compliance Officer (Logs & Audits)", "user": "david", "pwd": "david123", "role": "Compliance", "dept": "Security"}
            ]
            
            for p in profiles:
                if st.button(p["name"], use_container_width=True):
                    try:
                        res = httpx.post(f"{API_URL}/auth/login", json={"username": p["user"], "password": p["pwd"]})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.username = data["username"]
                            st.session_state.role = data["role"]
                            st.session_state.department = data["department"]
                            st.success(f"Bypassed login. Acting as {p['role']} User.")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"Seeding issue. Standard login credentials for user {p['user']} failed.")
                    except Exception as e:
                        st.error(f"Backend API offline. Run: python main.py. Error: {e}")
    st.stop()

# ----------------- MAIN LAYOUT -----------------

# Header Section
st.markdown(f"""
<div class="header-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">🛡️ Secure Enterprise Knowledge Assistant</h2>
            <p style="margin: 0; opacity: 0.85; font-size: 0.95rem;">Secure Information Intelligence Dashboard</p>
        </div>
        <div style="text-align: right;">
            <span style="font-weight: 600; font-size: 1.1rem; color: #F8FAFC;">Active Session: {st.session_state.username}</span>
            <div style="margin-top: 4px;">
                <span class="role-tag role-{st.session_state.role.lower()}">{st.session_state.role}</span>
                <span style="background-color: #334155; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; margin-left: 5px;">Dept: {st.session_state.department}</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='margin-bottom: 10px; font-weight:600;'>🧭 Platform Navigation</h3>", unsafe_allow_html=True)
    page = st.radio(
        "Select Screen",
        [
            "💬 Chat Assistant",
            "📂 Document Manager",
            "👥 User Management",
            "🛡️ Access Control Matrix",
            "📊 Retrieval Analytics",
            "📜 Security Audit Logs",
            "⚙️ System Performance"
        ]
    )
    
    st.markdown("<hr style='margin: 20px 0;'/>", unsafe_allow_html=True)
    
    # Active user role info
    st.markdown(f"""
    <div style='background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155;'>
        <h5 style='margin-top:0; color:#cbd5e1; font-weight:600;'>Clearance Info</h5>
        <p style='font-size:0.8rem; color:#94a3b8; margin-bottom:5px;'>Your role is granted access based on the following security permissions:</p>
        <ul style='font-size:0.8rem; color:#cbd5e1; margin-left:-10px; margin-bottom:0;'>
            <li>Public Documents: Yes</li>
            <li>Internal Documents: Yes</li>
            <li>Confidential: {'Yes (HR/Finance/Admin)' if st.session_state.role in ['Admin', 'HR', 'Finance'] else 'Only Own Department'}</li>
            <li>Restricted: {'Yes (Admin/Finance/Compliance)' if st.session_state.role in ['Admin', 'Finance', 'Compliance'] else 'No'}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True):
        logout_user()

# ----------------- PAGE 1: CHAT ASSISTANT -----------------
if page == "💬 Chat Assistant":
    st.subheader("💬 AI Enterprise Assistant")
    
    # Render chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "trace" in msg and msg["trace"]:
                trace = msg["trace"]
                with st.expander("🔍 Explainability & Retrieval Trace"):
                    # Display trace breakdown
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**Routed Intent**: `{trace['routing_intent']}`")
                        st.markdown(f"**Confidence Score**: `{trace['confidence_score'] * 100:.1f}%`")
                    with c2:
                        st.markdown(f"**Execution Path**: `{trace['execution_path']}`")
                        st.markdown(f"**Execution Latency**: `{trace['execution_time_ms']:.1f} ms`")
                    with c3:
                        st.markdown(f"**Hallucination Check**: `{trace.get('hallucination_check', 'N/A')}`")
                        st.markdown(f"**LLM Synthesizer**: `{trace.get('llm_provider_used', 'N/A')}`")
                        
                    st.markdown("**Retrieved Knowledge Chunks:**")
                    if "chunks" in msg and msg["chunks"]:
                        for idx, chunk in enumerate(msg["chunks"]):
                            st.markdown(f"""
                            <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-weight: 600; font-size: 0.8rem; color:#6366f1;">[{idx+1}] {chunk['metadata']['filename']}</span>
                                    <span style="background-color: #2e3c54; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;">Chunk: {chunk['metadata']['chunk_id']} | Score: {chunk['score']:.3f}</span>
                                </div>
                                <p style="font-size: 0.82rem; margin: 0; color:#cbd5e1; white-space: pre-wrap;">{chunk['content']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No chunks retrieved.")
                        
    # Chat Input
    query = st.chat_input("Ask a question about HR, Finance, Coding, or Security logs...")
    
    if query:
        # Display user question
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        # Call API
        with st.chat_message("assistant"):
            with st.spinner("Analyzing request and checking security clearance..."):
                try:
                    res = httpx.post(f"{API_URL}/chat", json={"query": query}, headers=get_headers(), timeout=60.0)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        trace = data.get("trace", {})
                        chunks = data.get("chunks", [])
                        
                        st.markdown(answer)
                        
                        # Add explainability expander
                        with st.expander("🔍 Explainability & Retrieval Trace"):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.markdown(f"**Routed Intent**: `{trace.get('routing_intent', 'N/A')}`")
                                st.markdown(f"**Confidence Score**: `{trace.get('confidence_score', 0.0) * 100:.1f}%`")
                            with c2:
                                st.markdown(f"**Execution Path**: `{trace.get('execution_path', 'N/A')}`")
                                st.markdown(f"**Execution Latency**: `{trace.get('execution_time_ms', 0.0):.1f} ms`")
                            with c3:
                                st.markdown(f"**Hallucination Check**: `{trace.get('hallucination_check', 'N/A')}`")
                                st.markdown(f"**LLM Synthesizer**: `{trace.get('llm_provider_used', 'N/A')}`")
                                
                            st.markdown("**Retrieved Knowledge Chunks:**")
                            if chunks:
                                for idx, chunk in enumerate(chunks):
                                    st.markdown(f"""
                                    <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 8px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <span style="font-weight: 600; font-size: 0.8rem; color:#6366f1;">[{idx+1}] {chunk['metadata']['filename']}</span>
                                            <span style="background-color: #2e3c54; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;">Chunk: {chunk['metadata']['chunk_id']} | Score: {chunk['score']:.3f}</span>
                                        </div>
                                        <p style="font-size: 0.82rem; margin: 0; color:#cbd5e1; white-space: pre-wrap;">{chunk['content']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.write("No chunks retrieved.")
                                
                        # Save in session state
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "trace": trace,
                            "chunks": chunks
                        })
                    else:
                        error_detail = res.json().get("detail", "Failed to get response")
                        st.error(f"Error ({res.status_code}): {error_detail}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

# ----------------- PAGE 2: DOCUMENT MANAGER -----------------
elif page == "📂 Document Manager":
    st.subheader("📂 Document Management Pipeline")
    
    # 2 columns layout: Uplader on left, List on right
    c_upload, c_list = st.columns([1, 2])
    
    with c_upload:
        st.markdown("""
        <div style='background-color:#1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155;'>
            <h4 style='margin-top:0; color:#fff; font-weight:600;'>Upload & Ingest File</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Check permissions: Admin, HR, Compliance can upload
        if st.session_state.role not in ["Admin", "HR", "Compliance"]:
            st.warning("🔒 Uploading new documents requires Admin, HR, or Compliance role privileges.")
        else:
            with st.form("upload_form", clear_on_submit=True):
                uploaded_file = st.file_uploader("Select File", type=["pdf", "csv", "json", "txt"])
                department = st.selectbox("Department Tag", ["HR", "Finance", "Engineering", "Security", "Legal", "General"])
                access_level = st.selectbox("Access Level", ["Public", "Internal", "Confidential", "Restricted"])
                
                # Checkbox for Allowed Roles
                st.write("Allowed Roles (for Confidential/Restricted)")
                allowed_admin = st.checkbox("Admin", value=True, disabled=True)
                allowed_hr = st.checkbox("HR", value=True if department == "HR" else False)
                allowed_finance = st.checkbox("Finance", value=True if department == "Finance" else False)
                allowed_eng = st.checkbox("Engineering", value=True if department == "Engineering" else False)
                allowed_comp = st.checkbox("Compliance", value=True if department == "Security" or department == "Legal" else False)
                
                submit = st.form_submit_button("Start Ingestion Pipeline", use_container_width=True)
                
                if submit:
                    if not uploaded_file:
                        st.error("Please select a file to upload.")
                    else:
                        # Build allowed roles list
                        roles = ["Admin"]
                        if allowed_hr: roles.append("HR")
                        if allowed_finance: roles.append("Finance")
                        if allowed_eng: roles.append("Engineering")
                        if allowed_comp: roles.append("Compliance")
                        
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {
                            "department": department,
                            "access_level": access_level,
                            "allowed_roles": json.dumps(roles)
                        }
                        
                        with st.spinner(f"Parsing and indexing {uploaded_file.name}..."):
                            try:
                                res = httpx.post(f"{API_URL}/documents", files=files, data=data, headers=get_headers())
                                if res.status_code == 201:
                                    st.success(f"Success! {uploaded_file.name} ingested into FAISS and metadata DB.")
                                    time.sleep(1.0)
                                    st.rerun()
                                else:
                                    st.error(f"Failed to ingest: {res.json().get('detail')}")
                            except Exception as e:
                                st.error(f"Server connection error: {e}")
                                
    with c_list:
        st.markdown("""
        <div style='background-color:#1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 15px;'>
            <h4 style='margin-top:0; color:#fff; font-weight:600;'>Ingested Core Enterprise Files</h4>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            res = httpx.get(f"{API_URL}/documents", headers=get_headers())
            if res.status_code == 200:
                docs = res.json()
                if not docs:
                    st.info("No documents are ingested yet.")
                else:
                    # Renders beautiful grid list
                    for doc in docs:
                        c_info, c_action = st.columns([4, 1])
                        
                        # Generate HTML for tag styling
                        r_tags = " ".join([f"<span class='role-tag role-{r.lower()}'>{r}</span>" for r in doc["allowed_roles"]])
                        a_class = f"access-{doc['access_level'].lower()}"
                        
                        with c_info:
                            st.markdown(f"""
                            <div style="background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-weight: 700; font-size: 1.05rem; color:#f8fafc;">📄 {doc['filename']}</span>
                                    <span class="access-tag {a_class}">{doc['access_level']}</span>
                                </div>
                                <div style="font-size:0.8rem; color:#94a3b8; margin-bottom: 6px;">
                                    ID: {doc['document_id']} | Type: <b>{doc['source_type'].upper()}</b> | Dept: <b>{doc['department']}</b> | Owner: <b>{doc['owner']}</b>
                                </div>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span style="font-size:0.75rem; color:#94a3b8;">Access Clearance:</span>
                                    {r_tags}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with c_action:
                            st.write("") # Padding
                            st.write("")
                            if st.session_state.role != "Admin":
                                st.button("❌ Remove", key=f"del_{doc['document_id']}", disabled=True, use_container_width=True, help="Deletion requires Admin privileges.")
                            else:
                                if st.button("❌ Remove", key=f"del_{doc['document_id']}", use_container_width=True):
                                    with st.spinner("Removing document & rebuilding indexes..."):
                                        res_del = httpx.delete(f"{API_URL}/documents/{doc['document_id']}", headers=get_headers())
                                        if res_del.status_code == 200:
                                            st.success("Deleted!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error("Delete failed.")
            else:
                st.error("Failed to load documents list.")
        except Exception as e:
            st.error(f"Cannot query database: {e}")

# ----------------- PAGE 3: USER MANAGEMENT -----------------
elif page == "👥 User Management":
    st.subheader("👥 User Account & Role Configuration")
    
    if st.session_state.role != "Admin":
        st.warning("🔒 User management operations are restricted to Administrators.")
        st.stop()
        
    c_add, c_list = st.columns([1, 2])
    
    with c_add:
        st.markdown("<h4 style='font-weight:600;'>Create User</h4>", unsafe_allow_html=True)
        with st.form("create_user_form", clear_on_submit=True):
            new_user = st.text_input("Username")
            new_pwd = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "HR", "Finance", "Engineering", "Compliance"])
            new_dept = st.selectbox("Department", ["HR", "Finance", "Engineering", "Security", "Legal", "General"])
            
            sub = st.form_submit_button("Add User", use_container_width=True)
            if sub:
                if not new_user or not new_pwd:
                    st.error("Fill in all fields.")
                else:
                    res = httpx.post(
                        f"{API_URL}/users", 
                        json={"username": new_user, "password": new_pwd, "role": new_role, "department": new_dept},
                        headers=get_headers()
                    )
                    if res.status_code == 201:
                        st.success(f"User {new_user} added successfully.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Error creating user"))
                        
    with c_list:
        st.markdown("<h4 style='font-weight:600;'>Active Accounts</h4>", unsafe_allow_html=True)
        try:
            res = httpx.get(f"{API_URL}/users", headers=get_headers())
            if res.status_code == 200:
                users = res.json()
                
                # Render table
                for u in users:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**👤 {u['username']}**")
                    with col2:
                        st.markdown(f"<span class='role-tag role-{u['role'].lower()}'>{u['role']}</span> (Dept: {u['department']})", unsafe_allow_html=True)
                    with col3:
                        # Allow modifying role
                        if u["username"] == "admin":
                            st.write("System")
                        else:
                            # Quick delete or modify mock placeholder
                            # Since we want to make it look premium, show edit triggers
                            st.write("Active")
                    st.markdown("<hr style='margin: 8px 0; border-color: #2e3c54;'/>", unsafe_allow_html=True)
            else:
                st.error("Failed to load users.")
        except Exception as e:
            st.error(f"Database error: {e}")

# ----------------- PAGE 4: ACCESS CONTROL MATRIX -----------------
elif page == "🛡️ Access Control Matrix":
    st.subheader("🛡️ Enterprise RBAC Access Control Matrix")
    
    st.markdown("""
    The Secure Enterprise Knowledge Assistant enforces strict pre-retrieval filters. 
    Restricted data coordinates are removed from queries before vector matching is computed, preventing authorization leakage in LLM contexts.
    """)
    
    # Render matrix table
    matrix_data = {
        "Document Access Level": ["🔓 Public", "🏢 Internal", "🛡️ Confidential", "🚫 Restricted"],
        "Admin Clearance": ["✅ Authorized", "✅ Authorized", "✅ Authorized", "✅ Authorized"],
        "HR Clearance": ["✅ Authorized", "✅ Authorized", "✅ Authorized (HR Dept / Allowed Roles)", "❌ Denied"],
        "Finance Clearance": ["✅ Authorized", "✅ Authorized", "✅ Authorized (Finance Dept / Allowed Roles)", "✅ Authorized (Only if in Allowed Roles)"],
        "Engineering Clearance": ["✅ Authorized", "✅ Authorized", "✅ Authorized (Engineering Dept / Allowed Roles)", "❌ Denied"],
        "Compliance Clearance": ["✅ Authorized", "✅ Authorized", "✅ Authorized (Legal/Security Dept / Allowed)", "✅ Authorized (Only if in Allowed Roles)"]
    }
    
    df_matrix = pd.DataFrame(matrix_data)
    st.table(df_matrix.set_index("Document Access Level"))
    
    # Policies Breakdown
    st.markdown("### 🔍 Technical Security Enforcement Details")
    st.info("""
    **Pre-retrieval Vector Filtering Hook**:
    When a user queries the model, their user details are checked. 
    A SQL query resolves their authorized `document_ids` based on their role and department.
    These document IDs are passed as a filter constraint directly into the FAISS indexing layer:
    ```python
    vector_store.similarity_search(query, k=k, filter=lambda m: m['document_id'] in allowed_doc_ids)
    ```
    Thus, any document containing data that does not belong to the authorized list is completely ignored by the FAISS ANN graph search, preventing text leakage.
    """)

# ----------------- PAGE 5: RETRIEVAL ANALYTICS -----------------
elif page == "📊 Retrieval Analytics":
    st.subheader("📊 Retrieval Performance & Analytics Dashboard")
    
    try:
        res = httpx.get(f"{API_URL}/audit/logs", headers=get_headers())
        if res.status_code == 200:
            logs = res.json()
            if not logs:
                st.info("No query logs available yet to build analytics. Run some chat queries!")
            else:
                df = pd.DataFrame(logs)
                
                # Calculations
                total_queries = len(df)
                access_granted = df["access_granted"].sum()
                access_denied = total_queries - access_granted
                avg_confidence = df["confidence_score"].mean() * 100
                avg_latency = df["execution_time_ms"].mean()
                
                # Key stats layout
                st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-bottom: 25px;">
                    <div style="flex:1;" class="metric-card"><div class="metric-value">{total_queries}</div><div class="metric-title">Total Queries</div></div>
                    <div style="flex:1;" class="metric-card"><div class="metric-value" style="color: #22c55e;">{access_granted}</div><div class="metric-title">Clearance Granted</div></div>
                    <div style="flex:1;" class="metric-card"><div class="metric-value" style="color: #ef4444;">{access_denied}</div><div class="metric-title">Clearance Denied</div></div>
                    <div style="flex:1;" class="metric-card"><div class="metric-value">{avg_confidence:.1f}%</div><div class="metric-title">Avg Confidence</div></div>
                    <div style="flex:1;" class="metric-card"><div class="metric-value">{avg_latency:.1f}ms</div><div class="metric-title">Avg Latency</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Visual charts (Plotly)
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.write("**Queries by Intent Routing**")
                    intent_counts = df["routing_intent"].value_counts().reset_index()
                    intent_counts.columns = ["Intent", "Count"]
                    fig1 = px.pie(intent_counts, values="Count", names="Intent", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                with col_chart2:
                    st.write("**Access Authorization Ratio**")
                    fig2 = go.Figure(data=[go.Pie(
                        labels=["Access Granted", "Access Denied"], 
                        values=[access_granted, access_denied], 
                        hole=.4,
                        marker_colors=["#10b981", "#ef4444"]
                    )])
                    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                    st.plotly_chart(fig2, use_container_width=True)
                    
                # Chart 3: Latency over time
                st.write("**RAG Response Latency Trend**")
                df["time_formatted"] = pd.to_datetime(df["timestamp"])
                df_sorted = df.sort_values("time_formatted")
                fig3 = px.line(df_sorted, x="timestamp", y="execution_time_ms", markers=True, color_discrete_sequence=["#6366F1"])
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font_color="#F8FAFC",
                    xaxis_title="Query Time",
                    yaxis_title="Latency (ms)"
                )
                fig3.update_xaxes(showgrid=False)
                fig3.update_yaxes(showgrid=True, gridcolor="#334155")
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error("Clearance Denied. Accessing audit analytics requires Admin or Compliance credentials.")
    except Exception as e:
        st.error(f"Failed to fetch audit data: {e}")

# ----------------- PAGE 6: SECURITY AUDIT LOGS -----------------
elif page == "📜 Security Audit Logs":
    st.subheader("📜 Security Audit Trails & Request Logs")
    
    # Checks permissions
    if st.session_state.role not in ["Admin", "Compliance"]:
        st.warning("🔒 Viewing the query audit logs requires Admin or Compliance role clearance.")
        st.stop()
        
    try:
        res = httpx.get(f"{API_URL}/audit/logs", headers=get_headers())
        if res.status_code == 200:
            logs = res.json()
            if not logs:
                st.info("No audit logs in SQLite database yet.")
            else:
                df = pd.DataFrame(logs)
                
                # Tweak columns for better presentation
                df_display = df[[
                    "timestamp", "username", "role", "department", "query", 
                    "routing_intent", "access_granted", "denied_reason", 
                    "confidence_score", "execution_time_ms", "hallucination_check"
                ]].copy()
                
                # Make timestamps pretty
                df_display["timestamp"] = df_display["timestamp"].apply(lambda x: x.split(".")[0].replace("T", " "))
                
                # Filter by status
                status_filter = st.selectbox("Filter by Access Granted Status", ["All", "Granted Only", "Denied/Blocked Only"])
                if status_filter == "Granted Only":
                    df_display = df_display[df_display["access_granted"] == 1]
                elif status_filter == "Denied/Blocked Only":
                    df_display = df_display[df_display["access_granted"] == 0]
                    
                st.dataframe(df_display, use_container_width=True)
                
                # Export option
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Logs as CSV",
                    data=csv,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.error("Failed to query audit logs endpoint.")
    except Exception as e:
        st.error(f"Cannot load audit data: {e}")

# ----------------- PAGE 7: SYSTEM PERFORMANCE -----------------
elif page == "⚙️ System Performance":
    st.subheader("⚙️ System Health & Infrastructure Metrics")
    
    try:
        res = httpx.get(f"{API_URL}/metrics", headers=get_headers())
        if res.status_code == 200:
            data = res.json()
            curr = data["current"]
            history = data["history"]
            
            # Displays current health metric boxes
            st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 25px;">
                <div style="flex:1;" class="metric-card"><div class="metric-value">{curr['cpu_usage']}%</div><div class="metric-title">CPU Load</div></div>
                <div style="flex:1;" class="metric-card"><div class="metric-value">{curr['memory_usage']}%</div><div class="metric-title">Memory Allocation</div></div>
                <div style="flex:1;" class="metric-card"><div class="metric-value">{curr['vector_count']}</div><div class="metric-title">FAISS Chunks Indexed</div></div>
                <div style="flex:1;" class="metric-card"><div class="metric-value">{curr['total_documents']}</div><div class="metric-title">Total Ingested Files</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Historical trends (if we have points)
            if history:
                df_hist = pd.DataFrame(history)
                df_hist["time_formatted"] = pd.to_datetime(df_hist["timestamp"])
                
                col_h1, col_h2 = st.columns(2)
                
                with col_h1:
                    st.write("**CPU & Memory Usage Trend**")
                    fig_sys = go.Figure()
                    fig_sys.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["cpu_usage"], name="CPU %", line=dict(color='#ef4444')))
                    fig_sys.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["memory_usage"], name="Memory %", line=dict(color='#3b82f6')))
                    fig_sys.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                    st.plotly_chart(fig_sys, use_container_width=True)
                    
                with col_h2:
                    st.write("**Database Scaling Trend**")
                    fig_db = go.Figure()
                    fig_db.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["vector_count"], name="Vector Count", line=dict(color='#8b5cf6')))
                    fig_db.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["total_documents"], name="Total Docs", line=dict(color='#10b981')))
                    fig_db.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
                    st.plotly_chart(fig_db, use_container_width=True)
            else:
                st.info("System performance history logging is running. Refresh in a few minutes to see graphs.")
        else:
            st.error("Failed to query metrics.")
    except Exception as e:
        st.error(f"Cannot load system stats: {e}")
