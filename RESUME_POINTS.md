# 🎓 AI College Project Generator - Resume & Scalability Guide

## 📄 Resume Bullet Points

**Project Title:** AI-Powered Automated College Project Generator & Viva Assistant

**Description:**
Developed a full-stack AI SaaS application that automates the creation of academic projects (Code, Documentation, Presentation) and simulates Viva Voce exams using Large Language Models (LLMs).

**Key Technical Achievements:**
- **AI Orchestration**: Integrated **Groq/Llama-3** to generate complex multi-file coding projects, technical reports (2000+ words), and presentations from a single prompt.
- **Dynamic Document Generation**: Engineered a Python-based pipeline using `python-docx` and `python-pptx` to programmatically build formatted Word documents and PowerPoint slides.
- **Context-Aware Chatbot**: Built a RAG-style Viva Assistant that maintains conversation history and uses generated project context to ask relevant technical questions.
- **SaaS Architecture**: Implemented a modular backend with **Streamlit** for the frontend, featuring state management, downloadable assets (ZIP/PDF), and extensible API wrappers.
- **Optimization**: Reduced generation costs to zero by leveraging open-source LLMs via efficient prompt engineering.

**Tech Stack:** Python, Streamlit, Groq API, Llama-3, Pandas, python-docx, python-pptx.

---

## 🚀 Future Scalability & Monetization Ideas

1. **Freemium Model**:
   - **Free Tier**: Basic code generation, watermarked PDF reports.
   - **Pro Tier ($5/mo)**: Enhanced code quality, non-watermarked export, editable PPTX, and specific viva modes (Strict/Lenient).

2. **Integration with GitHub**:
   - Automatically push generated code to a new GitHub repository for the user.
   - CI/CD pipeline generation for the created project.

3. **Multi-LLM Support**:
   - Add a dropdown to switch between GPT-4, Claude 3, and Llama 3 based on user preference and budget.

4. **Custom Templates**:
   - Allow universities to upload their specific thesis/report format templates.

5. **Code Execution Sandbox**:
   - Integrate a secure sandbox (e.g., Docker) to run and test the generated code in the browser.
