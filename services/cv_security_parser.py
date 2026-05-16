import re
from dataclasses import dataclass

@dataclass
class PiiReport:
    emails: list[str]
    phones: list[str]
    links: list[str]


class CVSecurityParser:
    EMAIL_REGEX = r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"
    PHONE_REGEX = r"\+?\d[\d\s().-]{7,}\d"
    LINKEDIN_REGEX = r"linkedin\.com/in/[^\s]+"
    GITHUB_REGEX = r"github\.com/[^\s]+"

    def detect(self, text: str) -> PiiReport:
        return PiiReport(
            emails=re.findall(self.EMAIL_REGEX, text),
            phones=re.findall(self.PHONE_REGEX, text),
            links=re.findall(self.LINKEDIN_REGEX + "|" + self.GITHUB_REGEX, text),
        )

    def sanitize(self, text: str) -> str:
        text = re.sub(self.EMAIL_REGEX, "[EMAIL]", text)
        text = re.sub(self.PHONE_REGEX, "[PHONE]", text)
        text = re.sub(self.LINKEDIN_REGEX, "[LINKEDIN]", text)
        text = re.sub(self.GITHUB_REGEX, "[GITHUB]", text)
        return text