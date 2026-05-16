import sys
from pathlib import Path
from app.app_container import appContainer
from app.file_loader import load_and_index
from app.command_handler import CommandHandler
from app.session_manager import SessionManager
from services.file_helper import PDFLoader, resolve_candidate_file, normalize

DATA_DIR = Path("data")

# ---------------- INIT ----------------
services = appContainer(
    mode='Analyser',
    logger_file_path="logs/analyser_app.log",
    audit_logger_path="logs/analyser_audit.json"
)

logger = services["logger"]
audit = services["audit"]
store = services["store"]
memory = services["memory"]
agent = services["agent"]
security = services["security"]
pdf_reader = PDFLoader()

# ---------------- LOAD DATA ----------------
docs = load_and_index(store, logger, security, pdf_reader, mode='analyzer')

# ---------------- COMMAND HELP ----------------
print(f"Indexed {len(docs)} chunks\n")
logger.info(f"Indexing completed | total_chunks={len(docs)}")
logger.log_print("=== CV ANALYSER AGENT READY ===")
print("\n📌 AVAILABLE COMMANDS:\n")

print("🔹 Candidate Selection:")
print("  select <name>        → choose a CV (e.g. select lina saeed)")
print("  change              → clear selected CV")
print("  list                → show all CV candidates\n")

print("🔹 Analysis Commands (require selected CV):")
print("  summary             → full CV summary")
print("  skills             → extract technical + soft skills")
print("  improve <section>  → improve CV section\n")

print("🔹 Search:")
print("  ask <question>     → ask anything about CVs\n")

print("🔹 System:")
print("  mmr               → toggle diversity search")
print("  exit              → quit system\n")

# ---------------- SESSION ----------------
session = SessionManager()

# ---------------- COMMAND HANDLER ----------------
handler = CommandHandler(agent, memory, audit, session, logger)

# ---------------- LOOP ----------------
with store:
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("Bye")
            memory.clear()
            sys.exit(0)
        logger.user_query(user_input)
        if not user_input:
            continue

        # ---------------- EXIT ----------------
        if user_input.lower() in ("exit", "quit"):
            print("Bye")
            memory.clear()
            audit.system(
                event="app_exit",
                app="analyser"
            )
            audit.flush()
            sys.exit(0)

        # ---------------- MMR ----------------
        if user_input.lower() == "mmr":
            agent.toggle_mmr()
            print(f"[MMR: {'ON' if agent._use_mmr else 'OFF'}]")
            continue

        # ---------------- ASK ----------------
        if user_input.lower().startswith("ask "):
            answer, sources, cv_used = handler.handle_ask(user_input[4:])

            print(f"\nAgent: {answer}")

            audit.log(
                action="ask",
                user_input=user_input[4:],
                response=answer,
                candidate=session.selected_file,
                sources=[
                    r.document.metadata.get("source", "?")
                    for r in sources
                ] if sources else [],
                metadata={
                    "cv_used": cv_used
                },
                app="analyser"
            )

            if sources and cv_used:
                seen: set[str] = set()
                for r in sources:
                    src = r.document.metadata.get("source", "?")
                    if src not in seen:
                        score_str = f"source:{r.score:.2f}" if r.score < 1.0 else "MMR"
                        print(f"   > Score: {src}   ({score_str})")
                        seen.add(src)
            continue

        # ---------------- SELECT ----------------
        if user_input.lower().startswith("select "):
            candidate = user_input[7:].strip()
            selected = resolve_candidate_file(candidate, DATA_DIR)
            if selected:
                session.select(selected)
                audit.system(
                    event="candidate_selected",
                    data={"candidate": selected},
                    app="analyser"
                )
                print(f"Selected: {selected}")
            else:
                print("No matching CV found")
            continue

        # ---------------- LIST ----------------
        if user_input.lower() == "list":
            print("\nCandidates:")
            for p in DATA_DIR.glob("*"):
                if p.is_file():
                    print("-", normalize(p.stem))
            continue

        # ---------------- CHANGE ----------------
        if user_input.lower() == "change":  # change to clear
            old_candidate = session.selected_file
            session.clear()
            audit.system(
                event="candidate_cleared",
                data={"previous_candidate": old_candidate},
                app="analyser"
            )
            print("Selection cleared")
            continue

        # ---------------- SUMMARY ----------------
        if user_input.lower() == 'summary':
            result, _ = handler.handle_summary()
            audit.log(
                action="summary",
                user_input="summary",
                response=result,
                candidate=session.selected_file,
                app="analyser"
            )
            print(result)
            continue

        # ---------------- SKILLS ----------------
        if user_input.lower() == "skills":
            result, _ = handler.handle_skills()
            audit.log(
                action="skills",
                user_input="skills",
                response=result,
                candidate=session.selected_file,
                app="analyser"
            )
            print(result)
            continue

        # ---------------- IMPROVE ----------------
        if user_input.lower().startswith('improve '):
            section = user_input[8:].strip()
            result, _ = handler.handle_improve(section)
            audit.log(
                action="improve",
                user_input=user_input,
                response=result,
                candidate=session.selected_file,
                metadata={
                    "section": section
                },
                app="analyser"
            )
            print(result)
            continue

        logger.log_print("Unknown command")
