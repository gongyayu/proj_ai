from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_ollama import ChatOllama
from ollama import chat
import streamlit as st
import asyncio
import aiohttp
import requests
# from ai_mod.tools_mod import TOOLS
# from ai_mod import common_mod


def client_chat(ollama_model, user_prompt, debug, model_think) -> str:
    if debug == 'Yes':
        response = chat(
            model=ollama_model,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            think=model_think
        )
        st.write(response['message']['content'])
        st.write('More response information:')
        st.write('-' * 50)
        st.write(response)
    else:
        response = chat(
            model=ollama_model,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )

        def generate():
            for chunk in response:
                yield chunk["message"]["content"]
        st.write_stream(generate)

        return ('Done!')


def aiohttp_chat(ollama_model, user_prompt, debug, model_URL) -> str:
    async def chat(prompt: str) -> str:
        payload = {
            "model": ollama_model,
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": False,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(model_URL, json=payload) as resp:
                result = await resp.json()
                if debug == 'Yes':
                    return result
                return result.get("message", {}).get("content", "no response")
    return asyncio.run(chat(user_prompt))


def requests_chat(ollama_model, user_prompt, debug, model_URL) -> str:
    import json

    def chat(prompt: str) -> str:
        payload = {
            "model": ollama_model,
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": False,
        }
        response = requests.post(model_URL, json=payload)
        if debug == 'Yes':
            return response.json().get("message")
        return response.json().get("message", {}).get("content", "no response")
    return chat(user_prompt)


def llama_chat(user_prompt) -> str:
    from llama_cpp import Llama
    model_path = "/Users/gongya/.ollama/models/blobs/sha256-e566218f2f25cfb315482a280283016bdb0c011f97e49cb327708c38fa075db5"
    llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": user_prompt}], max_tokens=50)
    print(response["choices"][0]["message"]["content"])
    # print(response)
    return response


def local_API_chat(ollama_model, user_prompt, debug) -> str:
    from openai import OpenAI

    # Replace with your Ollama API key if needed
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "user", "content": user_prompt}],
        stream=False
    )
    print(response)
    if debug == 'Yes':
        return response
    return response.choices[0].message.content
# local_API_chat("llama3.1:8b", "What is the capital of France?", "No")

def gemini_chat(llm_model, user_prompt, debug) -> str:
    import os
    from google import genai
    from google.genai import types

    # Initialize the client (automatically uses GEMINI_API_KEY environment variable)
    client = genai.Client()

    # Initialize a chat session with system instructions
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful, friendly AI assistant. Keep responses brief.",
            temperature=0.7,
        )
    )
    # Send message and receive response
    response = chat.send_message(user_prompt)
        
    return f"{response.text}"

def nvidia_chat(llm_model, user_prompt, debug) -> str:
    from openai import OpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()
    base_url = 'https://integrate.api.nvidia.com/v1/'
    api_key = os.getenv("NVIDIA_API_KEY")

    client = OpenAI(
        base_url = base_url,
        api_key = api_key
    )
    print(f"base_url: {base_url}")
    print(f"llm_mosel: {llm_model}")
    print(f"api_key is not None: {api_key is not None}")
    response = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def nvidia_request_chat(llm_model, user_prompt, debug) -> str:
    from dotenv import load_dotenv
    import requests
    import os
    import json

    API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": llm_model,
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": 2048,
        "stream": True,
        "temperature": 1.0,
    }

    #print(f"API_URL: {API_URL}")
    #print(f"llm_mosel: {llm_model}")
    #print(f"api_key is not None: {api_key is not None}")
    
    #resp = requests.post(API_URL, headers=headers, json=body, stream=True)
    resp = requests.post(API_URL, headers=headers, json=body)
    # print(resp.text)

    #print(f"resp.raise_for_status(): {resp.raise_for_status()}")
    #print(f"resp.text: {resp.text}")
    response = ''
    for line in resp.iter_lines():
        if not line or not line.startswith(b"data: "):
            continue
        data = line[6:]
        if data == b"[DONE]":
            break
        chunk = json.loads(data)
        if chunk["choices"]:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                #print(delta["content"], end="", flush=True)
                response += delta["content"]
    return response

    


