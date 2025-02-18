import sys
# reconfigure stdout to use UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
import time
import config
from openai import AzureOpenAI
import json
import re  # added re import

def clean_response(response):
    sentence_endings = [".", "!", "?"]
    last_ending_index = max(response.rfind(ending) for ending in sentence_endings)
    if last_ending_index != -1:
        response = response[:last_ending_index+1]


    response = response.strip()
    response = response.replace("*", "")
    response = response.replace("‘", "").replace("’", "").replace("'", "")
    response = response.replace('"', "")
    # Escape the string for JSON
    cleaned = json.dumps(response)
    return cleaned

def chat_completion_azure(conversation_file):
    # Load conversation messages from file
    with open(conversation_file, "r") as f:
        messages = json.load(f)
    url = config.AZURE_OPENAI_GPT4_ENDPOINT
    key = config.AZURE_OPENAI_GPT4_KEY
    model = config.AZURE_MODEL
    max_tokens = config.AZURE_MAX_TOKENS

    client = AzureOpenAI(
        azure_endpoint=url, 
        api_key=key,  
        api_version="2024-02-15-preview"
        )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.9,
        max_tokens=max_tokens,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
        )

    response = completion.choices[0].message.content
    cleaned_response = clean_response(response)
    
    print("\n")
    print("\n")
    print(cleaned_response)
    print("\n")
    print("\n")
    
    return cleaned_response

def chat_completion_ollama(conversation_file):
    # ...existing ollama chat completion logic...
    return f"Ollama LLM response for {conversation_file}"

def llm_chat_completion(conversation_file):
    if config.LLM == "azure":
        return chat_completion_azure(conversation_file)
    elif config.LLM == "ollama":
        return chat_completion_ollama(conversation_file)
    # Fallback behavior
    return f"Default LLM response using conversation file: {conversation_file}"


