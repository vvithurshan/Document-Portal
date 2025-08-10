import uuid
from pathlib import Path
import sys
from datetime import datetime, timezone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class SingleDocIngestor:

    def __init__(self, data_dir = "data/single_document", faiss_dir: str = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info(f"SingleDocIngestor Initiated, data_dir: {self.data_dir}, faiss_dir: {self.faiss_dir}")

        except Exception as e:

            self.log.error(f"Error occurred initializing SingleDocIngestor, error: {str(e)}")
            raise DocumentPortalException("Error occurred initializing SingleDocIngestor", sys)
        
    def ingest_files(self, uploaded_files):

        try:
            documents = []

            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f_out:
                   f_out.write(uploaded_file.read())

                self.log.info(f"PDF saved ({uploaded_file.name}) in {temp_path}")

                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            self.log.info(f"PDF files loaded, count {len(documents)}")

            return self._create_retriver(documents)
        
        except Exception as e:

            self.log.error(f"Document ingestion failed, error {str(e)}")
            raise DocumentPortalException("Document ingestion failed", sys)
        
    def _create_retriver(self, documents):
        try:
            # split
            splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 300)
            chunks = splitter.split_documents(documents)
            self.log.info(f"Chunks created, count: {len(chunks)}")

            # create embeddings
            embeddigns = self.model_loader.load_embeddings()

            # vector store
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddigns)

            # save FAISS index
            vectorstore.save_local(str(self.faiss_dir))
            self.log.info(f"FAISS index saved in {self.faiss_dir}") 

            # retriever
            retriever = vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k": 5})
            self.log.info(f"Retriever created")

            return retriever


        except Exception as e:

            self.log.error(f"Retriever creation failed, error: {str(e)}")
            raise DocumentPortalException("Retriever creation failed", sys)