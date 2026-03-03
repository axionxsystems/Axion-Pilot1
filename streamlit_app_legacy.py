import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI College Project Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4B4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #6C757D;
        margin-top: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    .success-box {
        padding: 1rem;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-radius: 5px;
        color: #155724;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.title("🎓 AI Project Gen")
        st.info("Industry-Ready Project Generator & Viva Assistant")
        
        api_key = st.text_input("Enter LLM API Key (Groq/OpenRouter)", type="password", help="Leave empty if set in .env")
        if not api_key:
             api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        
        if api_key:
            st.session_state['api_key'] = api_key
            st.success("API Key Detected ✨")
        else:
            st.warning("Please provide an API Key to proceed.")
            
        st.markdown("---")
        mode = st.radio("Select Mode", ["Project Generator", "Viva Assistant", "Download Center"])
        
        st.markdown("---")
        st.markdown("### 💎 Subscription")
        st.caption("Current Plan: Free Tier")
        st.button("Upgrade to Pro 🚀")

    if mode == "Project Generator":
        st.markdown('<div class="main-header">🚀 AI College Project Generator</div>', unsafe_allow_html=True)
        st.write("Generate complete college projects including Code, Reports, and PPTs in seconds.")
        
        col1, col2 = st.columns(2)
        with col1:
            domain = st.selectbox("Select Domain", ["Machine Learning", "Web Development", "Data Science", "IoT", "Blockchain", "Cybersecurity", "Android App"])
            difficulty = st.select_slider("Project Difficulty", options=["Beginner", "Intermediate", "Advanced"])
        with col2:
            tech_stack = st.text_input("Preferred Tech Stack (e.g., Python, React, MERN)")
            year = st.selectbox("Academic Year", ["1st Year", "2nd Year", "3rd Year", "Final Year"])
            
        topic = st.text_input("Specific Topic (Optional)", placeholder="e.g., Stock Price Prediction")
        
        if st.button("✨ Generate Project"):
            if 'api_key' not in st.session_state or not st.session_state['api_key']:
                 st.error("Please configure your API Key in the sidebar.")
            else:
                with st.spinner("Generating project structure... This may take 1-2 minutes."):
                    try:
                        from generators.project_gen import generate_project
                        project_data = generate_project(
                            st.session_state['api_key'], 
                            domain, 
                            topic if topic else "Random innovative topic", 
                            difficulty, 
                            tech_stack, 
                            year
                        )
                        if project_data:
                            st.session_state['project_data'] = project_data
                            st.success(f"Project '{project_data.get('title')}' Generated Successfully! Go to Download Center.")
                        else:
                            st.error("Failed to generate project structure. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                
    elif mode == "Viva Assistant":
        st.markdown('<div class="main-header">🤖 AI Viva Assistant</div>', unsafe_allow_html=True)
        
        if 'project_data' not in st.session_state:
            st.warning("Please generate a project first to start the Viva.")
        else:
            st.write(f"Viva for: **{st.session_state['project_data'].get('title')}**")
            
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your external examiner. Tell me about your project."}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Type your answer or question here..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                
                with st.spinner("Examiner is thinking..."):
                    from generators.viva_gen import get_viva_response
                    response = get_viva_response(
                        st.session_state['api_key'], 
                        st.session_state.messages, 
                        st.session_state['project_data']
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").write(response)

            
    elif mode == "Download Center":
        st.markdown('<div class="main-header">📥 Download Center</div>', unsafe_allow_html=True)
        
        if 'project_data' in st.session_state:
            project = st.session_state['project_data']
            st.info(f"Ready to download assets for: {project.get('title')}")
            
            tab1, tab2, tab3 = st.tabs(["📄 Report", "📊 Presentation", "💻 Source Code"])
            
            with tab1:
                from generators.report_gen import generate_report
                report_buffer = generate_report(project)
                st.download_button(
                    label="Download Report (DOCX)",
                    data=report_buffer,
                    file_name="project_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            with tab2:
                from generators.ppt_gen import generate_ppt
                ppt_buffer = generate_ppt(project)
                st.download_button(
                    label="Download Presentation (PPTX)",
                    data=ppt_buffer,
                    file_name="project_presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
            with tab3:
                from generators.code_gen import generate_code_zip
                zip_buffer = generate_code_zip(project)
                st.download_button(
                    label="Download Source Code (ZIP)",
                    data=zip_buffer,
                    file_name="project_code.zip",
                    mime="application/zip"
                )
        else:
            st.warning("No project generated yet. Go to 'Project Generator' to start.")

if __name__ == "__main__":
    main()
