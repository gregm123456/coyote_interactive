# Local development secrets template. Copy this file to config_secrets.py and fill in real values.

AZURE_OPENAI_GPT4_ENDPOINT = "your_azure_openai_gpt4_endpoint"
AZURE_OPENAI_GPT4_KEY = "your_azure_openai_gpt4_key"
AZURE_MODEL = "your_azure_model"
AZURE_MAX_TOKENS = 125
AZURE_OPENAI_DALLE_ENDPOINT = "your_azure_openai_dalle_endpoint"
AZURE_OPENAI_DALLE_KEY = "your_azure_dalle_key"

OLLAMA_ENDPOINT = "your_ollama_endpoint"
OLLAMA_MODEL = "your_ollama_model"
OLLAMA_KEEP_ALIVE = -1
OLLAMA_REPEAT_LAST_N = 64
OLLAMA_REPEAT_PENALTY = 1.5
OLLAMA_TEMPERATURE = 0.99
OLLAMA_TOP_K = 85
OLLAMA_TOP_P = 0.9
OLLAMA_NUM_CTX = 1024
OLLAMA_IMAGE_CLASSIFIER_MODEL = "your_ollama_image_classifier_model"
OLLAMA_NUM_PREDICT = 100
OLLAMA_CACHE_PROMPT = False

AX650_GENERATE_ENDPOINT = "http://localhost:11434/api/generate"
AX650_RUNTIME_STOP_ENDPOINT = "http://127.0.0.1:8000/api/stop"
AX650_RUNTIME_RESET_ENDPOINT = "http://127.0.0.1:8000/api/reset"
AX650_MODEL = "qwen3-ax650"
AX650_TIMEOUT_SECONDS = 30
