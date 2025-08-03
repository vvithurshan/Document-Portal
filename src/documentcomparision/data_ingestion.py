import sys
import os
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentCompare:
    def __init__(self, base_dir):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def delete(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error occured while deleting: {e}")
            raise DocumentPortalException(f"Error occured while deleting: {e}")

    def save_uploaded_file(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error Occured while saving file: {e}")
            raise DocumentPortalException(f"Error occured while saving file: {sys}")

    def read_pdf(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                if doc.isencrypted:
                    raise ValueError("PDF is encrypted and cannot be read")
        except Exception as e:
            self.log.error(f"Error occured while reading PDF: {e}")
            raise DocumentPortalException(f"An Error occured while reading pdf: {sys}")