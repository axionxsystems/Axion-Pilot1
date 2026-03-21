import io
import zipfile
import json
from app.core.generators.report_gen import generate_report
from app.core.generators.ppt_gen import generate_ppt

def generate_code_zip(project_data):
    files = project_data.get('files', [])
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            filename = file.get('filename', 'unknown.txt')
            content = file.get('content', '')
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def generate_full_zip(project_data):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add Code Files
        files = project_data.get('files', [])
        for file in files:
            filename = file.get('filename', 'unknown.txt')
            content = file.get('content', '')
            zip_file.writestr(f"code/{filename}", content)
            
        # Add Report
        try:
            report_buffer = generate_report(project_data)
            zip_file.writestr("Project_Report.docx", report_buffer.read())
        except Exception as e:
            zip_file.writestr("Project_Report_Error.txt", f"Failed to generate report: {str(e)}")
            
        # Add PPT
        try:
            ppt_buffer = generate_ppt(project_data)
            zip_file.writestr("Project_Presentation.pptx", ppt_buffer.read())
        except Exception as e:
            zip_file.writestr("Project_Presentation_Error.txt", f"Failed to generate UI: {str(e)}")

        # Add Viva Questions
        viva = project_data.get('viva_questions', [])
        viva_text = "Viva Questions:\n\n"
        for v in viva:
            viva_text += f"Q: {v.get('question', '')}\nA: {v.get('answer', '')}\n\n"
        zip_file.writestr("Viva_Questions.txt", viva_text)
        
    zip_buffer.seek(0)
    return zip_buffer
