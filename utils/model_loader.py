import sys
# sys.path.append('./')
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

# initialize logger
log = CustomLogger.get_logger(__name__)

class ModelLoader:
    """
    A utility function to load LLM and embedding models.
    """
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Config loaded sucessfully", list(self.config.keys()))
        
    def _validate_env(self):
        required_variables = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.api_keys = {key: os.getenv(key) for key in required_variables}
        missing = [key for key, value in self.api_keys.items() if value is None]

        if missing:
            log.info(f"Missing required environment variables: {', '.join(missing)}")
            raise DocumentPortalException(f"Missing required environment variables: {', '.join(missing)}")
        
        log.info("All required environment variables are present")

    def load_embeddings(self):
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info(f"Loading embeddings {model_name}")
            embeddings = GoogleGenerativeAIEmbeddings(
                model =model_name,
            )
            log.info("Embeddings loaded sucessfully")
            return embeddings                
        
        except Exception as e:
            log.error("Error Loading embeddings", error = str(e))
            raise DocumentPortalException("Error Loading embeddings")
        
    def load_llm(self):
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER", "groq")

        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider = provider_key)
            raise ValueError(f"LLM provider {provider_key} not found in config")
        
        llm_config = llm_block[provider_key]
        provider = llm_config["provider"]
        model_name = llm_config["model_name"]
        temperature = llm_config["temperature"]
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info(f"Loading LLM: provider={provider}, model_name={model_name}, temperature={temperature}, max_tokens={max_tokens}")

        if provider == 'google':
            llm = ChatGoogleGenerativeAI(
                model_name = model_name,
                temperature = temperature,
                max_output_tokens = max_tokens,
            )
            log.info(f"LLM {provider} loaded sucessfully")
            return llm
        
        elif provider == 'groq':
            llm = ChatGroq(
                model = model_name,
                temperature = temperature,
                max_tokens = max_tokens,
                api_key = self.api_keys["GROQ_API_KEY"],
            )
            log.info(f"LLM {provider} loaded sucessfully")
            return llm
        else:
            log.error("LLM provider not found", provider = provider)
            raise ValueError(f"LLM provider {provider} not found")  


if __name__ == "__main__":
    model_loader = ModelLoader()
    embeddings = model_loader.load_embeddings()
    print(f"Embeddings: {embeddings} Loaded sucessfully")

    llm = model_loader.load_llm()
    print(f"LLM: {llm} Loaded sucessfully")

    # Test
    result = llm.invoke("what does nm stand for in science?")
    print(f"Result: {result.content}")