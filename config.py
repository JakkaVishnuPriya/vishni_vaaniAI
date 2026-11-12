from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    paper_dir: Path = Path("data/papers")

def get_settings() -> Settings:
    return Settings()
