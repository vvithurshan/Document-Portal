# import os
# from pathlib import Path
# from src.documentanalyzer.data_ingestion import DocumentHandler       # Your PDFHandler class
# from src.documentanalyzer.data_analysis import DocumentAnalyzer  # Your DocumentAnalyzer class

# # Path to the PDF you want to test
# PDF_PATH = "data/document_analysis/sample.pdf"

# # Dummy file wrapper to simulate uploaded file (Streamlit style)
# class DummyFile:
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self):
#         return open(self._file_path, "rb").read()

# def main():
#     try:
#         # ---------- STEP 1: DATA INGESTION ----------
#         print("Starting PDF ingestion...")
#         dummy_pdf = DummyFile(PDF_PATH)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")
        
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         # ---------- STEP 2: DATA ANALYSIS ----------
#         print("Starting metadata analysis...")
#         analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
#         analysis_result = analyzer.analyze_document(text_content[:5000])

#         # ---------- STEP 3: DISPLAY RESULTS ----------
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")

# if __name__ == "__main__":
#     main()

# Testing Code for Document Comparision
# import io
# from pathlib import Path
# from src.documentcomparision.data_ingestion import DocumentCompare
# from src.documentcomparision.doc_compare import DocumentcompareLLM

# def load_fake_uploaded_file(file_path:Path):
#     return io.BytesIO(file_path.read_bytes())

# def test_compare_docuemnts():
#     ref_path = Path("data/document_compare/Long_Report_V1.pdf")
#     act_path = Path("/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/document_compare/Long_Report_V1.pdf")
    
#     class FakeUpload:
#         def __init__(self,file_path:Path):
#             self.name = file_path.name
#             self._buffer =  file_path.read_bytes()

#         def getbuffer(self):
#            return self._buffer
       
#     comparator = DocumentCompare()
#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)
    
#     ref_file, act_file = comparator.save_uploaded_file(ref_upload, act_upload)
#     combined_text = comparator.combine_documents()
    
#     print("\n Combined Text Preview (First 1000 chars):\n")
#     print(combined_text[:1000])
    
#     llm_comparator = DocumentcompareLLM()
#     comparison_df = llm_comparator.compare_documents(combined_text)
    
#     print("\n=== COMPARISON RESULT ===")
#     print(comparison_df.head())
    
# if __name__ == "__main__":
#     test_compare_docuemnts()

### 
# Testing Code for singlechat

# import sys
# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from src.singledocumentchat.data_ingestion import SingleDocIngestor
# from src.singledocumentchat.retrieval import ConversationalRAG
# from utils.model_loader import ModelLoader

# FAISS_INDEX_PATH = Path("faiss_index")

# # Dummy file wrapper to simulate an uploaded file, similar to Streamlit's UploadedFile
# class FakeUpload:
#     def __init__(self, file_path: Path):
#         self.name = file_path.name
#         self._data = file_path.read_bytes()

#     def read(self):
#         """Mimics the .read() method of a file-like object."""
#         return self._data

# def test_conversational_rag_on_pdf(pdf_path:str, question:str):
#     try:
#         model_loader = ModelLoader()
        
#         if FAISS_INDEX_PATH.exists():
#             print("Loading existing FAISS index...")
#             embeddings = model_loader.load_embeddings()
#             vectorstore = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH), embeddings=embeddings,allow_dangerous_deserialization=True)
#             retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
#         else:
#             # Step 2: Ingest document and create retriever
#             print("FAISS index not found. Ingesting PDF and creating index...")
#             pdf_file = Path(pdf_path)
#             fake_uploaded_file = FakeUpload(pdf_file)
#             ingestor = SingleDocIngestor()
#             retriever = ingestor.ingest_files([fake_uploaded_file])

#         print("Running Conversational RAG...")
#         session_id = "test_conversational_rag"
#         rag = ConversationalRAG(retriever=retriever, session_id=session_id)
#         response = rag.invoke(question)
#         print(f"\nQuestion: {question}\nAnswer: {response}")
                    
#     except Exception as e:
#         print(f"Test failed: {str(e)}")
#         sys.exit(1)
    
# if __name__ == "__main__":
#     # Example PDF path and question
#     pdf_path = "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/single_document/sample.pdf"
#     question = "Explain the significance of attention mechanism in simple terms?"

#     if not Path(pdf_path).exists():
#         print(f"PDF file does not exist at: {pdf_path}")
#         sys.exit(1)
    
#     # Run the test
#     test_conversational_rag_on_pdf(pdf_path, question)

## Tesing for multidoc chat
from pathlib import Path
import sys
from src.multidocumentchat.data_ingestion import DocumentIngestor
from src.multidocumentchat.retrieval import ConversationalRAG

print("Testing for MultiDocumentChat")
def test_document_ingestion_and_rag():
    try:
        test_files = [
            "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/multi_document/market_analysis_report.docx",
            "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/multi_document/NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/multi_document/sample.pdf",
            "/Users/uw-user/Documents/AI-2025/LLMOps/Document-Portal/data/multi_document/state_of_the_union.txt"
        ]

        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File not found: {file_path}")

        if not uploaded_files:
            print("No valid files found for testing.")
            sys.exit(1)

        ingestor = DocumentIngestor()
        retriever = ingestor.ingest_files(uploaded_files)

        for file in uploaded_files:
            file.close()
        
        session_id = "test_document_ingestion_and_rag"
        rag = ConversationalRAG(session_id=session_id, retriever=retriever)

        question = "What is the summary of attention is all you need"
        answer = rag.invoke(question)
        print(f"\nQuestion: {question}\nAnswer: {answer}")

    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_document_ingestion_and_rag()
