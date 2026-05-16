import json


class HiringCommandHandler:
    def __init__(self, container, store):
        self.container = container
        self.store = store

    def load_jd(self, path: str):
        self.container.session.job_description = self.container.job_loader.load(path)

    def score_all(self):
        jd = self.container.session.job_description
        outputs = []

        for candidate in self.container.namespace_manager.all():
            raw = self.container.agent.score_candidate(
                candidate_name=candidate,
                namespace=candidate,
                job_description=jd,
            )
            if isinstance(raw, str):
                raw = raw.strip()

                if not raw:
                    raise ValueError("Empty response from agent.score_candidate")

                try:
                    raw = json.loads(raw)
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON from LLM:\n{raw}")

            outputs.append(raw)

        self.container.session.scores = outputs
        return outputs

    def compare_all(self):
        return self.container.agent.compare_candidates(
            self.container.session.scores
        )

    def recommend(self, comparison: str):
        return self.container.agent.recommend(comparison)
