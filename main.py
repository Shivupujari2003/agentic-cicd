import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")  # 🔁 Change to EC2 IP when deployed

st.set_page_config(
    page_title="Agentic CI/CD Task Manager", 
    layout="centered",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .task-item {
        background: #f8f9fa;
        padding: 1em;
        border-radius: 8px;
        margin: 0.5em 0;
        border-left: 4px solid #1f77b4;
    }
    .stats-box {
        background: #e8f4f8;
        padding: 1em;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">� Agentic CI/CD Task Manager</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Task Management with Enterprise DevOps Integration</p>', unsafe_allow_html=True)

# Sidebar for project info
with st.sidebar:
    st.header("📊 Project Info")
    st.markdown("""
    **Agentic CI/CD Task Manager**
    - 🤖 AI-Powered Test Generation
    - 🔄 Jenkins Pipeline Integration
    - 🎟️ JIRA Automation
    - 🐳 Docker Deployment
    - ☁️ AWS EC2 Hosting
    """)
    
    # API Health Check
    try:
        health_response = requests.get(f"{API_URL}/tasks", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ API Status: Connected")
        else:
            st.error("❌ API Status: Error")
    except requests.exceptions.RequestException:
        st.error("❌ API Status: Disconnected")
    
    st.markdown(f"**API Endpoint:** `{API_URL}`")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- Add Task ---
st.subheader("➕ Add New Task")
col1, col2 = st.columns([3, 1])

with col1:
    title = st.text_input("Task Title", placeholder="e.g., Implement user authentication", key="task_input")
with col2:
    st.write("")
    st.write("")
    add_button = st.button("Add Task", type="primary")

if add_button:
    if title.strip():
        try:
            response = requests.post(f"{API_URL}/tasks", json={"title": title}, timeout=10)
            if response.status_code == 201:
                st.success("✅ Task added successfully!")
                st.rerun()
            else:
                st.error(f"❌ Failed to add task. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: {str(e)}")
    else:
        st.warning("⚠️ Task title cannot be empty.")

# --- Get Tasks ---
st.subheader("📋 All Tasks")

try:
    response = requests.get(f"{API_URL}/tasks", timeout=10)
    
    if response.status_code == 200:
        tasks = response.json()
        
        if not tasks:
            st.info("📝 No tasks found. Add your first task above!")
        else:
            # Task Statistics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.get('completed', False))
            pending_tasks = total_tasks - completed_tasks
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", total_tasks)
            with col2:
                st.metric("Completed", completed_tasks)
            with col3:
                st.metric("Pending", pending_tasks)
            
            st.markdown("---")
            
            # Display tasks
            for i, task in enumerate(tasks):
                with st.container():
                    col1, col2, col3, col4 = st.columns([0.5, 4, 1, 1])
                    
                    with col1:
                        # Task completion toggle
                        current_status = task.get('completed', False)
                        new_status = st.checkbox(
                            "Complete", 
                            value=current_status, 
                            key=f"complete_{task['id']}",
                            label_visibility="hidden"
                        )
                        
                        if new_status != current_status:
                            try:
                                update_response = requests.put(
                                    f"{API_URL}/tasks/{task['id']}", 
                                    json={"completed": new_status},
                                    timeout=10
                                )
                                if update_response.status_code == 200:
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update task status")
                            except requests.exceptions.RequestException:
                                st.error("Network error while updating task")
                    
                    with col2:
                        # Task title with status
                        status_icon = "✅" if task.get('completed', False) else "⏳"
                        task_style = "text-decoration: line-through; color: #888;" if task.get('completed', False) else ""
                        st.markdown(f'<div style="{task_style}">{status_icon} **{task["title"]}**</div>', unsafe_allow_html=True)
                    
                    with col3:
                        # Task ID
                        st.caption(f"ID: {task['id']}")
                    
                    with col4:
                        # Delete button
                        if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                            try:
                                delete_response = requests.delete(f"{API_URL}/tasks/{task['id']}", timeout=10)
                                if delete_response.status_code == 200:
                                    st.success("Task deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete task")
                            except requests.exceptions.RequestException:
                                st.error("Network error while deleting task")
                    
                    st.markdown("---")
    else:
        st.error(f"❌ Failed to load tasks. API returned status: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    st.error(f"❌ Cannot connect to API server: {str(e)}")
    st.info("💡 Make sure the API server is running on port 8000")
    st.code("python task_api.py", language="bash")

# --- Footer Section ---
st.markdown("---")
st.markdown("### 🛠️ Development & CI/CD Info")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **🔧 Tech Stack:**
    - Backend: FastAPI + SQLModel
    - Frontend: Streamlit
    - Database: SQLite
    - CI/CD: Jenkins + Docker
    - Cloud: AWS EC2
    """)

with col2:
    st.markdown("""
    **🚀 Features:**
    - AI-Powered Test Generation
    - Automated JIRA Integration
    - Docker Containerization
    - Pipeline Automation
    - Real-time Task Management
    """)

# Debug section (only show if API is down)
if st.checkbox("🔧 Show Debug Info"):
    st.markdown("### Debug Information")
    st.json({
        "API_URL": API_URL,
        "timestamp": datetime.now().isoformat(),
        "streamlit_version": st.__version__,
        "environment": "development" if "localhost" in API_URL else "production"
    })
    
    # Quick API test
    if st.button("🔍 Test API Connection"):
        try:
            test_response = requests.get(f"{API_URL}/tasks", timeout=5)
            st.success(f"✅ API Response: {test_response.status_code}")
            st.json(test_response.json() if test_response.status_code == 200 else {})
        except Exception as e:
            st.error(f"❌ API Test Failed: {str(e)}")

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9em;">'
    '🚀 Agentic CI/CD Task Manager - Built with AI-Powered DevOps Automation'
    '</div>', 
    unsafe_allow_html=True
)
