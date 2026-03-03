import io
import zipfile

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
