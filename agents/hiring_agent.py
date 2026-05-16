from langchain_core.messages import HumanMessage, SystemMessage
from services.cv_prompts import CVPrompts
from services.candidate_scores import CandidateScore


class HiringAgent:
    """
    Hiring Agent (LLM-based evaluation system)

    This agent is responsible for:
    - Scoring candidates against a job description
    - Comparing multiple candidates
    - Generating final hiring recommendations

    Architecture:
    - Uses RAG (vector DB) to fetch relevant CV chunks
    - Uses LLM for structured reasoning (Gemini/OpenAI)
    - Uses audit logger for traceability of all hiring decisions

    Output Style:
    - Structured JSON scoring
    - Ranked comparison table
    - Final recommendation summary
    """

    def __init__(self, llm, store, logger, audit):
        self._llm = llm
        self._store = store
        self._logger = logger
        self._audit = audit

    def _ask_llm(self, prompt: str, context: str) -> str:
        """
        Sends a structured prompt + CV context to the LLM.

        Used by all hiring operations:
        - scoring
        - comparison
        - recommendation
        """
        messages = [
            SystemMessage(content=CVPrompts.HIRING_SYSTEM),
            HumanMessage(content=f"{prompt}\n\n{context}")
        ]
        return self._llm.invoke(messages)

    def score_candidate(self, candidate_name: str, namespace: str, job_description: str):
        """
        Evaluates a single candidate against a job description.

        Flow:
        1. Retrieve top-K relevant CV chunks (RAG)
        2. Build unified context
        3. Send scoring prompt to LLM
        4. Return structured JSON result

        Audit:
        - logs candidate scoring event
        - stores sources + metadata
        """
        results = self._store.retrieve(query=job_description, top_k=5, namespace=namespace)
        context = "\n\n---\n\n".join(
            r.document.page_content for r in results
        )
        sources = [
            r.document.metadata.get("source", "?")
            for r in results
        ]
        response = self._ask_llm(
            CVPrompts.SCORE_CANDIDATE,
            f"Job Description:\n{job_description}\n\nCandidate CV:\n{context}"
        )
        self._logger.info(f"Scored {candidate_name}")
        self._audit.log(
            action="score_candidate",
            candidate=candidate_name,
            response=response,
            sources=sources,
            metadata={
                "namespace": namespace,
                "top_k": len(results)
            },
            app="hiring"
        )

        return response

    def compare_candidates(self, scored_candidates: list[dict]) -> str:
        """
        Ranks candidates based on pre-computed scores.

        Important:
        - Does NOT re-score candidates
        - Only formats + analyzes existing scores
        """
        combined = "\n\n".join(
            f"""
            Candidate: {c['name']}
            Technical: {c['technical']}
            Experience: {c['experience']}
            Nice-to-Have: {c['nice_to_have']}
            Total: {c['total']}
            Reason: {c.get('reason', '')}
            """.strip()
            for c in scored_candidates
        )

        self._logger.info("Compared all candidates")

        response = self._ask_llm(
            CVPrompts.COMPARE_CANDIDATES,
            combined
        )

        self._audit.log(
            action="compare_candidates",
            response=response,
            metadata={
                "candidates_count": len(scored_candidates)
            },
            app="hiring"
        )
        return response

    def recommend(self, comparison_output: str) -> str:
        """
        Generates final hiring decision based on comparison output.

        This is the final step of the hiring pipeline.
        """
        response = self._ask_llm(
            CVPrompts.RECOMMEND_CANDIDATE,
            comparison_output
        )

        self._logger.info("Generated final recommendation")

        self._audit.log(
            action="recommend_candidate",
            response=response,
            metadata={
                "source": "comparison_output"
            },
            app="hiring"
        )
        return response
