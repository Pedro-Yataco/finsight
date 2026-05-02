import os
from langchain_core.language_models import BaseChatModel


def get_llm() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "ollama")

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
        return ChatOllama(model=model, base_url=base_url, num_ctx=num_ctx)

    if provider == "groq":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        return ChatGoogleGenerativeAI(model=model)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-haiku-4-5-20251001")

    raise ValueError(
        f"Unknown LLM_PROVIDER: '{provider}'. Use 'ollama', 'groq', 'gemini', or 'anthropic'."
    )
