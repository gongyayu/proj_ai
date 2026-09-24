import subprocess
import asyncio
import threading
import streamlit as st

# variables
ollama_URL = "http://localhost:11434/api/chat"

options = False
outputdir = '/Users/gongya/Programming/mac_python/proj_ai/ai_app/data/output/'
inputdir = '/Users/gongya/Programming/mac_python/proj_ai/ai_app/data/input/'

agent_types_list = ['Chain', 'Graph', 'ReAct', 'MCP']
service_types_list = ['Chat', 'Agent', 'Harness']
chat_methods_list = ['ChatClient', 'aiohttp', 'requests']

tools_selected = []
outlines = ''
codelines = ''

main_title = {
    'ollama': 'ollama Demo',
    'Agent': 'Agent'
}

def get_ollama_models() -> list:
    model_list = []
    ret = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True
    )

    if ret:
        ln = 0
        for line in ret.stdout.split('\n'):
            if ln == 0:
                ln = 1
                continue
            if len(line) == 0:
                continue
            model_list.append(line.split()[0])
    return model_list

provider_models = {}
provider_models['ollama'] = get_ollama_models()
provider_models['tokenrouter'] = ['z-ai/glm-5.3-free']
provider_models['google'] = ['gemini-3.6-flash']
provider_models['nvidia'] = ['moonshotai/kimi-k3','deepseek-ai/deepseek-v4.1-flash','z-ai/glm-5.3','meta/muse-glimmer-30b']

def get_llm_providers() -> list:
    providersList = []
    for p in provider_models.keys():
        providersList.append(p)
    return providersList

def get_llm_models(provider) -> list:
    return provider_models[provider]

class AsyncMCPBridge:
    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        """
        Called by synchronous Streamlit code.

        Submit an async coroutine to the background
        event loop and wait for its result.
        """
        future = asyncio.run_coroutine_threadsafe(
            coro,
            self.loop
        )
        return future.result()

    def stop(self):
        self.loop.call_soon_threadsafe(
            self.loop.stop
        )

# streamlit wrapper


def line_print(out: str) -> str:
    global outlines
    outlines += out + '<br>'
    return outlines


def code_print(out: str) -> str:
    global codelines
    codelines += out + '\n'
    return codelines


def st_print(out: str):
    global outlines
    if _st:
        st.write(f'{out}', unsafe_allow_html=True)
        outlines = ''
    else:
        print(f'{out}')


def st_code(str):
    global codelines
    st.code(str, width='content', wrap_lines=True)
    codelines = ''
