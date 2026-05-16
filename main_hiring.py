import sys
from pathlib import Path
from services.file_helper import PDFLoader
from services.score_formatter import print_scores
from app.hiring_session import HiringSession
from app.hiring_command_handler import HiringCommandHandler
from app.app_container import appContainer
from app.file_loader import load_and_index

services = appContainer(
    mode='hiring',
    logger_file_path="logs/hiring_app.log",
    audit_logger_path="logs/hiring_audit.json"
)

logger = services["logger"]
audit = services["audit"]
store = services["store"]
security = services["security"]
llm_client = services["llm"]
pdf_reader = PDFLoader()

container = HiringSession(
    llm_client=llm_client,
    store=store,
    logger=logger,
    audit=audit
)

handler = HiringCommandHandler(
    container=container,
    store=store,
)

DATA_DIR = Path("data")
JOB_DIR = Path("job_description")
# ---------------- LOAD ALL CANDIDATES ----------------
load_and_index(store, logger, security, pdf_reader, mode='hiring', container=container)

logger.log_print(
    f"Loaded {len(container.namespace_manager.all())} candidates"
)

# ---------------- COMMAND HELP ----------------
print("\n📌 HIRING AGENT READY\n")

print("🔹 Job Description:")
print("  load_jd <file>       → load job description file\n")

print("🔹 Candidate Evaluation:")
print("  score_all            → score all candidates")
print("  compare_all          → compare all candidates")
print("  recommend            → recommend top candidate\n")

print("🔹 System:")
print("  list                 → list all candidate namespaces")
print("  exit                 → cleanup + quit\n")


# ---------------- STATE ----------------
last_comparison = None

# ---------------- MAIN LOOP ----------------
with store:
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            user_input = "exit"

        if not user_input:
            continue

        logger.user_query(user_input)

        # ---------------- EXIT ----------------
        if user_input.lower() in ("exit", "quit"):
            print("Cleaning up candidate namespaces...")

            for namespace in container.namespace_manager.all():
                store.clear_namespace(namespace)
                audit.system(
                    event="namespace_deleted",
                    data={"namespace": namespace},
                    app="hiring"
                )

            audit.system(
                event="app_exit",
                app="hiring"
            )
            audit.flush()
            print("Bye")
            sys.exit(0)

        # ---------------- LIST ----------------
        if user_input.lower() == "list":
            print("\nCandidates:")
            for ns in container.namespace_manager.all():
                print("-", ns)
            continue

        # ---------------- LOAD JOB DESCRIPTION ----------------
        if user_input.lower().startswith("load_jd "):
            jd_file = user_input[8:].strip()
            jd_path = JOB_DIR / jd_file

            if not jd_path.exists():
                print("Job description file not found.")
                continue

            handler.load_jd(str(jd_path))

            audit.system(
                event="job_description_loaded",
                data={"file": jd_file},
                app="hiring"
            )
            print(f"Loaded job description: {jd_file}")
            continue

        # ---------------- SCORE ALL ----------------
        if user_input.lower() == "score_all":
            if not container.session.job_description:
                print("Load job description first.")
                continue

            print("\nScoring candidates...\n")

            scores = handler.score_all()

            print_scores(scores)
            audit.system(
                event="score_all",
                data={"candidates_count": len(scores)},
                app="hiring"
            )

            continue

        # ---------------- COMPARE ALL ----------------
        if user_input.lower() == "compare_all":
            if not container.session.scores:
                print("Run score_all first.")
                continue

            comparison = handler.compare_all()

            last_comparison = comparison

            print("\nCandidate Comparison:\n")
            print(comparison)

            audit.system(
                event="compare_all",
                app="hiring"
            )
            continue

        # ---------------- RECOMMEND ----------------
        if user_input.lower() == "recommend":
            if not last_comparison:
                print("Run compare_all first.")
                continue

            recommendation = handler.recommend(last_comparison)

            print("\nFinal Recommendation:\n")
            print(recommendation)

            audit.system(
                event="recommend",
                app="hiring"
            )
            continue

        # ---------------- UNKNOWN ----------------
        print("Unknown command.")

