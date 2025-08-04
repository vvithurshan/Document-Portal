import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id: str, retriever) -> None:
        try:
            self.log = CustomLogger.get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever

        except Exception as e:
            self.log.error(f"Error initializing conversationalRAG, error: {str(e)}")
            raise DocumentPortalException("Error initializing conversationalRAG", sys)
        
    def _load_llm(self):
        try:
            pass

        except Exception as e:
            self.log.error(f"Error loading LLM via ModelLoader, error: {str(e)}")
            raise DocumentPortalException("Error loading LLM via ModelLoader", sys)
        
    def _get_session_history(self):
        try:
            pass

        except Exception as e:
            self.log.error(f"Error getting session history, e: {str(e)}")
            raise DocumentPortalException("Error getting session history", sys)
        
    def _create_retriever_from_faiss(self):
        try:
            pass

        except Exception as e:
            self.log.error(f"Error loading retriver from FAISS, error: {str(e)}")
            raise DocumentPortalException("Error loading retriver from FAISS", sys)
        
    def invoke(self):

        try:
            pass
        
        except Exception as e:
            self.log.error(f"Error invoking, error: {str(e)}")
            raise DocumentPortalException("Error invoking", sys)