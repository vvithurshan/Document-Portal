import sys
import os
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from dotenv import load_dotenv
import pandas as pd
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentcompareLLM:
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser()
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.parser
        self.log.info("DocumentcompareLLM initialization done.")

    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions()
            }
            self.log.info("Starting document comparison.")
            response = self.chain.invoke(inputs)
            self.log.info("Document comparison completed.")
            return self._format_response(response)

        except Exception as e:
            self.log.error(f"Error in document comparison: {e}")
            raise DocumentPortalException("An error occurred during document comparison.", sys)

    def _format_response(self, response_parsed: list[dict]) -> pd.DataFrame:
        try:
            df = pd.DataFrame(response_parsed)
            self.log.info(f"Response formatted into DataFrame with shape {df.shape}.")
            return df
        except Exception as e:
            self.log.error(f"Error occurred while formatting into Pandas DataFrame: {e}")
            raise DocumentPortalException("Error occurred while formatting into Pandas DataFrame.", sys)
