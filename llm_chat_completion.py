import sys
import config
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')


AX650_FALLBACK_RESPONSE = "Sorry, I had trouble generating a response."


def _load_messages(conversation_file):
    with open(conversation_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _latest_user_prompt(messages):
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        prompt = (message.get("content") or "").strip()
        if prompt:
            return prompt
    return None


def chat_completion_azure(conversation_file):
    # Load conversation messages from file
    messages = _load_messages(conversation_file)

    from openai import AzureOpenAI

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
    messages = _load_messages(conversation_file)

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


def chat_completion_ax650(conversation_file):
    timeout = getattr(config, "AX650_TIMEOUT_SECONDS", 30)
    endpoint = getattr(config, "AX650_GENERATE_ENDPOINT", "http://localhost:11434/api/generate")
    model = getattr(config, "AX650_MODEL", "qwen3-ax650")

    try:
        messages = _load_messages(conversation_file)
        prompt = _latest_user_prompt(messages)
        if not prompt:
            print("AX650 error: no latest user prompt found in conversation.")
            return AX650_FALLBACK_RESPONSE

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        llm_response = requests.post(endpoint, json=payload, timeout=timeout)
        llm_response.raise_for_status()
        llm_response_json = llm_response.json()

        response = (llm_response_json.get("response") or "").strip()
        if not response:
            print(f"AX650 error: missing or empty 'response' field from {endpoint}.")
            return AX650_FALLBACK_RESPONSE

        print("\n")
        print(response)
        print("\n")
        return response
    except Exception as e:
        print(f"AX650 generation error at {endpoint}: {e}")
        return AX650_FALLBACK_RESPONSE


def ax650_soft_reset_and_reassert_prompt():
    timeout = getattr(config, "AX650_TIMEOUT_SECONDS", 30)
    stop_endpoint = getattr(config, "AX650_RUNTIME_STOP_ENDPOINT", "http://127.0.0.1:8000/api/stop")
    reset_endpoint = getattr(config, "AX650_RUNTIME_RESET_ENDPOINT", "http://127.0.0.1:8000/api/reset")
    reset_payload = {"system_prompt": config.SYSTEM_MESSAGE_TEXT}

    ok = True

    try:
        requests.get(stop_endpoint, timeout=timeout).raise_for_status()
        print(f"AX650 runtime stop OK: {stop_endpoint}")
    except Exception as e:
        ok = False
        print(f"AX650 runtime stop failed at {stop_endpoint}: {e}")

    try:
        requests.post(reset_endpoint, json=reset_payload, timeout=timeout).raise_for_status()
        print(f"AX650 runtime reset OK: {reset_endpoint}")
    except Exception as e:
        ok = False
        print(f"AX650 runtime reset failed at {reset_endpoint}: {e}")

    return ok


def llm_chat_completion(conversation_file):
    if config.LLM == "azure":
        return chat_completion_azure(conversation_file)
    elif config.LLM == "ollama":
        return chat_completion_ollama(conversation_file)
    elif config.LLM == "ax650":
        return chat_completion_ax650(conversation_file)
    # Fallback behavior
    return f"Default LLM response using conversation file: {conversation_file}"


