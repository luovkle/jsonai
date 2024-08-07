from typing import TypedDict

FoundTopics = TypedDict(
    "FoundTopics",
    {
        "topics": list[dict],
        "preview": int | None,
        "next": int | None,
    },
)
