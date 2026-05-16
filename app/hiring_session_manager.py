class HiringSessionManager:
    def __init__(self):
        self.job_description: str | None = None
        self.candidates: list[str] = []
        self.scores: list[str] = []