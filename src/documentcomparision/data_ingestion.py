import sys
import os
from pathlib import Path
import fitz  # PyMuPDF
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentCompare:
    def __init__(self, base_dir: Path = Path("./data/document_compare")):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = base_dir if isinstance(base_dir, Path) else Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def delete(self):
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                        self.log.info(f"File deleted: {file}")
                self.log.info(f"Directory cleaned: {self.base_dir}")
        except Exception as e:
            self.log.error(f"Error occurred while deleting: {e}")
            raise DocumentPortalException("Error occurred while deleting", sys)

    def save_uploaded_file(self, reference_file, actual_file):
        try:
            self.log.info("Deleting previously saved files (if any)...")
            # self.delete()  # Uncomment if needed

            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Only PDF files are allowed")

            ref_path = self.base_dir / reference_file.name
            act_path = self.base_dir / actual_file.name

            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())

            self.log.info(f"Files saved - reference: {ref_path}, actual: {act_path}")
            return ref_path, act_path

        except Exception as e:
            self.log.error(f"Error occurred while saving files: {e}")
            raise DocumentPortalException("Error occurred while saving files", sys)

    def read_pdf(self, pdf_path: Path) -> str:
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError("PDF is encrypted and cannot be read")

                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all_text.append(f"\n-- Page {page_num + 1} --\n{text}")

                self.log.info(f"PDF read successfully - file: {pdf_path}, pages: {len(all_text)}")
                return "\n".join(all_text)

        except Exception as e:
            self.log.error(f"Error occurred while reading PDF: {e}")
            raise DocumentPortalException("Error occurred while reading PDF", sys)

    def combine_documents(self) -> str:
        try:
            content_dict = {}
            doc_parts = []

            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix.lower() == ".pdf":
                    content_dict[filename.name] = self.read_pdf(filename)

            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info(f"Documents combined - count: {len(doc_parts)}")
            return combined_text

        except Exception as e:
            self.log.error(f"Error occurred while combining documents: {e}")
            raise DocumentPortalException("Error occurred while combining documents", sys)
