import os

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, APITimeoutError, Groq

from config import GROQ_MODEL_ID, TEMPERATURE


def generate(prompt):
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Create a .env file and add GROQ_API_KEY before asking questions.")

    model_id = os.getenv("GROQ_MODEL_ID", GROQ_MODEL_ID)
    client = Groq(api_key=api_key, timeout=45.0)

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
        )
    except APIStatusError as error:
        raise RuntimeError(
            f"Groq request failed (HTTP {error.status_code}): {error.message}"
        ) from error
    except (APITimeoutError, APIConnectionError, TimeoutError, ConnectionError) as error:
        raise RuntimeError(
            "Groq did not respond within 45 seconds. Check your connection and try again."
        ) from error

    content = (
        response.choices[0].message.content
        if response.choices and response.choices[0].message
        else None
    )
    if not content or not content.strip():
        raise RuntimeError("Groq returned an empty answer. Please try again.")
    return content.strip()
