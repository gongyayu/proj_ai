import requests
import json
from . import common_mod
from .common_mod import st_code, st_print, line_print, code_print
import streamlit as st


def calculator(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Calculator error: {e}"


def get_weather(city):
    # Just a fake tool for demonstration
    return f"The weather in {city} is sunny, 72°F."


TOOLS = {
    "calculator": calculator,
    "get_weather": get_weather,
}


def call_llm(llm, messages):

    payload = {
        "model": llm,
        "messages": messages,
        "stream": False,
    }

    response = requests.post(
        common_mod.ollama_URL,
        json=payload
    )

    st_code(f"Response: {response}")

    response.raise_for_status()
    st_code(f"Response: {response.json()['message']}")
    return response.json()["message"]


def harness_agent(llm, user_input):

    system_message = """
    You are an AI agent.
    You can use these tools:
    calculator(expression)
    get_weather(city)

    When you need a tool, respond EXACTLY like this:
    TOOL: calculator
    ARGS: {"expression": "25 * 4"}
    or:
    TOOL: get_weather
    ARGS: {"city": "Seattle"}

    If you don't need a tool, respond normally.
    """

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    message = call_llm(llm, messages)
    assistant_text = message["content"]

    st_code(f"LLM:\n {assistant_text}")

    if not assistant_text.startswith("TOOL:"):
        return assistant_text

    lines = assistant_text.splitlines()
    tool_name = lines[0].replace("TOOL:", "").strip()

    args_text = lines[1].replace("ARGS:", "").strip()

    args = json.loads(args_text)

    st_code(f"HARNESS: Calling tool: {tool_name}")
    st_code(f"Arguments: {args}")

    tool = TOOLS.get(tool_name)

    if tool is None:
        tool_result = f"Unknown tool: {tool_name}"
    else:
        tool_result = tool(**args)

    return f"Tool result: {tool_result}"

    messages.append({
        "role": "assistant",
        "content": assistant_text
    })

    messages.append({
        "role": "user",
        "content": f"""
            Tool result: 
            {tool_result}
            Use this result to continue solving the user's request.
        """
    })
