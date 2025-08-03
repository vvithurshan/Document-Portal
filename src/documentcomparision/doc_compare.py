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
        self.fixing_parser = OutputFixingParser.from_llm(parser = self.parser, llm = self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentcompareLLM initialization Done")

    def compare_documents(self, combined_docs):
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions()
            }
            self.log.info(f"Starting Document Comparision inputs: {inputs}")
            response = self.chain.invoke(inputs)
            self.log.info(f"Document Comparison Completed, response {response}")
            return self._format_response(response)

        except DocumentcompareLLM as e:
            self.log.error(f"Error in Compare Document: {e}")
            raise DocumentcompareLLM(f"An Error occured: {sys}")

    def _format_response(self, response_parsed:list[dict]) -> pd.DataFrame:
        try:
            df = pd.DataFrame(response_parsed)
            self.log.info(f"Response formated into DataFrame, dataframe: {df}")
            return df
        except Exception as e:
            self.log.error(f"Error occured while formatting into Pandas DataFrame: {e}")
            raise DocumentPortalException(f"Error occured while formatting into Pandas DataFrame: {e}")



