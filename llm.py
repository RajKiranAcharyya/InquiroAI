import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from config import GEMINI_MODEL, TEMPERATURE


def generate(prompt):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Create a .env file and add GEMINI_API_KEY before asking questions.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=45000),
    )
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=TEMPERATURE),
        )
    except errors.APIError as error:
        raise RuntimeError(
            f"Gemini request failed (HTTP {error.code}): {error.message}"
        ) from error
    except (TimeoutError, ConnectionError) as error:
        raise RuntimeError(
            "Gemini did not respond within 45 seconds. Check your connection and try again."
        ) from error

    if not response.text:
        raise RuntimeError("Gemini returned an empty answer. Please try again.")
    return response.text.strip()
