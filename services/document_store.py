from dataclasses import dataclass, field
from pathlib import Path
from logging import Logger

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from base.retriever_base import RetrieverBase, RetrievalResult

from services.embedding_service import EmbeddingService

# Dimension of Google gemini-embedding-001 output vectors.
_EMBEDDING_DIMENSION = 3072


@dataclass
class ChunkConfig:
    chunk_size: int = 500
    chunk_overlap: int = 50  #
    separators: list[str] = field(
        default_factory=lambda: ["\n\n", "\n", ". ", " ", ""]
    )


@dataclass
class PineconeConfig:
    api_key: str
    index_name: str
    namespace: str = "tutorial_05"
    cloud: str = "aws"
    region: str = "us-east-1"


class DocumentStore(RetrieverBase):
    def __init__(
            self,
            logger: Logger,
            embedding_service: EmbeddingService,
            pinecone_config: PineconeConfig,
            chunk_config: ChunkConfig = ChunkConfig(),
            cleanup_on_exit: bool = False,

    ) -> None:
        if not pinecone_config.api_key:
            raise ValueError("PineconeConfig.api_key is required and cannot be empty.")
        if not pinecone_config.index_name:
            raise ValueError("PineconeConfig.index_name is required and cannot be empty.")
        if not pinecone_config.namespace:
            raise ValueError("PineconeConfig.namespace is required and cannot be empty.")

        self._logger = logger
        self._embedder = embedding_service
        self._pc_cfg = pinecone_config
        self._cleanup_on_exit = cleanup_on_exit
        self._active_namespaces: set[str] = set()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_config.chunk_size,
            chunk_overlap=chunk_config.chunk_overlap,
            separators=chunk_config.separators,
        )
        self._store: PineconeVectorStore | None = None
        # Connect to Pinecone and create the index if it doesn't exist yet.
        pc = Pinecone(api_key=pinecone_config.api_key)
        existing = [idx.name for idx in pc.list_indexes()]
        if pinecone_config.index_name not in existing:
            pc.create_index(
                name=pinecone_config.index_name,
                dimension=_EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=pinecone_config.cloud,
                    region=pinecone_config.region,
                ),
            )
        self._pc_index = pc.Index(pinecone_config.index_name)

    def load_file(self, path: str, metadata: dict | None = None) -> list[Document]:
        text = Path(path).read_text(encoding="utf-8")
        return self._chunk_text(text, Path(path).name)

    def load_text(self, text: str, source: str = "unknown", metadata: dict | None = None) -> list[Document]:
        return self._chunk_text(text, source)

    def _chunk_text(self, text: str, source: str) -> list[Document]:
        base_meta = {"source": source}
        chunks = self._splitter.create_documents([text], metadatas=[base_meta])

        self._logger.info(f"Text chunked: {source} | chunks={len(chunks)}")

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i

        return chunks


    def index(self, documents: list[Document], namespace: str | None = None) -> None:

        target_namespace = namespace or self._pc_cfg.namespace
        PineconeVectorStore.from_documents(
            documents=documents,
            embedding=self._embedder.get_model(),
            index_name=self._pc_cfg.index_name,
            pinecone_api_key=self._pc_cfg.api_key,
            namespace=target_namespace,
        )

        self._active_namespaces.add(target_namespace)
        self._store = PineconeVectorStore(
            index=self._pc_index,
            embedding=self._embedder.get_model(),
            namespace=target_namespace,
        )

        self._logger.info(
            f"Indexed {len(documents)} docs into namespace='{target_namespace}'"
        )

    def retrieve(self, query: str, top_k: int = 4, namespace: str | None = None) -> list[RetrievalResult]:
        target_namespace = namespace or self._pc_cfg.namespace

        store = PineconeVectorStore(
            index=self._pc_index,
            embedding=self._embedder.get_model(),
            namespace=target_namespace,
        )

        raw = store.similarity_search_with_score(query, k=top_k)
        self._logger.retrieval(len(raw))
        self._logger.info(
            f"Retrieving query='{query}' namespace='{target_namespace}' results={len(raw)}"
        )
        return [RetrievalResult(document=doc, score=score) for doc, score in raw]

    def retrieve_mmr(self, query: str, top_k: int = 4, namespace: str | None = None) -> list[RetrievalResult]:
        target_namespace = namespace or self._pc_cfg.namespace

        store = PineconeVectorStore(
            index=self._pc_index,
            embedding=self._embedder.get_model(),
            namespace=target_namespace,
        )

        docs = store.max_marginal_relevance_search(
            query, k=top_k, fetch_k=top_k * 4
        )
        self._logger.retrieval(len(docs))
        self._logger.info(
            f"MMR query='{query}' namespace='{target_namespace}' results={len(docs)}"
        )
        return [RetrievalResult(document=doc, score=1.0) for doc in docs]


    def clear_namespace(self, namespace: str) -> None:
        self._pc_index.delete(
            delete_all=True,
            namespace=namespace,
        )

        if namespace in self._active_namespaces:
            self._active_namespaces.remove(namespace)

        self._logger.info(f"Namespace cleared: {namespace}")

    def clear(self) -> None:
        for namespace in list(self._active_namespaces):
            self.clear_namespace(namespace)

        self._store = None
        self._logger.info("All namespaces cleared")


    def __enter__(self) -> "DocumentStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._cleanup_on_exit:
            self.clear()
            print("clean up done")
