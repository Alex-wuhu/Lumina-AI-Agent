#from LLM_service import 
import os
import json
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from uuid import uuid4
from app.services.scraping_service import Pdf_handler,Markdown_hander
EMBEDDING_DIMENSION = 1536
RAG_PATH = os.path.abspath(os.path.dirname(__file__) + "/../RAG_Doc/")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def get_chroma_vector_store():
    vector_store = Chroma(
        collection_name="test_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
        )
    return vector_store


def local_Rag():
   trained_files = RAG_PATH+("/trained_fils.json")
   print(trained_files)
   with open(trained_files) as file:
       files_json = json.load(file)
       for i in files_json["Files"]:
           print(i)
           print("trained resouce : "+i["name"])
           print("path : "+RAG_PATH+i["path"])
           if "md" in i["path"]:
                cur_doc = Markdown_hander(RAG_PATH+i["path"])
           else:
                cur_doc = Pdf_handler(RAG_PATH+i["path"])
           embed_chunks_and_upload_to_Chroma(cur_doc)
           break
   print("train finished")        
   

def embed_chunks_and_upload_to_Chroma(documents):
    vector_store = get_chroma_vector_store()
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    print(f"\nUploaded {len(documents)} chunks .")


