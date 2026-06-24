from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    MultiVectorComparator,
    MultiVectorConfig,
    PayloadSchemaType,
    VectorParams,
)

from backend.models.config import Settings


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    settings = settings or Settings()
    kwargs: dict[str, str] = {"url": settings.qdrant_url}

    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key

    return QdrantClient(**kwargs)


def ensure_collections(client: QdrantClient) -> None:
    settings = Settings()

    if not client.collection_exists(settings.image_collection):
        client.create_collection(
            collection_name=settings.image_collection,
            vectors_config=VectorParams(
                size=128,
                distance=Distance.DOT,
                multivector_config=MultiVectorConfig(
                    comparator=MultiVectorComparator.MAX_SIM,
                ),
            ),
        )

    if not client.collection_exists(settings.text_collection):
        client.create_collection(
            collection_name=settings.text_collection,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE,
            ),
        )

    for collection_name in (settings.image_collection, settings.text_collection):
        for field_name, field_schema in [
            ("doc_id", PayloadSchemaType.KEYWORD),
            ("page_num", PayloadSchemaType.INTEGER),
        ]:
            try:
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_schema,
                )
            except UnexpectedResponse:
                pass
