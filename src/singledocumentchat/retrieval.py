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
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value] # extra validation
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.history_aware_retriever = create_history_aware_retriever(self.llm, self.retriever, self.contextualize_prompt)
            self.log.info(f"ConversationalRAG Initiated, session_id: {self.session_id}")
            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
            self.log.info(f"RAG chain Created")
            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history(),
                input_messages_key = "input",
                history_messages_key = "chat_history",
                output_messages_key = "answer"
            )

        except Exception as e:
            self.log.error(f"Error initializing conversationalRAG, error: {str(e)}")
            raise DocumentPortalException("Error initializing conversationalRAG", sys)
        
    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info(f"LLM loaded, class_name = {llm.__class__.__name__}")
            return llm

        except Exception as e:
            self.log.error(f"Error loading LLM via ModelLoader, error: {str(e)}")
            raise DocumentPortalException("Error loading LLM via ModelLoader", sys)
        
    def _get_session_history(self):
        try:
            pass

        except Exception as e:
            self.log.error(f"Error getting session history, e: {str(e)}")
            raise DocumentPortalException("Error getting session history", sys)
        
    def _load_retriever_from_faiss(self, index_path: str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index not found at {index_path}")
            
            vectorstore = FAISS.load_local(index_path, embeddings)
            self.log.info(f"FAISS index loaded from {index_path}")
            return vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k": 5})

        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS, error: {str(e)}")
            raise DocumentPortalException("Error loading retriever from FAISS", sys)
        
    def invoke(self, user_input: str) -> str:

        try:
            response = self.chain.invoke(
                {"input": user_input},
                config = {"configurable": {"session_id": self.session_id}}
            )
            answer =  response.get("answer", "No answer")
            if answer == "No answer":
                self.log.warning(f"Empty Answer received, session_id: {self.session_id}")
        
        except Exception as e:
            self.log.error(f"Error invoking, error: {str(e)}")
            raise DocumentPortalException("Error invoking", sys)