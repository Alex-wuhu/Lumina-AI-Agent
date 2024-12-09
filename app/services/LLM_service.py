from langchain_openai import ChatOpenAI 
import os
from app.services.Chroma_service import get_chroma_vector_store,local_Rag
from pathlib import Path
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain import hub
from langgraph.graph import START, StateGraph
PROMPT_LIMIT = 3750


def get_response(question):
  g = GraphBuilder()
  response = g.invoke({"question": question})
  return response


## graph related
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
def retrieve(state: State):
    # if Vector_db not exist , trained data first
    db_path = Path(__file__).parent.parent.parent.parent/"chroma_langchain_db"
    if(os.path.exists(db_path) == False):
      local_Rag()
    vector_store = get_chroma_vector_store()
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}
def generate(state: State):
    llm = ChatOpenAI(api_key="sk-xxx", base_url="https://api.deepseek.com",model="deepseek-chat")
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    prompt = hub.pull("rlm/rag-prompt")
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}
def GraphBuilder():
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    print("return graph model")
    return graph
