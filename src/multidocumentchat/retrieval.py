import os
import sys
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id: str, retriever = None):
        try:
            self.log = CustomLogger.get_logger(__name__)
            self.session_id = session_id
            self.llm = self._loadllm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            if retriever is None:
                raise ValueError("Retriever cannot be None")
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info(f"ConversationalRAG Initialized with session_id: {self.session_id}")

        except Exception as e:
            self.log.error(f"Failed to initialize ConversationalRAG: {e}")
            raise DocumentPortalException(f"Failed to initialize ConversationalRAG: {e}", sys)

    def load_retriever_from_faiss(self):
        pass

    def invoke(self):
        pass

    def _loadllm(self):
        pass
    @staticmethod
    def _formart_docs(docs):
        pass

    def _build_lcel_chain(self):
        pass

    

