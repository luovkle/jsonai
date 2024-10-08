import re

import orjson
from flask import current_app
from openai import OpenAI

from app.config import settings
from app.db import db_save_completion
from app.exceptions import ChatGPTCompletionError, JSONExtractionError

client = OpenAI(api_key=settings.OPENAI_API_KEY)

pattern_match_error_template = (
    "The completion of topic {topic_id} does not match the pattern"
)
json_decoding_error_template = "Error decoding the JSON of topic {topic_id}"
chatgpt_completion_error_template = (
    "An error occurred while generating the completion for topic {topic_id}"
)


def extract_json_from_completion(topic_id: str, completion: str) -> list[dict]:
    pattern = r"```json\s*(\[\s*\{.*?\}\s*\])\s*```"
    match = re.search(pattern, completion, re.DOTALL)
    if not match:
        current_app.logger.error(pattern_match_error_template.format(topic_id=topic_id))
        raise JSONExtractionError(
            pattern_match_error_template.format(topic_id=topic_id)
        )
    try:
        json_data = orjson.loads(match.group(1))
    except orjson.JSONDecodeError:
        current_app.logger.error(json_decoding_error_template.format(topic_id=topic_id))
        raise JSONExtractionError(
            json_decoding_error_template.format(topic_id=topic_id)
        )
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
        current_app.logger.error(
            chatgpt_completion_error_template.format(topic_id=topic_id)
        )
        raise ChatGPTCompletionError(
            chatgpt_completion_error_template.format(topic_id=topic_id)
        )
    return content


def generate_data(topic_id: str, topic: str) -> list[dict]:
    prompt = generate_prompt(topic)
    completion = generate_completion(topic_id, prompt)
    try:
        data = extract_json_from_completion(topic_id, completion)
    except (ChatGPTCompletionError, JSONExtractionError) as e:
        db_save_completion(topic_id, prompt, completion, error=str(e))
        raise
    db_save_completion(topic_id, prompt, completion)
    return data
