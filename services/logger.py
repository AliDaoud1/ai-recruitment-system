from pathlib import Path
from datetime import datetime


class Logger:
    def __init__(self, path: str = "logs/app.log") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        # CREATE FRESH FILE ON START (overwrite)
        self._path.write_text("", encoding="utf-8")

    def _write(self, level: str, message: str) -> None:
        timestamp = datetime.now().isoformat()

        line = f"[{timestamp}] [{level}] {message}\n"

        with self._path.open("a", encoding="utf-8") as f:
            f.write(line)

    # ---------------- system events ----------------
    def info(self, message: str) -> None:
        self._write("INFO", message)

    def warning(self, message: str) -> None:
        self._write("WARNING", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)

    def log_print(self, message: str) -> None:
        print(message)
        self.info(message)

    # ---------------- domain helpers ----------------
    def file_loaded(self, filename: str, chunks: int) -> None:
        self.info(f"Loaded file: {filename} | chunks={chunks}")

    def indexing_done(self, total_chunks: int) -> None:
        self.info(f"Indexing completed | total_chunks={total_chunks}")

    def user_query(self, query: str) -> None:
        self.info(f"User query: {query}")

    def retrieval(self, count: int) -> None:
        self.info(f"Retrieved documents: {count}")
