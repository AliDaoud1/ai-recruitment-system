from agents.hiring_agent import HiringAgent
from services.job_description_loader import JobDescriptionLoader
from services.namespace_manager import NamespaceManager
from app.hiring_session_manager import HiringSessionManager


class HiringSession:
    def __init__(self, llm_client, store, logger, audit):
        self.job_loader = JobDescriptionLoader()
        self.namespace_manager = NamespaceManager()
        self.session = HiringSessionManager()
        self.agent = HiringAgent(llm_client, store, logger, audit)