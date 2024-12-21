from langchain_openai import ChatOpenAI 
from langgraph.checkpoint.memory import MemorySaver
import os
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain import hub
from app.utils.tools import GetTools

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
def get_response(question):
  agent = AgentBuilder()
  config = {"configurable": {"thread_id": "abc123"}}
  response = agent.invoke(
        {"messages": [HumanMessage(content=question)]},config=config
    )
  return response
def AgentBuilder():
    memory = MemorySaver()
    llm = ChatOpenAI(api_key="sk-afd1a5f77a4242059fe9a7fc42cc0f88", base_url="https://api.deepseek.com",model="deepseek-chat")
    tools = GetTools()
    prompt = hub.pull("hwchase17/react")
    agent_executor = create_react_agent(llm, tools, checkpointer=memory,prompt = prompt)
    
    return agent_executor

