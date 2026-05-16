import os
from dotenv import load_dotenv
from services.llm_client import LlmClient, LlmConfig
from services.embedding_service import EmbeddingService, EmbeddingConfig
from services.document_store import DocumentStore, PineconeConfig, ChunkConfig
from services.cv_security_parser import CVSecurityParser
from services.logger import Logger
from services.audit_logger import AuditLogger
from services.vector_memory_store import VectorMemoryService
from agents.cv_analyser_agent import CVAnalyserAgent


def appContainer(
        mode: str,
        logger_file_path:str,
        audit_logger_path:str,
):
    logger = Logger(logger_file_path)
    logger.info("Hiring application started" if mode == 'hiring' else 'Analyser application started')
    audit = AuditLogger(audit_logger_path)
    load_dotenv()

    llm_client = LlmClient(
        LlmConfig(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("GEMINI_MODEL_NAME"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE")),
        )
    )

    embedder = EmbeddingService(
        EmbeddingConfig(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=os.getenv("GEMINI_EMBEDDING_MODEL"),
        )
    )

    store = DocumentStore(
        logger,
        embedder,
        PineconeConfig(
            api_key=os.getenv("PINECONE_API_KEY"),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            namespace= "hiring_global" if mode == 'hiring' else os.getenv("PINECONE_NAMESPACE"),
        ),
        ChunkConfig(chunk_size=400, chunk_overlap=40),
        cleanup_on_exit=True,
    )

    memory =  VectorMemoryService(embedder)  if mode == 'Analyser' else None

    agent = CVAnalyserAgent(llm_client, store, logger) if mode == 'Analyser' else None
    security = CVSecurityParser()

    return {
        "logger": logger,
        "audit": audit,
        "llm": llm_client,
        "embedder": embedder,
        "store": store,
        "memory": memory,
        "agent": agent,
        "security": security,
    }