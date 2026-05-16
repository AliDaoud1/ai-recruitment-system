from dataclasses import dataclass


@dataclass
class CandidateScore:
    name: str
    technical: int
    experience: int
    nice_to_have: int

    @property
    def total(self) -> int:
        return self.technical + self.experience + self.nice_to_have