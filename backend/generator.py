import base64
from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import Path
from typing import Any

import openai
from PIL import Image

from backend.models.schemas import GenerationResponse, RetrievalResult


SYSTEM_PROMPT = "You are a precise document Q&A assistant. You are given:\n1. A page image from a technical document\n2. Relevant text chunks from the same document\n\nAnswer the user's question using BOTH the visual content of the image (charts, diagrams, figures, tables) AND the text. If the answer comes from a figure or diagram, describe what you see visually. Cite the page number. If the answer is not in the provided context, say so explicitly. Do not hallucinate."
_client = openai.AsyncOpenAI()


async def generate_answer(
    query: str,
    retrieval_result: RetrievalResult,
    stream: bool = False,
) -> GenerationResponse | AsyncIterator[str]:
    image_path = (
        Path(retrieval_result.top_pages[0]["image_path"])
        if retrieval_result.top_pages
        else None
    )
    used_image = image_path is not None and image_path.exists()
    encoded = _encode_image_as_png(image_path) if used_image else None

    text_context = "\n\n".join(
        chunk["text"] for chunk in retrieval_result.top_chunks[:3]
    )[:2000]
    content_list: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": f"Question: {query}\n\nContext:\n{text_context}",
        }
    ]
    if used_image:
        content_list.append(
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{encoded}",
            }
        )

    client = _client

    if stream:
        return _stream_response(client, content_list)

    response = await client.responses.create(
        model="gpt-5.4-mini-2026-03-17",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": content_list,
            }
        ],
    )
    sources = [
        {"page_num": page["page_num"], "doc_id": page["doc_id"]}
        for page in retrieval_result.top_pages
    ]
    return GenerationResponse(
        answer=response.output_text,
        sources=sources,
        used_image=used_image,
    )


async def _stream_response(
    client: Any,
    content_list: list[dict[str, Any]],
) -> AsyncIterator[str]:
    stream = await client.responses.create(
        model="gpt-5.4-mini-2026-03-17",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": content_list,
            }
        ],
        stream=True,
    )
    async for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


def _encode_image_as_png(image_path: Path) -> str:
    buffer = BytesIO()
    with Image.open(image_path) as image:
        image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
