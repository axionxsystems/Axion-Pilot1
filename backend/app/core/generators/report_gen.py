from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

def generate_report(project_data):
    doc = Document()
    
    # Title Page
    doc.add_heading(project_data.get('title', 'Project Report'), 0)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"\nA Project Report Submitted for {project_data.get('domain', 'Computer Science')}\n").bold = True
    
    doc.add_page_break()
    
    # Abstract
    doc.add_heading('Abstract', level=1)
    doc.add_paragraph(project_data.get('abstract', 'No abstract provided.'))
    
    # Proposed System
    doc.add_heading('Problem Statement', level=1)
    doc.add_paragraph(project_data.get('problem_statement', ''))
    
    # Architecture
    doc.add_heading('System Architecture', level=1)
    doc.add_paragraph(project_data.get('architecture_description', ''))
    
    # Tech Stack
    doc.add_heading('Technology Stack', level=1)
    tech = project_data.get('tech_stack_details', {})
    for k, v in tech.items():
        doc.add_paragraph(f"{k}: {v}", style='List Bullet')
        
    # Conclusion
    doc.add_heading('Conclusion', level=1)
    doc.add_paragraph("This project demonstrates a practical implementation of the proposed system.")
    
    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
