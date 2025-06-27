#libraries
import io
import pymupdf

#files
from .chatbot import chatbot_function
from backend_app.constants import cv_prompt


def extract_text_from_cv(uploaded_file : ...) -> str | None:
    try:
        # Read uploaded file as BytesIO
        cv_data = pymupdf.open(stream=io.BytesIO(uploaded_file.file.read()), filetype="pdf")
        full_text = []

        for page_num in range(cv_data.page_count):
            page = cv_data.load_page(page_num)
            page_text = page.get_text("text")  # Extract plain text
            full_text.append(page_text)
        cv_text = full_text
        cv_text = chatbot_function(prompt=cv_prompt, data=cv_text)
        cv_data.close()
        return cv_text
    except Exception as e:
        return f"Error reading PDF: {e}"
