# 
# from Agentic_RAG才是未来碾压传统_RAG_Agentic_RAG才是未来碾压传统_RAG_带你
#
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ollama import chat, ChatResponse

load_dotenv()

def classic_rag(llm_model, user_prompt, debug):
    EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    GEN_MODEL = "google/flan-t5-base"

    print(os.getcwd())
    loader = TextLoader("data/input/company_vacation_policy.txt", encoding="utf8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=100, chunk_overlap=0)
    splits = text_splitter.split_documents(documents)

    embedder = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedder,
        persist_directory="data/chroma_db",
    )

    # user_prompt = "What is the company's vacation policy?"
    docs = vectorstore.similarity_search(user_prompt, k=3)



    context = "\n".join(f"- {doc.page_content}" for doc in docs)

    prompt_template = """
    "Answer the question using only the context below.\n"
    "If the answer is not in the context, say you don't know.\n\n"
    f"Context:\n{context}\n\n"
    f"Question: {user_prompt}\n"
    "Answer:"
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "user_prompt"])
    final_prompt = prompt.format(context=context, user_prompt=user_prompt)

    #
    # gemini-3.6-flash
    #
    if llm_model == 'gemini-3.6-flash':
        client = genai.Client()
        gemini_chat = client.chats.create(
            # model="gemini-3.6-flash",
            model=llm_model,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful, friendly AI assistant. Keep responses brief.",
                temperature=0.7,
            )
        )
        response = gemini_chat.send_message(final_prompt)
    else:
    #
    # ollama
    #
        response: ChatResponse = chat(model=llm_model, messages=[
                                        {"role": "user", "content": final_prompt}])
    if debug:
        print(f"Context:\n{context}\n")
        print(f"Prompt:\n{final_prompt}\n")
        print(f"User: {user_prompt}\n")
        if llm_model == 'gemini-3.6-flash':
            print(f"Bot (gemini): {response.text}\n")
        else:
            print(f"Bot: {response}\n")
    if llm_model == 'gemini-3.6-flash':
        return response.text  
    else:
        return response['message']['content']