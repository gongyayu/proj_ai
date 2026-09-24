import os
import sys
import time
import subprocess
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from ollama import chat
import streamlit as st
import asyncio
from ai_mod import common_mod, chat_mod, mcp_client_mod, react_mod, tokenrouter_mod
from ai_mod.common_mod import AsyncMCPBridge
from ai_mod.mcp_client_mod import ask_mcp
from ai_mod import harness_mod

from dotenv import load_dotenv

from ai_mod import chain_mod, tools_mod
load_dotenv()

SYSTEM_MESSAGE = (
    """You are a file assistant.

    Whenever the user asks to save, create, write, or update a file, you MUST use the write_to_file tool.

    Never pretend you wrote a file.
    Please always call the tool.
    """
)


@st.cache_resource
def get_mcp_bridge():
    return AsyncMCPBridge()


def main():
    st.set_page_config(page_title="AI Demos", layout="wide")
    st.title("AI Demos")

    if common_mod.options == False:
        button_title = 'To be confirmed'
    else:
        button_title = 'Confirmed'

    # print(common_mod.options)
    def selection_changed():
        common_mod.options = False

    def tool_changed():
        # Access the changed widget value via session_state
        common_mod.tools_selected = [
            tool.name for tool in tools_mod.AGENT_TOOLS
            if st.session_state.get(tool.name, False)
        ]
        st.session_state.selected_tools = common_mod.tools_selected
        common_mod.options = False

    provider = st.sidebar.selectbox("Select a Provider", common_mod.get_llm_providers(
    ), key="provider_select", on_change=selection_changed)

    model_list = common_mod.get_llm_models(provider)
    llm_model = st.sidebar.selectbox(
        "Select a Model", model_list, key="model_select", on_change=selection_changed)

    if llm_model in common_mod.get_ollama_models():
        response = subprocess.Popen(
            ["ollama", "show", llm_model], stdout=subprocess.PIPE, text=True)
        lines = f'{'-' * 20}\n Modle: {llm_model}<br>'
        for line in response.stdout:
            lines += line

    if llm_model == 'llama3.1:8b':
        model_think = None
    else:
        model_think = True

    service = st.sidebar.radio("Service", common_mod.service_types_list,
                               index=0, key="debug_radio_task", on_change=selection_changed)
    if service == 'Chat':
        chat_method = st.sidebar.radio(
            "chat_method", common_mod.chat_methods_list, index=0, key="chat_method", on_change=selection_changed)
    if service == 'Agent':
        sub_service = st.sidebar.radio("Agent Type", common_mod.agent_types_list,
                                       index=0, key="debug_radio_agent_type", on_change=selection_changed)
        if sub_service == 'Chain':
            toolidx = []
            with st.sidebar:
                col1, col2 = st.columns(2)
                for i, tool in enumerate(tools_mod.AGENT_TOOLS, 1):
                    if i % 2:
                        with col2:
                            st.checkbox(
                                tool.name, on_change=tool_changed, key=tool.name)
                    else:
                        with col1:
                            st.checkbox(
                                tool.name, on_change=tool_changed, key=tool.name)
    if service == 'Harness':
        # st.write("Harness service is under development and not available yet.")
        user_prompt = st.text_input("Enter your query: ")
        answer = harness_mod.harness_agent(llm_model, user_prompt)
        st.code(answer, language='python')
    # debug = st.sidebar.radio("debug",["No","Yes"],index=0,key="debug_radio_agent", on_change=selection_changed)
    debug_checked = st.sidebar.checkbox("Debug", on_change=selection_changed)
    if debug_checked:
        debug = 'Yes'
    else:
        debug = 'No'

    if st.sidebar.button('Confirm'):
        bridge = get_mcp_bridge()
        common_mod.options = True

    if common_mod.options == False:
        st.sidebar.write("--- Not confirmed yet")
    else:
        st.sidebar.write("--- Confirmed")

    if llm_model in common_mod.get_ollama_models():
        st.sidebar.write(lines, unsafe_allow_html=True)

    # user_prompt = st.text_input("Enter your query: ")

    # if user_prompt and common_mod.options:
    if common_mod.options:
        if service == 'Chat':
            user_prompt = st.text_input("Enter your query: ")
            if user_prompt:
                if chat_method == 'ChatClient':
                    start = time.time()
                    if provider == 'google':
                        st.write(chat_mod.gemini_chat(llm_model,user_prompt,debug))
                    elif provider == 'nvidia':
                        st.write(chat_mod.nvidia_chat(llm_model,user_prompt,debug))
                    else:
                        st.write(chat_mod.client_chat(llm_model,
                             user_prompt, debug, model_think))
                    end = time.time()
                    st.write(f'Time cost: {end - start:.2f} seconds')
                elif chat_method == 'aiohttp':
                    start = time.time()
                    st.write(chat_mod.aiohttp_chat(llm_model,
                             user_prompt, debug, common_mod.ollama_URL))
                    end = time.time()
                    st.write(f'Time cost: {end - start:.2f} seconds')
                elif chat_method == 'requests':
                    start = time.time()
                    if provider == 'ollama':
                        st.write(chat_mod.requests_chat(llm_model,
                                                        user_prompt, debug, common_mod.ollama_URL))
                    elif provider == 'tokenrouter':
                        st.write(tokenrouter_mod.send_routed_request(
                            user_prompt, mode="balanced"))
                    elif provider == 'nvidia':
                        st.write(chat_mod.nvidia_request_chat(llm_model,user_prompt, debug))
                    end = time.time()
                    st.write(f'Time cost: {end - start:.2f} seconds')
                else:
                    st.write(f'Unknown chat method')
        elif service == 'Agent':
            if sub_service == 'Chain':
                user_input = f'Please help me to correct a local python script name test.py and write the corrected one to a file'
                # gemma4:latest is tested against this prompt
                user_prompt = st.text_input(
                    "Enter your query: ", value=user_input)
                if user_prompt:
                    st.write(chain_mod.start_agent_chain(llm_model,
                             user_prompt, debug, common_mod.tools_selected))
            elif sub_service == 'Graph':
                user_prompt = st.text_input("Enter your query: ")
                if user_prompt:
                    st.write(chain_mod.start_graph(
                        llm_model, user_prompt, debug))
            elif sub_service == 'ReAct':
                react_mod.llm_model = llm_model
                react_mod.debug = debug
                user_input = f'I want to visit Lithuania. I am interested to see some good places there.'
                user_prompt = st.text_input(
                    "Enter your query: ", value=user_input)
                if user_prompt:
                    react_mod.query(user_prompt)
            elif sub_service == 'MCP':
                user_input = f"What is our company's vacation policy?"
                user_prompt = st.text_input(
                    "Enter your query: ", value=user_input)
                if user_prompt:
                    # response = asyncio.run(mcp_client_mod.ask_mcp(user_prompt, llm_model, debug))     # user_prompt = What is our company's vacation policy?
                    response, debug_info = bridge.run(
                        ask_mcp(user_prompt, llm_model, debug))
                    st.write('=' * 50)
                    st.write(response)
                    st.write('-' * 50)
                    for each in debug_info:
                        st.write(each)


if __name__ == "__main__":
    main()
