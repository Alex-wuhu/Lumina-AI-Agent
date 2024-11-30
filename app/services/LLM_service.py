from langchain_openai import ChatOpenAI 
import os
from Chroma_service import get_chroma_vector_store,local_Rag
from langchain.chains import RetrievalQA
from pathlib import Path
#from app.utils.helper_functions import build_prompt, construct_messages_list

PROMPT_LIMIT = 3750



def get_response(question):
  llm = ChatOpenAI(api_key="sk-###", base_url="https://api.deepseek.com",model="deepseek-chat")
  db_path = Path(__file__).parent.parent.parent.parent/"chroma_langchain_db"
  # if Vector_db not exist , trained data first
  if(os.path.exists(db_path) == False):
     local_Rag()
  vector_store = get_chroma_vector_store()
    # Create a RetrievalQA chain
  qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(),
    return_source_documents=True
    )
  response = qa_chain({"query": question})
  return response
  



'''


def construct_llm_payload(question, context_chunks, chat_history):
  
  # Build the prompt with the context chunks and user's query
  prompt = build_prompt(question, context_chunks)
  print("\n==== PROMPT ====\n")
  print(prompt)

  # Construct messages array to send to OpenAI
  messages = construct_messages_list(chat_history, prompt)

  # Construct headers including the API key
  headers = {
      'content-type': 'application/json; charset=utf-8',
      'Authorization': f"Bearer {OPENAI_API_KEY}"            
  }  

  # Construct data payload
  data = {
      'model': CHATGPT_MODEL,
      'messages': messages,
      'temperature': 1, 
      'max_tokens': 1000,
      'stream': True
  }

  return headers, data

'''

