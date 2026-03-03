from pptx import Presentation
from pptx.util import Inches, Pt
import io

def generate_ppt(project_data):
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = project_data.get('title', 'Project Presentation')
    subtitle.text = f"Presented by Student\nDomain: {project_data.get('domain', '')}"
    
    # Abstract Slide
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Abstract"
    tf = body_shape.text_frame
    tf.text = project_data.get('abstract', '')[:500] + "..." # Truncate if too long
    
    # Problem Statement
    slide = prs.slides.add_slide(bullet_slide_layout)
    slide.shapes.title.text = "Problem Statement"
    slide.placeholders[1].text_frame.text = project_data.get('problem_statement', '')
    
    # Architecture
    slide = prs.slides.add_slide(bullet_slide_layout)
    slide.shapes.title.text = "System Architecture"
    slide.placeholders[1].text_frame.text = project_data.get('architecture_description', '')

    # Tech Stack
    slide = prs.slides.add_slide(bullet_slide_layout)
    slide.shapes.title.text = "Technology Stack"
    tf = slide.placeholders[1].text_frame
    tech = project_data.get('tech_stack_details', {})
    for k, v in tech.items():
        p = tf.add_paragraph()
        p.text = f"{k}: {v}"

    # Conclusion
    slide = prs.slides.add_slide(bullet_slide_layout)
    slide.shapes.title.text = "Conclusion"
    slide.placeholders[1].text_frame.text = "Thank You!"

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer
