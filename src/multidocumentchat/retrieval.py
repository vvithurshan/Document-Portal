import os
import sys
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional
from langchain_core.messages import BaseMessage
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

    def load_retriever_from_faiss(self, index_path: str):
        try:
            embedding = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index not found at {index_path}")
            vectorstore = FAISS.load_local(
                index_path,
                embedding,
                allow_dangerous_deserialization=True
            )
            self.retriever = vectorstore.as_retriever(search_type = 'similarity', search_kwargs = {'k': 5})
            self.log.info(f"Retriever loaded from FAISS at {index_path}")
            self._build_lcel_chain()
            return self.retriever

        except Exception as e:
            self.log.error(f"Failed to load retriever from FAISS: {e}")
            raise DocumentPortalException(f"Failed to load retriever from FAISS: {e}", sys)

    def invoke(self, user_input: str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        try:
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning(f"No answer generated for input: {user_input}")
                return "No answer generated"
            self.log.info(f"Answer generated for input: {user_input}")
            return answer
        
        except Exception as e:
            self.log.error(f"Failed to invoke ConversationalRAG: {e}")
            raise DocumentPortalException(f"Failed to invoke ConversationalRAG: {e}", sys)

    def _loadllm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("Failed to load LLM")
            self.log.info("LLM loaded successfully")
            return llm

        except Exception as e:
            self.log.error(f"Failed to load LLM: {e}")
            raise DocumentPortalException(f"Failed to load LLM: {e}", sys)
        
    @staticmethod
    def _formart_docs(docs):
        return "\n\n".join([doc.page_contect] for doc in docs)

    def _build_lcel_chain(self):
        # the following can be done with langgraph
        try:
            question_rewriter = (
                {
                    "input": itemgetter("input"), "chat_history": itemgetter("chat_history")
                }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )
            retrieve_docs = self.retriever | self._formart_docs
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                |self.qa_prompt
                |self.llm
                |StrOutputParser()

            )
            self.log.info("LCEL chain built successfully")

        except Exception as e:
            self.log.error(f"Failed to build LCEL chain: {e}")
            raise DocumentPortalException(f"Failed to build LCEL chain: {e}", sys)

    

