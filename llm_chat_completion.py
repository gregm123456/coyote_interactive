import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import config
from openai import AzureOpenAI
import json
import requests


def chat_completion_azure(conversation_file):
    # Load conversation messages from file
    with open(conversation_file, "r") as f:
        messages = json.load(f)

    client = AzureOpenAI(
        azure_endpoint=config.AZURE_OPENAI_GPT4_ENDPOINT,
        api_key=config.AZURE_OPENAI_GPT4_KEY,
        api_version="2024-02-15-preview"
        )

    completion = client.chat.completions.create(
        model=config.AZURE_MODEL,
        messages=messages,
        temperature=0.9,
        max_tokens=config.AZURE_MAX_TOKENS,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
        )

    response = completion.choices[0].message.content
    print("\n")
    print(response)
    print("\n")

    return response


def chat_completion_ollama(conversation_file):
    # Load conversation messages from file
    with open(conversation_file, "r") as f:
        messages = json.load(f)

    payload = {
        "model": config.OLLAMA_MODEL,
        "keep_alive": config.OLLAMA_KEEP_ALIVE,
        "stream": False,
        "options": {
            "temperature": config.OLLAMA_TEMPERATURE,
            "top_k": config.OLLAMA_TOP_K,
            "top_p": config.OLLAMA_TOP_P,
            "num_ctx": config.OLLAMA_NUM_CTX,
            "repeat_last_n": config.OLLAMA_REPEAT_LAST_N,
            "repeat_penalty": config.OLLAMA_REPEAT_PENALTY,
            "num_predict": config.OLLAMA_NUM_PREDICT,
            "stop": ["#", "["]
        },
        "messages": messages
    }

    llm_response = requests.post(config.OLLAMA_ENDPOINT, json=payload)
    llm_response_decoded = llm_response.content.decode()
    llm_response_json = json.loads(llm_response_decoded)

    response = llm_response_json['message']['content']
    print("\n")
    print(response)
    print("\n")

    return response


def llm_chat_completion(conversation_file):
    if config.LLM == "azure":
        return chat_completion_azure(conversation_file)
    elif config.LLM == "ollama":
        return chat_completion_ollama(conversation_file)
    # Fallback behavior
    return f"Default LLM response using conversation file: {conversation_file}"


