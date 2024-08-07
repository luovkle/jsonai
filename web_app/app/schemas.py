from pydantic import BaseModel, Field


class TopicRead(BaseModel):
    topic_id: str = Field(alias="_id")
    topic: str
