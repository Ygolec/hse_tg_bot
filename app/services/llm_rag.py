import os
import logging
import requests
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

def get_llm_rag_url() -> str:
    url = os.getenv("LLM_RAG_API_URL")
    if not url:
        logger.error("LLM RAG API URL not found in environment variables")
        raise ValueError("LLM_RAG_API_URL environment variable is not set")
    return url


def ask_llm_rag(question: str) -> Dict[str, Any]:

    base_url = get_llm_rag_url()

    url = f"{base_url.rstrip('/')}/ask"

    headers = {
        "Content-Type": "application/json"
    }


    payload = {
        "question": question,
        "directory": "instruction_documents"
    }

    try:
        logger.info(f"Sending question to LLM RAG API: {question}")
        logger.info(f"API URL: {url}")

        response = requests.post(url, headers=headers, json=payload, timeout=300)

        logger.info(f"API response status code: {response.status_code}")

        logger.info(f"API response text: {response.text[:500]}...")

        response.raise_for_status()


        try:
            return response.json()
        except ValueError as json_err:
            logger.error(f"Error parsing JSON response: {json_err}")

            return {"text": response.text}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to LLM RAG API: {e}")

        return {"error": str(e), "detail": "Не удалось подключиться к серверу нейросети. Пожалуйста, попробуйте позже."}
