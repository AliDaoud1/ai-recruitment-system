class CommandHandler:
    def __init__(self, agent, memory, audit, session, logger):
        self.agent = agent
        self.memory = memory
        self.audit = audit
        self.session = session
        self.logger = logger

    def handle_ask(self, question: str):
        hits = self.memory.search(question, top_k=3)

        memory_context = "\n".join(
            f"{h.role}: {h.content}" for h in hits
        )

        answer, sources, cv_used = self.agent.chat(question, memory_context)

        self.memory.add("user", question)
        self.memory.add("assistant", answer)

        return answer, sources, cv_used

    def handle_summary(self):
        if not self.session.is_selected():
            return "Select candidate first", []

        return self.agent.summary(self.session.selected_file)

    def handle_skills(self):
        if not self.session.is_selected():
            return "Select candidate first", []

        return self.agent.skills(self.session.selected_file)

    def handle_improve(self, section: str):
        if not self.session.is_selected():
            return "Select candidate first", []

        answer, sources = self.agent.improve_section(self.session.selected_file, section)
        self.memory.add("user", f"improve {section}")
        self.memory.add("assistant", answer)
        return answer, sources