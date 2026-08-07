from __future__ import annotations

from google.genai import types

from generate.models import GeneratedWord


def build_response_schema() -> types.Schema:
    json_schema = types.JSONSchema(**GeneratedWord.model_json_schema())
    word_schema = types.Schema.from_json_schema(json_schema=json_schema)
    return types.Schema(type=types.Type.ARRAY, items=word_schema)
