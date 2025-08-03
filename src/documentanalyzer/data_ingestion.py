import os
import sys
import fitz
import uuid # for universal identification number
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from pathlib import Path
from io import BytesIO # to keep the data in the memory

class DocumentHandler:
    """
    Handles PDF saving and reading operations.
    Automatically logs all actions and supports secssion-based organization
    """
    def __init__(self, data_dir = None, session_id = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or \
            os.getenv("DATA_STORAGE_PATH", 
                    os.path.join(os.getcwd(), "data", "document_analysis"))
            self.session_id = session_id or \
            f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok = True)
            self.log.info(f"PDFHandler initialized, session_id = {self.session_id}, session_path = {self.session_path}")

        except Exception as e:
            self.log.error(f"Error initializing PDFHandler: {e}")
            raise DocumentPortalException(e, sys)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException("Invalid file type. Only PDFs are allowed")
            
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            self.log.info(f"PDF {filename}saved to {save_path} successfully session_id = {self.session_id}")

            return save_path
        
        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException(e, sys)

    # this can be repalced with langchain PDF reader
    def read_pdf(self, pdf_path):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start = 1):
                    text_chunks.append(f"\n-- page {page_num} --\n{page.get_text()}")
            text = "\n".join(text_chunks)
            self.log.info(f"PDF read successfully session_id = {self.session_id}")
            return text

        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentPortalException(e, sys)
        
# it saves the data inside the session folder
# this is called data archival strategy
if __name__ == "__main__":
    pdf_path = "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/document_analysis/sample.pdf"

    class DummyFile:
        def __init__(self, file_path):
            self.name = Path(file_path).name
            self._file_path = file_path
            
        def getbuffer(self):
            return open(self._file_path, "rb").read()
        
    dummy_pdf = DummyFile(pdf_path)

    handler = DocumentHandler(session_id = "test_session")

    try: 
        saved_path = handler.save_pdf(dummy_pdf)
        print(saved_path)

        content = handler.read_pdf(saved_path)
        print(content[:100])

    except Exception as e:
        print(e)



