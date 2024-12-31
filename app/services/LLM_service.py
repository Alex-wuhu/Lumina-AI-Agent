from langchain_openai import ChatOpenAI 
from langgraph.checkpoint.memory import MemorySaver
import os
from app.utils.tools import GetTools
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

def get_response(question):
  config = {"configurable": {"thread_id": "test11","recursion_limit": 10}}
  graph = GraphBuilder()
  events = graph.stream(
    {"messages": [("user", question)]}, config, stream_mode="values"
   )
  for event in events:
      event["messages"][-1].pretty_print()
  return 



class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
   llm = ChatOpenAI(api_key="sk-", base_url="https://api.deepseek.com",model="deepseek-chat")
   return {"messages": [llm.invoke(state["messages"])]}
def Transactionbot(state: State):
   llm = ChatOpenAI(api_key="sk-", base_url="https://api.deepseek.com",model="deepseek-chat")
   llm_with_tools = llm.bind_tools(GetTools())
   return {"messages": [llm_with_tools.invoke(state["messages"])]}


def GraphBuilder():
   tool_node = ToolNode(GetTools())
   memory = MemorySaver()
   graph_builder = StateGraph(State)
   graph_builder.add_node("chatbot", chatbot)
   graph_builder.add_node("Transactionbot", Transactionbot)
   graph_builder.add_node("tools", tool_node)
   # Add edge from chatbot to Transactionbot
   graph_builder.add_edge("chatbot", "Transactionbot")
   graph_builder.add_conditional_edges(
    "Transactionbot",
    tools_condition,
   )
   graph_builder.set_entry_point("chatbot")
   graph = graph_builder.compile(checkpointer=memory)
   return graph