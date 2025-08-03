import sys
import os
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentCompare:
    def __init__(self, base_dir = Path("./data/document_compare")):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def delete(self):
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink() # delete
                        self.log.info(f"File Deleted, path: {str(file)}")

                self.log.info(f"Directory cleaned, directory: {str(self.base_dir)}")

        except Exception as e:
            self.log.error(f"Error occured while deleting: {e}")
            raise DocumentPortalException(f"Error occured while deleting", sys)

    def save_uploaded_file(self, reference_file, actual_file):
        try:
            self.delete()
            self.log.info(f"File deleted successfully")
            ref_path = Path(self.base_dir, reference_file.name)
            act_path = Path(self.base_dir, actual_file.name)

            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Only PDf files are allowed")
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())

            self.log.info(f"Files saved reference: {str(ref_path)}, actural: {str(act_path)}")
            return ref_path, act_path
        
        except Exception as e:
            self.log.error(f"Error Occured while saving file: {e}")
            raise DocumentPortalException(f"Error occured while saving file", sys)

    def read_pdf(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError("PDF is encrypted and cannot be read")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()

                    if text.strip():
                        all_text.append(f"\n --Page {page_num + 1} -- \n{text}")

                self.log.info(f"PDf read successfully file = {str(pdf_path)}, pages = {len(all_text)}")
                return "\n".join(all_text)

        except Exception as e:
            self.log.error(f"Error occured while reading PDF: {e}")
            raise DocumentPortalException(f"An Error occured while reading pdf", sys)
        
    def combine_documents(self):
        try:
            content_dict = {}
            doc_parts = []

            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix == ".pdf":
                    content_dict[filename.name] = self.read_pdf(filename)

            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info(f"Document combined, count: {len(doc_parts)}")
            return combined_text
        
        except Exception as e:
            self.log.error(f"Error combining documents: {e}")
            raise DocumentPortalException(f"Error combining documents", sys)
