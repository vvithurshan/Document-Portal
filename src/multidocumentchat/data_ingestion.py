import uuid
from pathlib import Path
import sys
from datetime import datetime, timezone
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, MarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class DocumentIngestor:
    SUPPORTED_FILE_TYPES = {'.pdf', '.docx', '.txt', '.md'}
    def __init__(self,temp_dir:str = "data/multi_document", faiss_dir: str = "faiss_index", session_id: str | None = None ):
        self.log = CustomLogger.get_logger(__name__)
        try:
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents = True, exist_ok = True)
            self.faiss_dir.mkdir(parents = True, exist_ok = True)

            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok = True)
            self.session_faiss_dir.mkdir(parents = True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info(f"DocumentIngestor Initialized with session_id: {self.session_id}")


        except Exception as e:
            self.log.error(f"Failed to initialize DocumentIngestor: {e}")
            raise DocumentPortalException(f"Failed to initialize DocumentIngestor: {e}", sys)

    def ingest_files(self, uploaded_files):
        try:
            documents = []
            for uploaded_file in uploaded_files:
                extension = Path(uploaded_file.name).suffix.lower()
                if extension not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning(f"Unsupported file type: {extension}")
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}.{extension}"
                temp_path = self.session_temp_dir / unique_filename

                with open(temp_path, "wb") as f_out:
                    f_out.write(uploaded_file.read())
                self.log.info(f"File saved ({uploaded_file.name}) in {temp_path}")

                if extension == '.pdf':
                    loader = PyPDFLoader(str(temp_path))
                elif extension == '.docx':
                    loader = Docx2txtLoader(str(temp_path))
                elif extension == '.txt':
                    loader = TextLoader(str(temp_path))
                elif extension == '.txt':
                    loader = TextLoader(str(temp_path))
                elif extension == '.md':
                    loader = MarkdownLoader(str(temp_path))
                
                document = loader.load()
                documents.extend(document)

            if not documents:
                self.log.error(f"No Files are Loaded")
                raise DocumentPortalException("No Files are Loaded", sys)    
            
            self.log.info(f"Files loaded, count: {len(documents)}")
            return self._create_retrieval(documents)

        except Exception as e:
            self.log.error(f"Ingestion Error : {e}")
            raise DocumentPortalException(f"Ingestion Error: {e}", sys)

    def _create_retrieval(self, documents):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            self.log.info(f"Total Chunks: {len(chunks)}")

            embeddings = ModelLoader().load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            vectorstore.save_local(str(self.session_faiss_dir))
            self.log.info(f"Vectorstore saved in {self.session_faiss_dir}")

            return vectorstore.as_retriever(search_type = 'similarity', search_kwargs = {'k': 5})
        
        except Exception as e:
            self.log.error(f"Retrieval Error : {e}")
            raise DocumentPortalException(f"Retrieval Error: {e}", sys)


