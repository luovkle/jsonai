import re

import orjson
from openai import OpenAI

from app.config import settings
from app.exceptions import ChatGPTCompletionError, JSONExtractionError

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def extract_json_from_completion(topic_id: str, completion: str) -> list[dict]:
    pattern = r"```json\s*(\[\s*\{.*?\}\s*\])\s*```"
    match = re.search(pattern, completion, re.DOTALL)
    if not match:
        raise JSONExtractionError(
            f"The completion of topic {topic_id} does not match the pattern"
        )
    try:
        json_data = orjson.loads(match.group(1))
    except orjson.JSONDecodeError:
        raise JSONExtractionError(f"Error decoding the JSON of topic {topic_id}")
    return json_data


def generate_prompt(topic: str) -> str:
    return (
        f"Generate a detailed and informative list of JSON objects based on the topic "
        f"'{topic}'. Each JSON object should contain relevant information and "
        f"attributes related to '{topic}'. Ensure the list is comprehensive, diverse, "
        "and accurately represents the topic."
    )


def generate_completion(topic_id: str, prompt: str) -> str:
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in generating realistic JSON mockups.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        max_tokens=settings.OPENAI_MAX_TOKENS,
    )
    content = completion.choices[0].message.content
    if not content:
        raise ChatGPTCompletionError(
            f"An error occurred while generating the completion for topic {topic_id}"
        )
    return content


def generate_data(topic_id: str, topic: str) -> list[dict]:
    prompt = generate_prompt(topic)
    completion = generate_completion(topic_id, prompt)
    return extract_json_from_completion(topic_id, completion)
