from logging import Logger
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from base.agent_base import AgentBase
from services.document_store import DocumentStore
from services.llm_client import LlmClient
from services.cv_prompts import CVPrompts


class CVAnalyserAgent(AgentBase):
    def __init__(self, client: LlmClient, store: DocumentStore, logger: Logger):
        self._llm = client
        self._store = store
        self._logger = logger

        # MMR toggle
        self._use_mmr = False

    def toggle_mmr(self) -> None:
        self._use_mmr = not self._use_mmr
        self._logger.info(f"MMR toggled -> {self._use_mmr}")


    # ---------------- core helpers ----------------
    def _retrieve(self, query: str, top_k: int, source: str | None = None):
        self._logger.info(
            f"[cv_analyser_agent] retrieve query='{query}' mmr={self._use_mmr}"
        )
        ## JUST FOR TEST
        query = f"{query} {source}" if source else query
        if self._use_mmr:
            results = self._store.retrieve_mmr(query, top_k)
        else:
            results = self._store.retrieve(query, top_k)
        if source:
            results = [
                r for r in results
                if source.lower() in r.document.metadata.get("source", "").lower()
            ]
        self._logger.info(f"[cv_analyser_agent] retrieved={len(results)}")
        return results

    def _build_context(self, results) -> str:
        return "\n\n".join(
            f"[{r.document.metadata.get('source', '?')}]\n{r.document.page_content}"
            for r in results
        )

    def _ask_llm(self, prompt: str, context: str):
        messages = [
            SystemMessage(content=CVPrompts.SYSTEM),
            HumanMessage(content=f"{prompt}\n\n{context}")
        ]
        return self._llm.invoke(messages)

    def chat(self, question: str, memory_context: str = ""):
        results = self._retrieve(question, top_k=4)
        context = self._build_context(results)
        full_context = f"""
        === Memory Context ===
        {memory_context}

        === CV Context ===
        {context}
        """

        answer = self._ask_llm(
            f"Question: {question}",
            f"Context:\n{full_context}"
        )
        return answer, results, True if '.pdf' in answer else False

    def summary(self, file_name: str):
        self._logger.info(f"[summary] file={file_name}")
        results = self._retrieve(
            "summary",
            top_k=10,
            source=file_name
        )
        context = self._build_context(results)
        answer = self._ask_llm(CVPrompts.SUMMARY, context)
        return answer, results

    def skills(self, file_name: str):
        self._logger.info(f"[skills] file={file_name}")
        # retrieve directly from file source
        results = self._retrieve(
            "skills technologies tools",
            top_k=10,
            source=file_name
        )
        context = self._build_context(results)
        answer = self._ask_llm(CVPrompts.SKILLS, context)
        return answer, results

    def improve_section(self, file_name: str, section: str):
        self._logger.info(f"[improve] file={file_name} section={section}")
        results = self._retrieve(
            f"{section}",
            top_k=10,
            source=file_name
        )
        context = self._build_context(results)
        answer = self._ask_llm(
            CVPrompts.IMPROVE + f"\n\nSECTION: {section}",
            context
        )
        return answer, results

    def reset(self) -> None:
        self._logger.info("[cv_analyser_agent] Reset called")
