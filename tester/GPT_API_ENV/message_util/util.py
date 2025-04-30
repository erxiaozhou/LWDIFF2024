import numpy as np
from openai import OpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse
from ..project_cfg import text2embedding_model_name
from ..api_util import api_key
from ..api_util import MODEL_VERSION
from ..api_util import base_url


MAX_EBD_TOKEN_NUM = 8192


def text_oversize(text):
    return len(text) > MAX_EBD_TOKEN_NUM


def get_client():
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    return client


def ask_and_get_question(messages: list, mode_name=MODEL_VERSION):
    assert 0, print('Cur mode_name is ', mode_name)
    response = get_response(messages, mode_name=mode_name)
    
    return get_text_from_response(response)


def get_response(messages, mode_name=MODEL_VERSION):
    client = get_client()
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=mode_name,
        temperature=0
    )
    return chat_completion


def get_embedding(content, model_name=text2embedding_model_name):
    client = get_client()
    result = client.embeddings.create(
        model=model_name,
        input=content,
        encoding_format="float"
    )
    return result


def get_text_from_response(response):
    return response.choices[0].message.content.strip()


def get_emb_array_from_text(text):
    response: CreateEmbeddingResponse = get_embedding(text)
    embedding = np.array(response.data[0].embedding).astype(
        'float32').reshape(1, -1)
    return embedding
