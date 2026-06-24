from pathlib import Path
from typing import Any

import torch
from PIL import Image
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
from tqdm import tqdm

from backend.ingest import ingest_pdf
from backend.models.config import Settings
from backend.models.schemas import RetrievalResult, Source


class MultimodalIndexer:
    def __init__(self, qdrant_client: Any, settings: Settings | None = None):
        from colpali_engine.models import ColPali, ColPaliProcessor

        self.settings = settings or Settings()
        self.qdrant_client = qdrant_client
        self.model = ColPali.from_pretrained(
            self.settings.colpali_model,
            torch_dtype=torch.bfloat16,
            device_map=self.settings.embed_device,
            low_cpu_mem_usage=True,
        )
        self.processor = ColPaliProcessor.from_pretrained(self.settings.colpali_model)
        self.model.eval()

        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-m3",
            cache_folder=str(Path(self.settings.hf_home) / "hub"),
        )

    def index_page_image(
        self,
        image: Image.Image,
        doc_id: str,
        page_num: int,
        image_path: str,
    ) -> None:
        inputs = self.processor.process_images([image])
        inputs = self._move_to_device(inputs)

        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = self._first_batch_item(outputs)
        patch_embeddings = embeddings.detach().cpu().float().tolist()

        self.qdrant_client.upsert(
            collection_name=self.settings.image_collection,
            points=[
                PointStruct(
                    id=abs(hash(f"{doc_id}_{page_num}")),
                    vector=patch_embeddings,
                    payload={
                        "doc_id": doc_id,
                        "page_num": page_num,
                        "image_path": image_path,
                    },
                )
            ],
        )

    def index_text_chunk(self, chunk: dict[str, Any], doc_id: str) -> None:
        embedding = self.embed_model.get_text_embedding(chunk["text"])

        self.qdrant_client.upsert(
            collection_name=self.settings.text_collection,
            points=[
                PointStruct(
                    id=abs(hash(chunk["chunk_id"])),
                    vector=list(embedding),
                    payload={
                        "doc_id": doc_id,
                        "page_num": chunk["page_num"],
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                    },
                )
            ],
        )

    def _move_to_device(self, inputs: Any) -> Any:
        device = self.settings.embed_device
        dtype = torch.bfloat16

        if hasattr(inputs, "to"):
            inputs = inputs.to(device)
            return {
                key: value.to(dtype) if value.dtype.is_floating_point else value
                for key, value in inputs.items()
            }

        if isinstance(inputs, dict):
            return {
                key: value.to(device).to(dtype)
                if hasattr(value, "to") and value.dtype.is_floating_point
                else value.to(device)
                if hasattr(value, "to")
                else value
                for key, value in inputs.items()
            }

        return inputs

    @staticmethod
    def _first_batch_item(outputs: Any) -> torch.Tensor:
        if hasattr(outputs, "last_hidden_state"):
            outputs = outputs.last_hidden_state
        elif isinstance(outputs, (list, tuple)):
            outputs = outputs[0]

        if not isinstance(outputs, torch.Tensor):
            outputs = torch.as_tensor(outputs)

        return outputs[0] if outputs.ndim == 3 else outputs


class MultimodalRetriever:
    def __init__(self, qdrant_client: Any, settings: Settings | None = None):
        from colpali_engine.models import ColPali, ColPaliProcessor

        self.settings = settings or Settings()
        self.qdrant_client = qdrant_client
        self.model = ColPali.from_pretrained(
            self.settings.colpali_model,
            torch_dtype=torch.bfloat16,
            device_map=self.settings.embed_device,
            low_cpu_mem_usage=True,
        )
        self.processor = ColPaliProcessor.from_pretrained(self.settings.colpali_model)
        self.model.eval()

        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-m3",
            cache_folder=str(Path(self.settings.hf_home) / "hub"),
        )

    def retrieve_images(
        self,
        query: str,
        top_k: int = 5,
        doc_id: str | None = None,
    ) -> list[dict]:
        inputs = self.processor.process_queries([query])
        inputs = self._move_to_device(inputs)

        with torch.no_grad():
            outputs = self.model(**inputs)

        query_embedding = self._first_batch_item(outputs).detach().cpu().float().tolist()
        query_filter = None
        if doc_id is not None:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id),
                    )
                ]
            )

        response = self.qdrant_client.query_points(
            collection_name=self.settings.image_collection,
            query=query_embedding,
            query_filter=query_filter,
            with_payload=True,
            limit=top_k,
        )

        points = getattr(response, "points", response)
        return [
            {
                "page_num": point.payload["page_num"],
                "image_path": point.payload["image_path"],
                "score": point.score,
                "doc_id": point.payload["doc_id"],
            }
            for point in points
        ]

    def retrieve_text(
        self,
        query: str,
        top_k: int = 5,
        doc_id: str | None = None,
    ) -> list[dict]:
        embedding = self.embed_model.get_text_embedding(query)
        query_filter = None
        if doc_id is not None:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id),
                    )
                ]
            )

        response = self.qdrant_client.query_points(
            collection_name=self.settings.text_collection,
            query=list(embedding),
            query_filter=query_filter,
            with_payload=True,
            limit=top_k,
        )

        points = getattr(response, "points", response)
        return [
            {
                "page_num": point.payload["page_num"],
                "chunk_id": point.payload["chunk_id"],
                "text": point.payload["text"],
                "score": point.score,
                "doc_id": point.payload["doc_id"],
            }
            for point in points
        ]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_id: str | None = None,
    ) -> RetrievalResult:
        image_results = self.retrieve_images(query, top_k, doc_id)
        text_results = self.retrieve_text(query, top_k, doc_id)
        top_image_pages = {result["page_num"] for result in image_results}

        for chunk in text_results:
            if chunk["page_num"] in top_image_pages:
                chunk["score"] += 0.1

        text_results.sort(key=lambda chunk: chunk["score"], reverse=True)
        return RetrievalResult(top_pages=image_results, top_chunks=text_results)

    def _move_to_device(self, inputs: Any) -> Any:
        device = self.settings.embed_device
        dtype = torch.bfloat16

        if hasattr(inputs, "to"):
            inputs = inputs.to(device)
            return {
                key: value.to(dtype) if value.dtype.is_floating_point else value
                for key, value in inputs.items()
            }

        if isinstance(inputs, dict):
            return {
                key: value.to(device).to(dtype)
                if hasattr(value, "to") and value.dtype.is_floating_point
                else value.to(device)
                if hasattr(value, "to")
                else value
                for key, value in inputs.items()
            }

        return inputs

    @staticmethod
    def _first_batch_item(outputs: Any) -> torch.Tensor:
        if hasattr(outputs, "last_hidden_state"):
            outputs = outputs.last_hidden_state
        elif isinstance(outputs, (list, tuple)):
            outputs = outputs[0]

        if not isinstance(outputs, torch.Tensor):
            outputs = torch.as_tensor(outputs)

        return outputs[0] if outputs.ndim == 3 else outputs


def ingest_and_index(
    file_bytes: bytes,
    doc_id: str,
    qdrant_client: Any,
    settings: Settings,
) -> dict[str, Any]:
    result = ingest_pdf(file_bytes, doc_id)
    indexer = MultimodalIndexer(qdrant_client=qdrant_client, settings=settings)

    for image_path in tqdm(result["page_image_paths"], desc="Indexing pages"):
        path = Path(image_path)
        page_num = int(path.stem.replace("page_", ""))
        with Image.open(path) as image:
            indexer.index_page_image(
                image=image,
                doc_id=doc_id,
                page_num=page_num,
                image_path=str(path),
            )

    for chunk in result["text_chunks"]:
        indexer.index_text_chunk(chunk=chunk, doc_id=doc_id)

    return result


def retrieve(query: str, top_k: int = 5) -> list[Source]:
    return []
