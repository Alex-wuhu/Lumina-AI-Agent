#from LLM_service import 
import os
from langchain_chroma import Chroma
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from uuid import uuid4
from langchain_core.documents import Document
from scraping_service import Pdf_handler
EMBEDDING_DIMENSION = 1536

def get_chroma_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
    )
    return vector_store


def local_Rag():
   parent_dir = os.path.abspath(os.path.dirname(__file__) + "/../RAG_Doc/bitcoin.pdf")
   #pdf1 = Path(__file__).parent+"//RAG_Doc//bitcoin.pdf"
   print("trained resouce : "+parent_dir)
   
   document1 = Pdf_handler(parent_dir)
   embed_chunks_and_upload_to_Chroma(document1)

def embed_chunks_and_upload_to_Chroma(documents):
    vector_store = get_chroma_vector_store()
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    print(f"\nUploaded {len(documents)} chunks .")



