import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Dict, List, Optional, Type, Tuple, Union, Any, Coroutine

import requests
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from .prompts import (
    MAX_VALIDATION_ERROR_TRY,
    SUMMARY_ROLE,
    SUMMARY_VALIDATION_RESOLVE_ROLE,
)
from .utils import Chunker, Tokenizer

summary_role = ""
loop_for_image = ""

## HeadersSchema
class HeadersSchema(BaseModel):
    authorization: str = Field(..., alias="Authorization")
    content_type: str = Field(default="application/json", alias="Content-Type")

    @classmethod
    def create(cls, api_key: str) -> "HeadersSchema":
        return cls(Authorization=f"Bearer {api_key}")

    class Config:
        populate_by_name = True


class MessageSchema(BaseModel):
    role: str
    content: str


class SummaryPayloadSchema(BaseModel):
    model: str
    messages: List[MessageSchema]
    temperature: float
    stream: bool
    max_completion_tokens: int = 2048
    response_format: Dict[str, str] = {"type": "json_object"}


class SummaryResponseSchema(BaseModel):
    summary: str
    characters: Dict[str, str]
    places: Dict[str, str]


class SummaryOutputSchema(SummaryResponseSchema):
    id: str


class SummaryContentSchema(BaseModel):
    past_context: str
    current_chapter: str
    character_list: Dict[str, str]
    places_list: Dict[str, str]


##Requests


class LlmApi(ABC):
    @abstractmethod
    def messages(
            self, content: str, character: Dict[str, str], places: Dict[str, str]
    ) -> List[MessageSchema]:
        pass

    @abstractmethod
    def get(self, message: List[MessageSchema]) -> str:
        pass

    @abstractmethod
    def validate_json(
            self, raw_data: str, schema: Type[BaseModel]
    ) -> Optional[Type[BaseModel]]:
        pass


@dataclass
class Summary:
    api_key: str
    url: str = "https://api.groq.com/openai/v1/chat/completions"
    role: str = (
        f"{SUMMARY_ROLE} follow given schema: {SummaryOutputSchema.schema()}"
    )
    validation_role: str = f"{SUMMARY_VALIDATION_RESOLVE_ROLE} Schema :{SummaryOutputSchema.schema()}"
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    stream: bool = False
    repetition_penalty: float = 1.5
    max_tokens: int = 6000

    def get_messages(
            self,
            content: str,
            previous_summary: str,
            characters: Dict[str, str],
            places: Dict[str, str],
    ) -> List[MessageSchema]:
        return [
            MessageSchema(role="system", content=self.role),
            MessageSchema(
                role="user",
                content=SummaryContentSchema(
                    past_context=previous_summary,
                    current_chapter=content,
                    character_list=characters,
                    places_list=places,
                ).json(by_alias=True),
            ),
        ]

    def validation_messages(self, input_text: str) -> List[MessageSchema]:
        return [
            MessageSchema(role="system", content=self.validation_role),
            MessageSchema(
                role="user",
                content=input_text,
            ),
        ]

    def get(self, messages: List[MessageSchema]) -> Tuple[int, str]:
        payload = SummaryPayloadSchema(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=self.stream,
        ).dict(by_alias=True)

        headers = HeadersSchema.create(api_key=self.api_key).dict(by_alias=True)
        response = requests.post(url=self.url, headers=headers, json=payload)
        code = response.status_code
        if code == 200:
            response_data = response.json()
            assistant_message = response_data["choices"][0]["message"]["content"]
            return code, assistant_message
        else:
            logger.warning(f"Error: {response.json()}")
            return code, "ERROR_API_CALL"

    def validate_json(
            self, raw_data: str, schema: Type[SummaryResponseSchema]
    ) -> Union[SummaryResponseSchema, bool]:
        """
        Validates JSON data against a provided Pydantic schema.

        :param raw_data: JSON string to be validated.
        :param schema: A Pydantic model class to validate against.
        :return: A tuple where the first element is a boolean indicating if there was an error,
                 and the second element is either the validated data or a list of error details.
        """
        try:
            parsed_data = json.loads(raw_data)
            validated_data = schema.parse_obj(parsed_data)
            return validated_data
        except (ValidationError, JSONDecodeError):
            logger.warning("ValidationError")
            return False


class SummaryLoop(BaseModel):
    content: List[Tuple[str, str]]
    summary: Summary
    summary_pool: List[SummaryOutputSchema] = Field(default_factory=list)
    chunked_content: List[Tuple[str, str, str]] = Field(default_factory=list)

    def initialize(self) -> Optional["SummaryLoop"]:
        hf_api = os.environ.get("HF_API")
        if not hf_api:
            logger.error("[SummaryLoop] HF_API Not defined ")
            return None

        self.summary_pool = [
            SummaryOutputSchema(
                summary="This is The first chapter There is No context",
                places={},
                characters={},
                id="",
            ),
        ]
        tokenizer = Tokenizer(api_key=hf_api)
        logger.trace("tokenizer set")
        chunker = Chunker(max_len=self.summary.max_tokens, tokenizer=tokenizer)
        logger.trace("Chunker set")
        self.chunked_content = chunker.chunk(content=self.content)
        logger.trace("Chapters Chunked")

        return self

    def run(self) -> None:
        """
        Assuming book comes in the form of ((id,title_chapter,chapter_content),...)
        """
        for idx, (id, title, content) in enumerate(self.chunked_content):
            past_context = self.summary_pool[idx]
            message = self.summary.get_messages(
                content=content,
                previous_summary=past_context.summary,
                characters=past_context.characters,
                places=past_context.places,
            )
            status_code, response = self.summary.get(messages=message)

            if status_code == 200:
                validated_response = self.summary.validate_json(
                    response, SummaryResponseSchema
                )

                if validated_response:
                    logger.trace(f"Chunk_{id=} Done")
                    self.summary_pool.append(
                        SummaryOutputSchema(
                            **(validated_response.dict(by_alias=True)), id=id
                        )
                    )
                    continue

                else:
                    output = self.handle_validation_error(response)
                    if output:
                        past_context = output
            elif status_code == 400:
                self.summary_pool.append(past_context)
                logger.warning(f"error getting {id=}")

    def handle_validation_error(self, input_text):
        message = self.summary.validation_messages(input_text)
        for _ in range(MAX_VALIDATION_ERROR_TRY):
            err, response = self.summary.get(messages=message)
            if not err:
                validated_response = self.summary.validate_json(
                    response, SummaryResponseSchema
                )
                if validated_response:
                    return validated_response
        logger.error("COULDN'T VALIDATE THE CHUNK, SKIPPING...")
        return None

    @property
    def get_summary_pool(self):
        return self.summary_pool


async def main(book_path) -> list[dict[str, str | dict[str, str]]] | None:
    from .reader import Ebook

    api = os.environ.get("GROQ_API")
    if not api:
        raise Exception("API NOT SET IN .env, HF_API=None")

    book = Ebook(book_path)
    chapter_content = book.get_chapters()

    summary = Summary(
        api_key=api,
    )

    looper = SummaryLoop(content=chapter_content, summary=summary).initialize()
    if not looper:
        return None
    looper.run()
    summary_results = []
    for i in looper.get_summary_pool:
        if not i.places or not i.characters:
            continue
        result = {
            "chapter_id": i.id,
            "summary": i.summary,
            "characters": {k: v for k, v in i.characters.items()},
            "places": {k: v for k, v in i.places.items()},
        }
        summary_results.append(result)

    return summary_results
