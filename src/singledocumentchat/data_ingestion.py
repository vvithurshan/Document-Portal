import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class SingleDocIngestor:

    def __init__(self):
        try:

            self.log = CustomLogger().get_logger(__name__)

        except Exception as e:

            self.log.error(f"Error occurred initializing SingleDocIngestor, error: {str(e)}")
            raise DocumentPortalException("Error occurred initializing SingleDocIngestor", sys)
        
    def ingest_files(self,):
        
        try:
            pass

        except Exception as e:

            self.log.error(f"Document ingestion failed, error {str(e)}")
            raise DocumentPortalException("Document ingestion failed", sys)
        
    def _create_retriver(self):
        try:

            pass

        except Exception as e:

            self.log.erro(f"Retriever creation failed, error: {str(e)}")
            raise DocumentPortalException("Retriever creation failed", sys)