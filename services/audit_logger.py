from pathlib import Path
from datetime import datetime
import json


class AuditLogger:
    def __init__(self, path: str = "logs/audit_log.json") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        self._records: list[dict] = []

        # initialize valid empty JSON array
        self._path.write_text("[]", encoding="utf-8")

    # -------------------------
    # GENERIC ACTION LOGGER
    # -------------------------
    def log(
        self,
        action: str,
        user_input: str | None = None,
        response: str | None = None,
        candidate: str | None = None,
        sources: list[str] | None = None,
        metadata: dict | None = None,
        app: str = "unknown"   # 👈 key for analyser vs hiring
    ) -> None:

        self._records.append({
            "timestamp": datetime.now().isoformat(),
            "app": app,              # analyser | hiring
            "action": action,
            "candidate": candidate,
            "user": user_input,
            "response": response,
            "sources": sources or [],
            "meta": metadata or {}
        })

    # -------------------------
    # SYSTEM EVENTS
    # -------------------------
    def system(self, event: str, data: dict | None = None, app: str = "unknown") -> None:
        self._records.append({
            "timestamp": datetime.now().isoformat(),
            "app": app,
            "type": "system",
            "event": event,
            "data": data or {}
        })

    # -------------------------
    # SAVE FILE
    # -------------------------
    def flush(self) -> None:
        self._path.write_text(
            json.dumps(self._records, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def reset(self) -> None:
        self._records = []
        self._path.write_text("[]", encoding="utf-8")