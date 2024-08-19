from typing import Any

from pydantic import BaseModel, Field, create_model


class TopicRead(BaseModel):
    topic_id: str = Field(alias="_id")
    topic: str


def generate_model(model_name: str, data: dict[str, Any]) -> type[BaseModel]:
    def parse_value(value: Any) -> Any:
        if isinstance(value, dict):
            return (generate_model(f"{model_name}SubModel", value), ...)
        elif isinstance(value, list) and value:
            list_item_type: Any = parse_value(value[0])[0]
            return (list[list_item_type], ...)
        elif isinstance(value, list):
            return (list[Any], ...)
        else:
            return (type(value), ...)

    fields = {key: parse_value(value) for key, value in data.items()}
    return create_model(model_name, **fields)
