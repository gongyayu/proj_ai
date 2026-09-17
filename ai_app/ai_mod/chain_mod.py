#import os, sys
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from ollama import chat
import streamlit as st
from ai_mod.tools_mod import AGENT_TOOLS
from . import common_mod

SYSTEM_MESSAGE = (
    """You are a file assistant.

    Whenever the user asks to save, create, write, or update a file, you MUST use the write_to_file tool.

    Never pretend you wrote a file.
    Please always call the tool.
    """
)

def start_agent_chain(ollama_model,user_prompt,debug,selected_tools) -> str:
    #model = ChatOllama(model="qwen3.6:latest",temperature=0)
    model = ChatOllama(model=ollama_model,temperature=0)
    tools_selected_list = []
    for tool in AGENT_TOOLS:
        if tool.name in selected_tools:
            tools_selected_list.append(tool)

    agent = create_agent(model=model,tools=tools_selected_list,system_prompt=SYSTEM_MESSAGE)

    history: List[BaseMessage] = []

    response = run_agent(user_prompt, agent, history)
    st.write(response["messages"][-1].content)
    st.write('')

    if debug == 'Yes':
        #st.write(response)
        for resp in response["messages"]:
            st.write(type(resp).__name__)
            st.write(resp)
            st.write("=" * 50)
    #   st.write('input tokens: ',response.usage_metadata["input_tokens"])
    #   st.write('input tokens: ',response.usage_metadata["output_tokens"])
    #   st.write('total tokens: ',response.usage_metadata["total_tokens"])
    #elif debug == 'All':
    #    st.write(response)
    #elif debug == "Tool_call":
    #   pass
    #else:
    #    st.write(response["messages"][-1].content)
        st.write(f"{'-' * 30 }")
        for t in tools_selected_list:
            st.write(t)

def run_agent(user_input: str, agent, history: List[BaseMessage]) -> list:                # -> AIMessage:
    """Single-turn agent runner with automatic tool execution via LangGraph."""
    try:
        result = agent.invoke(
            {"messages": history + [HumanMessage(content=user_input)]},config={"recursion_limit": 50}
        )
        # test to see if tool is used 
        # for m in result["messages"]:
        #    print(type(m).__name__)
        #    print(m)
        #    print("=" * 50)
    
        # Return the last AI message
        #return result["messages"][-1]
        return result
    except Exception as e:
        # Return error as an AI message so the conversation can continue
        return AIMessage(content=f"Error: {str(e)}\n\nPlease try rephrasing your request or provide more specific details.")