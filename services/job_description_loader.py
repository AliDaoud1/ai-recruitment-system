from pathlib import Path
class JobDescriptionLoader:
    def load(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")