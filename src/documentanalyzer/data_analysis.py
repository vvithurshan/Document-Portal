import os
import sys
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyzer:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        
        try:
            # load the model
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            # prepare parsers
            self.parser = JsonOutputParser(pydantic_object = Metadata)
            self.fix_parser = OutputFixingParser.from_llm(parser = self.parser, llm = self.llm)

            self.prompt = PROMPT_REGISTRY["document_analysis"]
            self.log.info("DocumentAnalyzer initialized successfully")


        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException(e, sys)

    def analyze_document(self, document_text: str) -> dict:
        try:
            chain = self.prompt | self.llm | self.fix_parser
            self.log.info("Document analysis started")
            
            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            self.log.info("Document analysis completed")
            return response
        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException(e, sys)